from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SubjectInterface(ABC):
    """
    Interfaz común para el RealSubject y el Proxy.
    Define las operaciones que el cliente (UI) puede solicitar
    """

    @abstractmethod
    def peticion(self, repo_url: str, force: bool = False) -> Dict[str, Any]:
        """
        Solicita el análisis de un repositorio
        """
        raise NotImplementedError
    
    @abstractmethod
    def list_analyses(self) -> List[Dict[str, Any]]:
        """
        Solicita el historial de análisis previos.
        """
        raise NotImplementedError