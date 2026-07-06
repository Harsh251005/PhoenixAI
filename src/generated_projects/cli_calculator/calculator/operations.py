from __future__ import annotations
import ast
from typing import Union

Number = Union[int, float]


def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of two numbers (a - b)."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient a / b. Raises ValueError on division by zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


def power(a: float, b: float) -> float:
    """Return a raised to the power of b."""
    return a ** b


_ALLOWED_BINOPS = {
    ast.Add: lambda x, y: x + y,
    ast.Sub: lambda x, y: x - y,
    ast.Mult: lambda x, y: x * y,
    ast.Div: lambda x, y: x / y,
    ast.Pow: lambda x, y: x ** y,
    ast.Mod: lambda x, y: x % y,
}

_ALLOWED_UNARYOPS = {
    ast.UAdd: lambda x: x,
    ast.USub: lambda x: -x,
}


def _eval_node(node: ast.AST) -> Number:
    """Recursively evaluate a parsed AST node allowing only safe arithmetic operations."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")
    if isinstance(node, ast.Num):  # type: ignore
        return node.n  # type: ignore
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_BINOPS:
            raise ValueError(f"Operator {op_type.__name__} is not allowed")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        # Protect divide-by-zero at runtime
        if op_type is ast.Div and right == 0:
            raise ValueError("Division by zero in expression")
        return _ALLOWED_BINOPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_UNARYOPS:
            raise ValueError(f"Unary operator {op_type.__name__} is not allowed")
        operand = _eval_node(node.operand)
        return _ALLOWED_UNARYOPS[op_type](operand)
    if isinstance(node, ast.Paren):  # pragma: no cover - Paren node not used in current AST
        return _eval_node(node)
    raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def evaluate_expression(expression: str) -> float:
    """Safely evaluate a mathematical expression string and return its numeric result."""
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Syntax error in expression: {exc}")
    # Walk AST to ensure no disallowed nodes are present
    for node in ast.walk(parsed):
        if isinstance(node, (ast.Call, ast.Attribute, ast.Name, ast.Lambda, ast.IfExp, ast.Dict, ast.List, ast.Set, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            raise ValueError(f"Disallowed expression element: {type(node).__name__}")
    result = _eval_node(parsed)
    return float(result)
