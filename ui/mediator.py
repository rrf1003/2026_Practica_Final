from typing import Dict, Any, Tuple, Optional
from flask import render_template

from proxy.subject_interface import SubjectInterface
from config import ConfigSingleton

class InputComponent:
    """
    Responsabilidad: Validar y extraer la URL del repositorio
    """
    def parse(self, form: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Analiza el formulario. Devuelve (repo_url, error).
        """
        repo_url = form.get("repo_url", "").strip()
        if not repo_url:
            return None, "⚠️ Debes introducir una URL de repositorio válida"
        
        # Validaciónbásica de formato (opcional)
        if not (repo_url.startswith("http") or repo_url.startwith("git@")):
            return None, "⚠️ La URL debe empezar por http://, https:// o git@"
        
        return repo_url, None
    
    def context(self, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Devuelve variables para la plantilla (mensajes de error).
        """
        return {"input_error": error}

class OptionsComponent:
    """
    Responsabilidad: Gestionar opciones de configuración (Force, Window).
    """
    def parse(self, form: Dict) -> Dict[str, Any]:
        """
        Extrae las opciones del formulario.
        """
        # Checkbox en HTML: si está marcado envía "on", si no, no evía nada.
        force = form.get("force") == "on"

        # Ventana de duplicación
        default_window = ConfigSingleton.get_instance().duplication_window
        try:
            dup_window = int(form.get("dup_window", str(default_window)))
        except ValueError:
            dup_window = default_window
        
        return {"force": force, "dup_window": dup_window}
    
    def context(self, current_options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Devuelve estado actual para repoblar el formulario
        """
        if not current_options:
            default_window = ConfigSingleton.get_instance().duplication_window
            return {"options": {"force": False, "dup_window": default_window}}
        return {"options": current_options}

class OutputComponent:
    """
    Responsabilida: Preparar el resultado del análisis para la vista
    """
    def prepare(self, result: Optional[Dict]) -> Dict[str, Any]:
        """
        Transforma el JSON crudo del backend en variables para Jinja2.
        """
        if not result:
            return {"shoe_output": False}
        
        return {
            "show_output": True,
            "result": result,  # Pasamos todo el objeto para iterar en HTML
            # Helpers para cabecera rápida
            "repo_name": result.get("repo_name", "Desconocido"),
            "analyzed_at": result.get("analyzed_at", ""),
            "from_cache": result.get("_from_cache", False),
            "forced": result.get("forced", False),
            "summary": result.get("summary", {})
        }

class HistoryComponent:
    """
    Responsabilidad: Obtener y formatear el historial de análisis.
    """
    def get_entries(self, subject: SubjectInterface) -> Dict[str, Any]:
        """Solicita al Subject la lista de análisis previos."""
        try:
            entries = subject.list_analyses()
        except Exception as e:
            print(f"[UI] Error recuperando historial: {e}")
            entries = []
        return {"history": entries}
    
class UIMediator:
    """
    Mediador que coordina los componentes UI y el Subject (Proxy).
    Desacopla la vista (Flask) de la lógica de negocio.
    """

    def __init__(self, subject: SubjectInterface):
        self.subject = subject
        # Instanciamos los componentes (colaboradores)
        self.input_c = InputComponent()
        self.options_c = OptionsComponent()
        self.output_c = OutputComponent()
        self.history_c = HistoryComponent()

    def show_index(self):
        """
        Maneja la petición GET / (Página de inicio).
        Muestra formulario vacío e historial.
        """
        ctx = {}
        # 1. Estado inicial del input (sin error)
        ctx.update(self.input_c.context())
        # 2. Opciones por defecto
        ctx.update(self.options_c.context())
        # 3. Sin resultados todavía
        ctx.update(self.output_c.prepare(None))
        # 4. Cargar historial
        ctx.update(self.history_c.get_entries(self.subject))

        return render_template("index.html", **ctx)

    def handle_analyze(self, form: Dict):
        """
        Maneja la petición POST /analyze.
        Coordina validación, llamada al backend y respuesta.
        """
        # 1. Parsear Input
        repo_url, error = self.input_c.parse(form)
        
        # Si hay error, detenemos proceso y volvemos a mostrar index con error
        if error:
            ctx = {}
            ctx.update(self.input_c.context(error)) # Pasamos el error
            ctx.update(self.options_c.context())    # Opciones por defecto
            ctx.update(self.output_c.prepare(None)) # Sin resultado
            ctx.update(self.history_c.get_entries(self.subject)) # Historial
            return render_template("index.html", **ctx)

        # 2. Parsear Opciones
        opts = self.options_c.parse(form)

        # 3. Llamada al Backend (A través del Proxy)
        # El proxy se encarga de Cache vs Real
        try:
            # Nota: metrics/facade.py compute_all usa 'dup_window' si se le pasa en options
            result = self.subject.peticion(repo_url, force=opts["force"])
        except Exception as e:
            # Si falla el backend (ej: repo no existe, fallo git), lo tratamos como error de input
            ctx = {}
            ctx.update(self.input_c.context(f"Error en el análisis: {str(e)}"))
            ctx.update(self.options_c.context(opts))
            ctx.update(self.output_c.prepare(None))
            ctx.update(self.history_c.get_entries(self.subject))
            return render_template("index.html", **ctx)

        # 4. Preparar contexto de éxito
        ctx = {}
        ctx.update(self.input_c.context()) # Limpiar error
        ctx.update(self.options_c.context(opts)) # Mantener opciones seleccionadas
        ctx.update(self.output_c.prepare(result)) # Mostrar métricas
        ctx.update(self.history_c.get_entries(self.subject)) # Historial actualizado

        return render_template("index.html", **ctx)