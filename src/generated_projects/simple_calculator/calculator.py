"""
Very simple safe calculator REPL.
Supports basic arithmetic with +, -, *, /, %, ** and parentheses.
Uses Python's ast module to safely parse and evaluate numeric expressions.
"""

from __future__ import annotations
import ast
import operator
import sys
from typing import Any, Dict

# Allowed binary operators mapping AST node -> function
_BIN_OPS: Dict[Any, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}

# Allowed unary operators mapping AST node -> function
_UNARY_OPS: Dict[Any, Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def parse_expression(expr: str) -> ast.AST:
    """Parse an expression string into an AST expression node.

    Raises SyntaxError if the expression is invalid.
    """
    try:
        parsed = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise SyntaxError(f"Invalid expression syntax: {e}")
    return parsed.body


def eval_node(node: ast.AST) -> float:
    """Recursively evaluate a safe AST node and return a numeric result.

    Raises TypeError for disallowed nodes and ZeroDivisionError for bad math.
    """
    if isinstance(node, ast.Num):  # type: ignore[attr-defined]
        return node.n  # type: ignore[return-value]

    if isinstance(node, ast.Constant):  # Python 3.8+: numeric constants
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError(f"Unsupported constant type: {type(node.value).__name__}")

    if isinstance(node, ast.BinOp):
        left = eval_node(node.left)
        right = eval_node(node.right)
        op_type = type(node.op)
        func = _BIN_OPS.get(op_type)
        if func is None:
            raise TypeError(f"Unsupported binary operator: {op_type.__name__}")
        try:
            return func(left, right)
        except ZeroDivisionError:
            raise

    if isinstance(node, ast.UnaryOp):
        operand = eval_node(node.operand)
        op_type = type(node.op)
        func = _UNARY_OPS.get(op_type)
        if func is None:
            raise TypeError(f"Unsupported unary operator: {op_type.__name__}")
        return func(operand)

    if isinstance(node, ast.Expression):
        return eval_node(node.body)  # pragma: no cover - defensive

    # Any other node types (Call, Name, Attribute, etc.) are disallowed
    raise TypeError(f"Disallowed expression element: {type(node).__name__}")


def safe_eval(expr: str) -> float:
    """Safely evaluate a numeric arithmetic expression string and return the result.

    Supports +, -, *, /, //, %, **, unary +/- and parentheses. Raises descriptive
    exceptions for invalid input or disallowed operations.
    """
    if not expr or expr.strip() == "":
        raise ValueError("Empty expression")
    node = parse_expression(expr)
    return eval_node(node)


def format_result(value: Any) -> str:
    """Format numeric result for display, using int when appropriate.

    Converts float values that are integer-equivalent to ints for cleaner output.
    """
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value)
    return str(value)


def print_help() -> None:
    """Print usage help text to the user."""
    help_text = (
        "Simple Calculator - enter arithmetic expressions to evaluate.\n"
        "Supported operators: + - * / // % ** and parentheses.\n"
        "Commands:\n"
        "  help    Show this message\n"
        "  quit    Exit the calculator\n"
        "  exit    Exit the calculator\n"
    )
    print(help_text)


def process_input(line: str) -> None:
    """Process one line of user input: evaluate expressions or execute commands."""
    cmd = line.strip()
    if not cmd:
        return
    if cmd.lower() in {"quit", "exit"}:
        print("Goodbye.")
        raise SystemExit(0)
    if cmd.lower() == "help":
        print_help()
        return

    try:
        result = safe_eval(cmd)
    except SyntaxError as e:
        print(f"Syntax error: {e}")
    except ZeroDivisionError:
        print("Math error: division by zero")
    except ValueError as e:
        print(f"Input error: {e}")
    except TypeError as e:
        print(f"Unsupported expression: {e}")
    except Exception as e:
        print(f"Error evaluating expression: {e}")
    else:
        print(format_result(result))


def repl() -> None:
    """Run the interactive read-eval-print loop for the calculator."""
    print("Simple Calculator. Type 'help' for instructions, 'quit' to exit.")
    while True:
        try:
            # Use a prompt compatible with redirected stdin
            if sys.stdin is sys.__stdin__:
                line = input('> ')
            else:
                line = input()
        except EOFError:
            print("\nGoodbye.")
            break
        except KeyboardInterrupt:
            print("\nInterrupted. Type 'quit' or Ctrl-D to exit.")
            continue

        try:
            process_input(line)
        except SystemExit:
            break


if __name__ == "__main__":
    try:
        repl()
    except Exception as e:
        # Catch-all to avoid silent crashes; print a helpful message.
        print(f"Calculator terminated with error: {e}")
        sys.exit(1)
