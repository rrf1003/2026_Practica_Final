import ast
import pytest
from metrics.lines import LinesStrategy, TodoStrategy
from metrics.imports import NumImportsStrategy
from metrics.functions import FunctionsStrategy
from metrics.maintainability import MaintainabilityStrategy
from metrics.duplication import DuplicationStrategy

# ==========================================
# 1. DATOS DE PRUEBA (FIXTURES)
# ==========================================

@pytest.fixture
def simple_code():
    """Código Python simple y limpio."""
    return """
def hello(name):
    if name:
        print(f"Hello {name}")
    else:
        print("Hello World")
"""

@pytest.fixture
def simple_ast(simple_code):
    return ast.parse(simple_code)

@pytest.fixture
def spaghetti_code():
    """Código complejo, sucio y difícil de mantener."""
    return """
import os
import sys
import math

def complex_logic(x, y, z):
    # Muchas operaciones y anidamiento
    a = x + y * z
    b = a / 2
    if a > 10:
        for i in range(10):
            while b < 100:
                if i % 2 == 0:
                    print(i)
                b += 1
    elif a < 5:
        print("Low")
    else:
        print("Medium")
    return b
"""

# ==========================================
# 2. TESTS (BATERÍA COMPLETA)
# ==========================================

# --- Tests Básicos (Líneas y TODOs) ---
def test_lines_count(simple_code):
    strategy = LinesStrategy()
    # El string tiene unas 6 líneas efectivas
    assert strategy.compute(simple_code) >= 5

def test_todo_detection():
    code = "# TODO: Refactor this\n# FIXME: Broken logic"
    strategy = TodoStrategy()
    assert strategy.compute(code) == 2

# --- Tests de Imports ---
def test_imports_count():
    code = "import os\nfrom datetime import datetime\nx = 'import fake'"
    strategy = NumImportsStrategy()
    assert strategy.compute(code) == 2

# --- Tests de Funciones (Complejidad y Anidamiento) ---
def test_function_metrics_simple(simple_ast):
    strategy = FunctionsStrategy()
    result = strategy.compute(simple_ast)
    
    assert "hello" in result
    metrics = result["hello"]
    assert metrics["params"] == 1
    assert metrics["cc"] == 2  # Base(1) + If(1)

def test_function_nesting_deep():
    # Probamos un anidamiento profundo: def -> if -> for -> while
    code = """
def deep():
    if True:
        for x in range(10):
            while False:
                pass
    """
    strategy = FunctionsStrategy()
    result = strategy.compute(ast.parse(code))
    
    # El nivel debería ser 3 (if + for + while)
    assert result["deep"]["max_nesting"] == 3

# --- Test de Duplicación (Shingles) ---
def test_duplication_detection(tmp_path):
    # Creamos un archivo con texto MUY repetido
    d = tmp_path / "dup"
    d.mkdir()
    p = d / "copy_paste.py"
    
    # Repetimos el mismo bloque 4 veces
    bloque = "print('linea 1')\nprint('linea 2')\nprint('linea 3')\n"
    contenido = bloque * 4
    
    p.write_text(contenido, encoding="utf-8")
    
    strategy = DuplicationStrategy()
    # Con ventana de 2 líneas, debería detectar mucha duplicación
    ratio = strategy.compute(p, window=2)
    
    # Aseguramos que detecta al menos un 50% de duplicación
    assert ratio > 0.5 

# --- Test de Mantenibilidad (Comparativa) ---
def test_maintainability_score(tmp_path, simple_code, spaghetti_code):
    d = tmp_path / "mi_test"
    d.mkdir()
    
    # 1. Archivo limpio
    clean_file = d / "clean.py"
    clean_file.write_text(simple_code, encoding="utf-8")
    
    # 2. Archivo sucio
    dirty_file = d / "dirty.py"
    dirty_file.write_text(spaghetti_code, encoding="utf-8")
    
    strategy = MaintainabilityStrategy()
    mi_clean = strategy.compute(clean_file)
    mi_dirty = strategy.compute(dirty_file)
    
    # El código limpio debe tener MEJOR nota (mayor valor) que el sucio
    assert mi_clean > mi_dirty
    
    # El código sucio debería tener menos de 100
    assert mi_dirty < 90