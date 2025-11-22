import ast
import datetime
from pathlib import Path
from typing import Dict, Any, List

# Importamos la interfaz y las implementaciones concretas
from .base import MetricStrategy
from .lines import LinesStrategy, TodoStrategy
from .imports import NumImportsStrategy
from .functions import FunctionsStrategy
from .duplication import DuplicationStrategy
from .maintainability import MaintainabilityStrategy
from config import ConfigSingleton

class MetricsFacade:
    """
    Fachada que orquesta el análisis de un repositorio completo.
    Oculta la complejidad de instanciar y llamar a múltiples estrategias.
    Patrón: Facade
    """

    def __init__(self):
        # Inicializamos todas las estrategias disponibles
        self.strategies: Dict[str, MetricStrategy] = {
            "lines": LinesStrategy(),
            "todos": TodoStrategy(),
            "imports": NumImportsStrategy(),
            "functions": FunctionsStrategy(),
            "duplication": DuplicationStrategy(),
            "maintainability": MaintainabilityStrategy()
        }
        self.config = ConfigSingleton.get_instance()

    def compute_all(self, repo_path: Path, options: dict = None) -> Dict[str, Any]:
        """
        Recorre el repositorio, aplica todas las métricas a cada fichero .py
        y genera un informe agregado.

        Args:
            repo_path (Path): Ruta local al directorio del repositorio clonado.
            options (dict): Opciones de configuración.

        Returns:
            Dict: Informe completo con resumen y detalle por archivo.
        """
        if options is None:
            options = {}

        print(f"\n--- 🕵️ DEBUG FACHADA ---")
        print(f"Analizando ruta absoluta: {repo_path.absolute()}")
        print(f"¿La carpeta existe?: {repo_path.exists()}")
        if repo_path.exists():
            print(f"¿Es un directorio?: {repo_path.is_dir()}")
            # Listamos qué hay dentro de la raíz (los primeros 5 elementos)
            contenido = list(repo_path.iterdir())
            print(f"Contenido raíz ({len(contenido)} items): {[p.name for p in contenido[:5]]}")
            
            # Probamos la búsqueda de python
            archivos_py = list(repo_path.rglob("*.py"))
            print(f"Archivos .py detectados por rglob: {len(archivos_py)}")
        print("------------------------\n")
        
        # Preparar contenedores de resultados
        file_metrics_list = []
        total_lines = 0
        total_files = 0
        sum_maintainability = 0.0

        # Buscar recursivamente todos los archivos .py
        # sorted() asegura que el orden sea determinista (útil para tests y UI)
        py_files = sorted(repo_path.rglob("*.py"))

        for file_path in py_files:
            # Ignoramos carpetas ocultas o venv si se colaron
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            total_files += 1

            # 1. Lectura y Parsing (Optimización: una sola vez) 
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                # Parseamos AST una vez para pasárselo a quien lo necesite
                ast_tree = ast.parse(content)
            except (SyntaxError, Exception):
                # Si falla (archivo binario o sintaxis inválida), usamos valores vacíos
                content = ""
                ast_tree = None
            
            # 2. Cálculo de Métricas por Archivo
            metrics = {
                "path": str(file_path.relative_to(repo_path)),
                "name": file_path.name
            }

            # Estrategias basadas en TEXTO
            metrics["loc"] = self.strategies["lines"].compute(content)
            metrics["todos"] = self.strategies["todos"].compute(content)
            metrics["num_imports"] = self.strategies["imports"].compute(content)

            # Estrategias basadas en AST
            if ast_tree:
                metrics["functions"] = self.strategies["functions"].compute(ast_tree)
            else:
                metrics["functions"] = {}
            
            # Estrategias basadas en FILESYSTEM / PATH
            # Duplication necesita 'window' de las opciones o del config
            dup_window = options.get("dup_window", self.config.duplication_window)
            metrics["duplication"] = self.strategies["duplication"].compute(file_path, window=dup_window)

            metrics["maintainability"] = self.strategies["maintainability"].compute(file_path)

            # 3. Acumulación para Resumen Global
            total_lines += metrics["loc"]
            sum_maintainability += metrics["maintainability"]

            file_metrics_list.append(metrics)

        # 4. Construcción del Resultado Final

        # Promedio de mantenibilidad
        avg_maintainability = 0.0
        if total_files > 0:
            avg_maintainability = sum_maintainability / total_files

        result = {
            # Metadatos generales
            "analyzed_at": datetime.datetime.now().isoformat(),
            "repo_name": repo_path.name,

            # Resumen ejecutivo (Summary)
            "summary": {
                "num_files": total_files,
                "total_lines": total_lines,
                "avg_maintainability": round(avg_maintainability, 2),
            },

            # Detalle granular
            "files": file_metrics_list
        }

        return result