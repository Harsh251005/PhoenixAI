"""
Simple Calculator CLI

A safe, console-based calculator that evaluates arithmetic expressions
without using eval. Supports +, -, *, /, //, %, ** and unary +/-. Also
provides a small interactive REPL with history and an `ans` variable
containing the previous result.

Usage:
    python calculator_cli.py            # start interactive REPL
    python calculator_cli.py 2+3*4      # evaluate expression passed as argument

Commands inside REPL:
    help      - show help
    history   - show evaluated expressions and results
    clear     - clear history
    exit/quit - exit the calculator

"""
from __future__ import annotations

import ast
import operator
import sys
from typing import Any, Dict, List, Tuple, Union

Number = Union[int, float]


class ExpressionEvaluator(ast.NodeVisitor):
    """Safely evaluate arithmetic expressions represented as ASTs.

    Only a small set of nodes and operators are allowed:
      - Binary ops: +, -, *, /, //, %, **
      - Unary ops: +, -
      - Numeric constants (int and float)
      - Names limited to provided variables (e.g. 'ans')
    """

    _binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    _unary_operators = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def __init__(self, variables: Dict[str, Number] | None = None) -> None:
        self.variables: Dict[str, Number] = variables or {}

    def visit(self, node: ast.AST) -> Number:
        """Visit a node and ensure return type is numeric."""
        result = super().visit(node)
        if not isinstance(result, (int, float)):
            raise ValueError("Expression did not evaluate to a numeric result")
        return result

    def visit_Expression(self, node: ast.Expression) -> Number:  # type: ignore[override]
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Number:
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value!r}")

    # For compatibility with older AST node names if ever encountered
    def visit_Num(self, node: ast.AST) -> Number:  # pragma: no cover - compatibility
        return self.visit_Constant(node)  # type: ignore[arg-type]

    def visit_BinOp(self, node: ast.BinOp) -> Number:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        func = self._binary_operators.get(op_type)
        if func is None:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        try:
            return func(left, right)
        except ZeroDivisionError:
            raise

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Number:
        operand = self.visit(node.operand)
        op_type = type(node.op)
        func = self._unary_operators.get(op_type)
        if func is None:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return func(operand)

    def visit_Name(self, node: ast.Name) -> Number:
        if node.id in self.variables:
            value = self.variables[node.id]
            if not isinstance(value, (int, float)):
                raise ValueError(f"Variable '{node.id}' is not numeric")
            return value
        raise ValueError(f"Unknown variable: {node.id}")

    def generic_visit(self, node: ast.AST) -> Any:  # pragma: no cover - safety
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def safe_eval(expression: str, variables: Dict[str, Number] | None = None) -> Number:
    """Safely evaluate a single arithmetic expression string.

    Raises:
        SyntaxError: if the expression cannot be parsed.
        ValueError: for unsupported nodes or names.
        ZeroDivisionError: for division by zero.
    """
    if not expression.strip():
        raise ValueError("Empty expression")

    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise SyntaxError("Invalid expression syntax") from exc

    evaluator = ExpressionEvaluator(variables)
    return evaluator.visit(parsed)


def format_number(value: Number) -> str:
    """Format a numeric result: show as int when appropriate."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def evaluate_and_report(expression: str, variables: Dict[str, Number]) -> Tuple[bool, str, Number | None]:
    """Evaluate expression and return (success, message, numeric_result_or_None)."""
    try:
        result = safe_eval(expression, variables)
        return True, format_number(result), result
    except ZeroDivisionError:
        return False, "Error: division by zero.", None
    except SyntaxError:
        return False, "Error: invalid expression syntax.", None
    except ValueError as exc:
        return False, f"Error: {str(exc)}", None
    except Exception as exc:  # pragma: no cover - unexpected
        return False, f"Unexpected error: {exc}", None


def repl() -> None:
    """Run the interactive Read-Eval-Print Loop for the calculator."""
    print("Simple Calculator — type 'help' for commands. Press Ctrl+C or type 'exit' to quit.")

    history: List[Tuple[str, str]] = []
    variables: Dict[str, Number] = {}

    while True:
        try:
            raw = input("calc> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting calculator.")
            break

        if not raw:
            continue

        lowered = raw.lower()
        if lowered in ("exit", "quit"):
            print("Goodbye.")
            break
        if lowered == "help":
            print(
                "Commands:\n  help - show this help\n  history - show past calculations\n  clear - clear history\n  exit, quit - exit the calculator\n\n"
                "You can use the variable 'ans' to refer to the previous numeric result.\n"
                "Supported operators: +, -, *, /, //, %, ** and unary +/-."
            )
            continue
        if lowered == "history":
            if not history:
                print("(no history)")
                continue
            for idx, (expr, result) in enumerate(history, start=1):
                print(f"{idx}: {expr} = {result}")
            continue
        if lowered == "clear":
            history.clear()
            print("History cleared.")
            continue

        # Evaluate an expression
        success, message, numeric = evaluate_and_report(raw, variables)
        if success:
            print(message)
            history.append((raw, message))
            # Update 'ans' variable to most recent numeric result
            if numeric is not None:
                variables["ans"] = numeric
        else:
            print(message)
            history.append((raw, message))


def evaluate_cli_expression(argv: List[str]) -> int:
    """Evaluate expression passed on the command line and print result.

    Returns exit code 0 on success, non-zero on error.
    """
    expr = " ".join(argv[1:]).strip()
    if not expr:
        print("No expression provided.")
        return 2

    success, message, _ = evaluate_and_report(expr, {})
    print(message)
    return 0 if success else 1


def main() -> None:
    """Entry point for the calculator script."""
    if len(sys.argv) > 1:
        exit_code = evaluate_cli_expression(sys.argv)
        raise SystemExit(exit_code)
    repl()


if __name__ == "__main__":
    main()
