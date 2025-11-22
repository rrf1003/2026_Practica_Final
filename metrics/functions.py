import ast
from typing import Any, Dict
from .base import MetricStrategy

class FunctionsStrategy(MetricStrategy):
    """
    Estrategia compleja que analiza definiciones de funciones usando AST.
    Calcula: LOC, Argumentos, Complejidad Ciclomática y Anidamiento.
    """

    def compute(self, ast_node: Any, **kwargs) -> Dict[str, Any]:
        """
        Recorre el AST buscando funciones y calculando sus métricas.
        
        Args:
            ast_node (ast.AST): El árbol sintáctico del módulo (archivo).
            
        Returns:
            Dict[str, Any]: Diccionario con las métricas de cada función.
            Ej: { "mi_funcion": {"loc": 10, "params": 2, "cc": 3, "max_nesting": 1} }
        """
        results = {}
        
        if not isinstance(ast_node, ast.AST):
            return results

        for node in ast.walk(ast_node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                
                # 1. LOC
                start = getattr(node, 'lineno', 0)
                end = getattr(node, 'end_lineno', start)
                loc = (end - start) + 1

                # 2. Número de parámetros
                num_params = len(node.args.args)

                # 3. Complejidad Ciclomática (CC)
                cc = self._compute_cc(node)

                # 4. Profundidad máxima de anidamiento
                max_nesting = self._compute_nesting(node)

                results[func_name] = {
                    "loc": loc,
                    "params": num_params,
                    "cc": cc,
                    "max_nesting": max_nesting
                }

        return results

    def _compute_cc(self, func_node: ast.AST) -> int:
        """
        Calcula la Complejidad Ciclomática.
        """
        complexity = 1
        
        for node in ast.walk(func_node):
            # Puntos de decisión estándar
            if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, 
                                 ast.With, ast.AsyncWith, ast.ExceptHandler, 
                                 ast.Assert)):
                complexity += 1
            
            # Operadores booleanos (and, or)
            elif isinstance(node, ast.BoolOp):
                # --- AQUÍ ESTABA EL POSIBLE ERROR ---
                # node.values es una lista de operandos. Necesitamos su longitud.
                complexity += len(node.values) - 1
                
        return complexity

    def _compute_nesting(self, node: ast.AST, current_depth: int = 0) -> int:
        """
        Calcula recursivamente la profundidad máxima de anidamiento.
        """
        max_depth = current_depth
        nesting_nodes = (ast.If, ast.For, ast.AsyncFor, ast.While, 
                         ast.Try, ast.FunctionDef, ast.AsyncFunctionDef)

        for child in ast.iter_child_nodes(node):
            next_depth = current_depth
            if isinstance(child, nesting_nodes):
                next_depth += 1
            child_depth = self._compute_nesting(child, next_depth)
            max_depth = max(max_depth, child_depth)
            
        return max_depth