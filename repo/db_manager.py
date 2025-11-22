import sqlite3
import json
from typing import Optional, List, Dict
from config import ConfigSingleton

class DBManager:
    """
    Gestor de Base de Datos SQLite.
    Responsabilidad: Persistir los resultados de los análisis y recuperar el historial.
    """

    def __init__(self):
        self.config = ConfigSingleton.get_instance()
        self.init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Crea una conexión a la base de datos configurada.
        """
        return sqlite3.connect(self.config.db_path)
    
    def init_db(self):
        """
        Crea la tabla 'analyses' si no existe.
        Esquema basado en el enunciado del proyecto.
        """
        schema = """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_url TEXT,
            analyzed_at TEXT,
            result_json TEXT
        );
        """
        with self._get_connection() as conn:
            conn.execute(schema)
    
    def save_analysis(self, result: Dict) -> None:
        """
        Guarda un nuevo análisis en la base de datos.
        Recibe el diccionario completo de resultados.
        """
        repo_url = result.get("repo")
        analyzed_at = result.get("analyzed_at")

        # Convertimos el diccionario de resultados a un string JSON
        resul_json = json.dumps(result)

        query = """
        INSERT INTO analyses (repo_url, analyzed_at, result_json)
        VALUES (?, ?, ?)
        """

        try:
            with self._get_connection() as conn:
                conn.execute(query, (repo_url, analyzed_at, resul_json))
        except sqlite3.Error as e:
            print(f"[DBManager] Error al guardar análisis: {e}")
    
    def get_latest_analysis(self, repo_url: str) -> Optional[Dict]:
        """
        Recupera el análisis más reciente para un repositorio dado.
        Devuelve el diccionario de resultados o None si no existe.
        """
        query = """
        SELECT result_json FROM analyses
        WHERE repo_url = ?
        ORDER BY analyzed_at DESC
        LIMIT 1
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (repo_url,))
            row = cursor.fetchone()

            if row:
                return json.loads(row[0])
            return None
    
    def list_analyses(self, limit: int = 50) -> List[Dict]:
        """
        Devuelve una lista de los últimos análisis realizados.
        Se usa para mostrar el historial en la UI
        """
        query = """
        SELECT result_json FROM analyses
        ORDER BY analyzed_at DESC
        LIMIT ?
        """

        analyses = []
        with self._get_connection as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()

            for row in rows:
                # Deserializamos cada fila para devolver objetos completos
                analyses.append(json.loads(row[0]))
        
        return analyses