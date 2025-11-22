from typing import List, Dict, Any

from .subject_interface import SubjectInterface
from repo.repo_manager import RepoManager
from repo.db_manager import DBManager
from metrics.facade import MetricsFacade

class ProxySubject(SubjectInterface):
    """
    Proxy que gestiona el acceso al análisis de repositorios.

    Responsabilidades:
    1. Caching: Comprobar si el análisis ya existe en BD antes de calcular.
    2. Lazy Loading: Solo descarga el repo si es estrictamente necesario.
    3. Gestión de 'Force': Permite invalidar la caché y recalcular
    """

    def __init__(self):
        # Inicializamos los subsistemas
        self.repo_manager = RepoManager()
        self.db_manager = DBManager()
        self.facade = MetricsFacade()
    
    def peticion(self, repo_url: str, force: bool = False) -> Dict[str, Any]:
        """
        Método principal del Proxy. Decide si usar caché o calcular de cero.
        """
        # 1. Si NO forzamos, intentamos buscar en la Base de Datos (Cache)
        if not force:
            cached_result = self.de_manager.get_latest_analysis(repo_url)
            if cached_result:
                print(f"[Proxy] Acierto de cache para: {repo_url}")
                # Marcamos que viene de cache
                cached_result["_from_cache"] = True
                cached_result["forced"] = False
                return cached_result
        
        print(f"[Proxy] Fallo de caché o forzado. Calculando: {repo_url}")

        # 2. Gestión del Repositorio Físico
        # Primero obtenemos la ruta donde DEBERÍA estar
        repo_path = self.repo_manager.ensure_repo(repo_url)

        # 3. Delegamos el cálculo pesado a la Fachada
        # Pasamos repo_path y opciones si las hubiera
        # Nota: Aquí podríamos pasar 'dup_window' desde opciones si la UI lo enviara
        result = self.facade.compute_all(repo_path, options={"force": force})

        # 4. Enriquecemos el resultado
        # La fachada trabaja con archivos locales, no sabe la URL remota. Se la ponemos nosotros.
        result["repo"] = repo_url
        result["forced"] = force
        result["_from_cache"] = False

        # 5. Guardamos en DB para el futuro (Write-through caching)
        self.db_manager.save_analysis(result)

        return result
    
    def list_analyses(self) -> List[Dict[str, Any]]:
        """
        Devuelve el historial directamente desde la BD
        """
        return self.db_manager.list_analyses()