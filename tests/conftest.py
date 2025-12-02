import pytest
import ast
from pathlib import Path

@pytest.fixture
def simple_code():
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