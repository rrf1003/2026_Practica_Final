from pathlib import Path
from typing import Any, List, Set
from .base import MetricStrategy

class DuplicationStrategy(MetricStrategy):
    """
    Estrategia para detectar duplicación de código (Copy-Paste) dentro de un archivo
    utilizando el algoritmo de Shingles (Ventanas Deslizantes) 
    """

    def compute(self, filepath: Any, **kwargs) -> float:
        """
        Calcula el ratio de duplicación interna de un fichero.
        
        Args:
            filepath (Path): Ruta al archivo a analizar.
            window (int, opcional): Tamaño de la ventana (bloque de líneas). Default: 4.
            
        Returns:
            float: Ratio de duplicación (0.0 = único, 1.0 = todo duplicado).
        """
        if not isinstance(filepath, Path):
            # Si nos pasan un string, lo convertimos a Path
            filepath = Path(str(filepath))
        
        # Obtenemos el tamaño de la ventan de los argumentos opcionales (default 4)
        window_size = kwargs.get('window', 4)

        try:
            # Leemos el fichero ignorando errores de codificación (importante para robustez)
            content = filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return 0.0
        
        # 1. Normalización: Limpiamos espacios y líneas vacías
        lines = self._normalize_to_lines(content)

        if len(lines) < window_size:
            return 0.0
        
        # 2. Creación de Shingles (Tejas)
        shingles = self._create_shingles(lines, window_size)

        if not shingles:
            return 0.0
        
        # 3. Detección de duplicados
        # Contamos cuántos shingles aparecen más de una vez
        unique_shingles = set()
        duplicated_shingles = 0

        # Usamos un set auxiliar para rastrear lo que ya hemos visto
        seen_once = set()

        for shingle in shingles:
            if shingle in seen_once:
                # Si ya lo hemos visto, es un duplicado
                duplicated_shingles += 1
            else:
                seen_once.add(shingle)
        
        # El ratio es: Número de bloques duplicados / Total de bloques
        # (Existen varias fórmulas, esta es la de "densidad de duplicación")
        return duplicated_shingles / len(shingles)
    
    def _normalize_to_lines(self, content: str) -> List[str]:
        """
        Convierte el texto en una lista de líneas 'limpias'.
        Elimina espacios al inicio/final y descarta líneas vacías.
        """
        valid_lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped:
                valid_lines.append(stripped)
        return valid_lines
    
    def _create_shingles(self, lines: List[str], window: int) -> List[tuple]:
        """
        Crea una lista de tuplas (shingles) usando una ventana deslizante.
        Ej: lines[A, B, C, D], window=3 --> [(A,B,C), (B,C,D)]
        """
        shingles = []
        # Range llega hasta len -windows + 1 para cubrir el último bloque
        for i in range(len(lines) - window + 1):
            # Range llega hasta len - windows + 1 para cubrir el último bloque
            block = tuple(lines[i : i + window])
            shingles.append(block)
        return shingles