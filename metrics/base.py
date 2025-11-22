from abc import ABC, abstractmethod
from typing import Any

class MetricStrategy(ABC):
    """
    Clase base abstracta (Interfaz) para las estrategias de métricas.
    Define el contrato que todas las métricas concretas deben seguir.
    Patrón: Strategy
    """

    @abstractmethod
    def compute(self, data: Any, **kwargs) -> Any:
        """
        Calcula la métrica basándose en los datos proporcionados.

        Args:
            data: Puede ser un string (código fuente), un nodo AST,
                  o un Path (ruta la fichero, dependiendo de la estrategia.
            **kwargs: Argumentos opcionales (ej. window size para duplicación.)
        
        Returns:
            El resultado de la métrica (int, float, dict, etc.)
        """
        pass