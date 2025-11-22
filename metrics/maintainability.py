import ast
import math
from pathlib import Path
from typing import Any, Set
from .base import MetricStrategy

class MaintainabilityStrategy(MetricStrategy):
    """
    Calcula el Índice de Mantenibilidad (Maintainability Index - MI).
    Formula Original: MI = 171 -5.2 * ln(V) -0.23 * CC - 16.2 * ln(LOC)
    Luego se escala al rango 0-100.
    """

    def compute(self, filepath: Any, **kwargs) -> float:
        """
        Calcula el MI de un fichero.

        Args:
            filepath (Path): Ryta al fichero.

        Returns:
            float: Valor entre 0 y 100.
        """
        if not isinstance(filepath, Path):
            filepath = Path(str(filepath))

        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            if not content.strip():
                return 100.0
                
            tree = ast.parse(content)
        except Exception:
            return 0.0

        # 1. Calcular LOC (Lineas de código vacías)
        loc = len([line for line in content.splitlines() if line.strip()])
        if loc == 0:
            return 100.0

        # 2. Calcular Complejidad Ciclomática (CC) Total del archivo
        cc = self._compute_cc(tree)

        # 3. Calcular Volumen de Halstead (V)
        volume = self._compute_halstead_volume(tree)

        # 4. Aplicar Fórmula MI
        # Evitamos log(0) usando max(1, value)
        try:
            term_volume = 5.2 * math.log(max(1, volume))
            term_cc = 0.23 * cc
            term_loc = 16.2 * math.log(max(1, loc))
            
            mi_raw = 171 - term_volume - term_cc - term_loc
            
            # Escalamos de 0-171 a 0-100 (Estándar Visual Studio)
            mi_normalized = max(0.0, mi_raw * 100 / 171.0)
            
            return min(100.0, mi_normalized)
            
        except ValueError:
            return 0.0

    def _compute_cc(self, tree: ast.AST) -> int:
        """
        Suma la complejidad de todos los nodos de decisión en el archivo.
        """
        complexity = 1
        decision_nodes = (
            ast.If, ast.For, ast.AsyncFor, ast.While, 
            ast.With, ast.AsyncWith, ast.ExceptHandler, ast.Assert
        )
        for node in ast.walk(tree):
            if isinstance(node, decision_nodes):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # --- CORRECCIÓN AQUÍ ---
                complexity += len(node.values) - 1
        return complexity

    def _compute_halstead_volume(self, tree: ast.AST) -> float:
        """
        Calcula el volumen de Halstead aproximado.
        V = N * log2(n)
        Donde:
            N = Total de operadores + operandos
            n = Vocabulario único (operadores únicos + operandos únicos)
        """

        operators = 0
        operands = 0
        unique_operators: Set[str] = set()
        unique_operands: Set[str] = set()

        for node in ast.walk(tree):
            # Simplificación: Consideramos nodos de tipo operador como operadores
            if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, 
                                 ast.Pow, ast.LShift, ast.RShift, ast.BitOr, 
                                 ast.BitXor, ast.BitAnd, ast.FloorDiv)):
                op_name = type(node).__name__
                operators += 1
                unique_operators.add(op_name)
            
            # Simplificación: Nombres de variables y constantes como operandos
            elif isinstance(node, ast.Name):
                operands += 1
                unique_operands.add(node.id)
            elif isinstance(node, ast.Constant):
                operands += 1
                unique_operands.add(str(node.value))
                
        N = operators + operands
        n = len(unique_operators) + len(unique_operands)
        
        if n == 0:
            return 0.0
            
        return N * math.log2(n)