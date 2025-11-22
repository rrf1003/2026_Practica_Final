from typing import Any
from .base import MetricStrategy

class LinesStrategy(MetricStrategy):
    """
    Estrategia para contar las líneas totales de un fichero (LOC).
    """
    def compute(self, source: Any, **kwargs) -> int:
        """
        Cuenta los saltos de línea en el código fuente.

        Args:
            source (str): El contenido del archivo.

        Returns:
            int: Número de líneas. Devuelve 0 si el source está vacío.
        """
        if not source:
            return 0
        
        # splitlines() es más robust que split('\n') porque maneja
        # diferentes finales de línea (\r\n, \n, \r) automáticamente.
        return len(source.splitlines())

class TodoStrategy(MetricStrategy):
    """
    Estrategia para contar marcas de deuda técnica (TODO, FIXME).
    """
    def compute(self, source: Any, **kwargs) -> int:
        """
        Escanea el código buscando 'TODO' o 'FIXME' (mayúsculas).
        
        Args:
            source (str): El contenido del archivo.
            
        Returns:
            int: Cantidad total de marcas encontradas.
        """
        if not source:
            return 0
        
        count = 0
        for line in source.splitlines():
            # Buscamos las marcas típicas.
            # Se puede ampliar a minúsculas si se prefiere, pero
            # por convención suelen ir en mayúsculas.
            if  "TODO" in line or "FIXME" in line:
                count += 1
        
        return count