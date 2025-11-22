import ast
from typing import Any
from .base import MetricStrategy

class NumImportsStrategy(MetricStrategy):
    """
    Estrategia para contar el número de sentencias de importación.
    Usa AST (Abstract Syntax Tree) para evitar falsos positivos en comentarios o strings.
    """
    def compute(self, source: Any, **kwargs) -> int:
        """
        Analiza el árbol sintáctico y cuenta nodos Import e ImportFrom.
        
        Args:
            source (str): El código fuente del archivo.
            
        Returns:
            int: Cantidad de imports encontrados.
        """
        if not source:
            return 0
        
        try:
            # Parseamos el código fuente a un árbol de nodos
            tree = ast.parse(source)
        except SyntaxError:
            # Si el archivo tiene errores de sintaxis (no es Python válido),
            # devolvemos 0 porque no podemos analizarlo con AST.
            return 0
        
        count = 0
        # ast.walk recorre todos los nodos del árbol recursivamente
        for node in ast.walk(tree):
            # Detectamos: "import x" (ast.Import) y "from x import y" (ast.ImportFrom)
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                count += 1
        return count