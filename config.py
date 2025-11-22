import os
from pathlib import Path

class ConfigSingleton:
    """
    Clase Singleton para gestionar la configuración global de la aplicación.
    Almacena rutas y parámetros por defecto.
    """
    _instance = None

    def __init__(self):
        """
        Inicializa la configuración.
        Lanza una excepción si se intenta directamente habiendo una instancia
        """
        if ConfigSingleton._instance is not None:
            raise Exception("Esta clase es un Singleton. Usa ConfigSIngleton.get_instance().")
        
        # Obtiene el directorio de trabajo actual (root del proyecto) 
        self.base_dir = Path(os.getcwd())

        # 1. Directorio donde descargaremos los repositorios (ignorando en .gitignore)
        self.repo_cache_dir = self.base_dir / "repo_cache"

        # 2. Ruta del fichero de Base de Datos SQLite
        self.db_path = self.base_dir / "analysis_v2.db"

        # 3. Ventana por defecto para detección de duplicados
        self.duplication_window = 4

        # Crear el directorio de caché automáticamente si no existe
        self._ensure_directories()

    @staticmethod
    def get_instance():
        """
        Método estático de acceso a la instancia única
        """
        if ConfigSingleton._instance is None:
            ConfigSingleton._instance = ConfigSingleton()
        return ConfigSingleton._instance
    
    def _ensure_directories(self):
        """
        Asegurar que los directorios necesarios existan.
        """
        self.repo_cache_dir.mkdir(exist_ok=True)
        print(f"[Config] Directorio de caché asegurado en: {self.repo_cache_dir}")
    
    def as_dict(self) -> dict:
        """
        Devuelve la configuración actual como diccionario
        """
        return{
            "repo_cache_dir": str(self.repo_cache_dir),
            "db_path": str(self.db_path),
            "duplication_window": self.duplication_window
        }