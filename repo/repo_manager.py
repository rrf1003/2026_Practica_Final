import shutil
import stat
import subprocess
import os
from pathlib import Path
from config import ConfigSingleton

class RepoManager:
    """
    Gestor de repositorios robusto para Windows/Linux.
    """
    
    def __init__(self):
        self.config = ConfigSingleton.get_instance()

    def ensure_repo(self, repo_url: str) -> Path:
        repo_name = self._extract_repo_name(repo_url)
        destination = self.config.repo_cache_dir / repo_name

        # Doble verificación: Si existe pero está vacía (solo .git), la tratamos como inválida
        if destination.exists():
            # Si solo tiene la carpeta .git y nada más, asumimos que está corrupta y re-clonamos
            items = list(destination.iterdir())
            if len(items) <= 1 and any(x.name == '.git' for x in items):
                print(f"[RepoManager] Carpeta corrupta detectada en {destination}. Re-clonando...")
                self.remove_repo(destination)
            else:
                return destination

        self._clone_repo(repo_url, destination)
        return destination

    def remove_repo(self, path: Path):
        """
        Borra el repositorio manejando permisos de solo lectura en Windows.
        """
        if path.exists():
            print(f"[RepoManager] Borrando {path}...")
            # Usamos un manejador de errores para forzar permisos de escritura
            shutil.rmtree(path, onerror=self._on_rm_error)

    def _on_rm_error(self, func, path, exc_info):
        """
        Manejador de errores para shutil.rmtree.
        Si falla por permiso denegado (común en .git de Windows), 
        le cambia los permisos y vuelve a intentar.
        """
        # El código de error de acceso denegado no siempre es fácil de pillar,
        # pero intentamos cambiar permisos de escritura al archivo
        os.chmod(path, stat.S_IWRITE)
        try:
            func(path)
        except Exception as e:
            print(f"[RepoManager] No se pudo borrar {path}: {e}")

    def _extract_repo_name(self, url: str) -> str:
        name = url.rstrip("/").split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name

    def _clone_repo(self, url: str, destination: Path):
        print(f"[RepoManager] Clonando {url} en {destination}...")
        try:
            # Aseguramos que la carpeta padre existe
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            subprocess.run(
                ["git", "clone", url, str(destination)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode().strip()
            # Si falla, limpiamos para no dejar carpetas zombies
            self.remove_repo(destination)
            raise RuntimeError(f"Error clonando repo: {error_msg}")