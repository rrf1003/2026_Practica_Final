import shutil
import subprocess
from pathlib import Path
from config import ConfigSingleton

class RepoManager:
    """
    Gestor de repositorios.
    Responsabilidad: Clonar repositorios remotos y gestionar su almacenamiento local.
    """

    def __init__(self):
        self.config = ConfigSingleton.get_instance()
    
    def ensure_repo(self, repo_url: str) -> Path:
        """
        Asegura que el repositorio esiste localmente.
        1. Calcula la ruta destino basada en el nombre del repo.
        2. Si ya existe, devuelve la ruta.
        3. Si no existe, lo clona.
        """
        repo_name = self._extract_repo_name(repo_url)
        destination = self.config.repo_cache_dir / repo_name

        if destination.exists():
            # Si ya existe asumimos que está listo para analizar.
            # (La lógica de 'force' / actualización la maneja el Proxy borrando antes)
            return destination
        
        self._clone_repo(repo_url, destination)
        return destination
    
    def remove_repo(self, path: Path):
        """
        Elimina un directorio de repositorio local.
        Se usa cuando se fuerza el recálculo (force=True)
        """
        if path.exists() and path.is_dir():
            # shutil.rmtree elimina recursivamente todo el contenido
            shutil.rmtree(path, ignore_errors=True)
            print(f"[RepoManager] Repositorio eliminado: {path}")
    
    def _extract_repo_name(self, url: str) -> str:
        """
        Extrae un nombre de carpeta seguro desde la URL.
        """
        # Nos quedamos con la última parte de la URL
        name = url.rstrip("/").split("/")[-1]

        # Quitamos la extensión .git si la tiene
        if name.endswith(".git"):
            name = name[:-4]
        return name

    
    def _clone_repo(self, url: str, destination: Path):
        """
        Ejecuta el comando 'git clone' usando un subproceso del sistema.
        """
        print(f"[RepoManager] Clonado {url} en {destination}...")

        try:
            # subprocess.run espera a que el comando termine.
            # check=True lanza una excepción si git devuelve error
            subprocess.run(
                ["git", "clone", url, str(destination)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            # Si falla lanzamos error legible
            error_msg = e.stderr.decode().strip()
            raise RuntimeError(f"Error al clonar el repositorio: {error_msg}")