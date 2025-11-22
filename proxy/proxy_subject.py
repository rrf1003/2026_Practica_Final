from typing import List, Dict, Any

from .subject_interface import SubjectInterface
from repo.repo_manager import RepoManager
from repo.db_manager import DBManager
from metrics.facade import MetricsFacade

class ProxySubject(SubjectInterface):
    """
    Proxy que gestiona el acceso al análisis de repositorios.
    """

    def __init__(self):
        # Inicializamos los subsistemas
        self.repo_manager = RepoManager()
        
        # --- AQUÍ ES DONDE PROBABLEMENTE ESTABA EL ERROR ---
        # Asegúrate de que pone 'db_manager' con 'b' de Barcelona (DataBase)
        self.db_manager = DBManager()  
        
        self.facade = MetricsFacade()

    def peticion(self, repo_url: str, force: bool = False) -> Dict[str, Any]:
        # 1. Si NO forzamos, intentamos buscar en la Base de Datos (Cache)
        if not force:
            # Revisa también aquí: self.db_manager
            cached_result = self.db_manager.get_latest_analysis(repo_url)
            if cached_result:
                print(f"[Proxy] Acierto de caché (Hit) para: {repo_url}")
                cached_result["_from_cache"] = True
                cached_result["forced"] = False
                return cached_result

        print(f"[Proxy] Fallo de caché (Miss) o forzado. Calculando: {repo_url}")

        # 2. Gestión del Repositorio Físico
        repo_path = self.repo_manager.ensure_repo(repo_url)

        if force:
            self.repo_manager.remove_repo(repo_path)
            repo_path = self.repo_manager.ensure_repo(repo_url)

        # 3. Delegamos cálculo a la Fachada
        result = self.facade.compute_all(repo_path, options={"force": force})

        # 4. Enriquecemos resultado
        result["repo"] = repo_url
        result["forced"] = force
        result["_from_cache"] = False

        # 5. Guardamos en BD
        # Revisa aquí también: self.db_manager
        self.db_manager.save_analysis(result)

        return result

    def list_analyses(self) -> List[Dict[str, Any]]:
        # Y aquí: self.db_manager
        return self.db_manager.list_analyses()