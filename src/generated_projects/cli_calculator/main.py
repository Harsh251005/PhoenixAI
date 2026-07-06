from __future__ import annotations
import sys
from typing import Any
from datetime import datetime
from calculator import operations, storage


def prompt_number(prompt: str) -> float:
    """Prompt the user for a number and return it as float, retrying on invalid input."""
    while True:
        try:
            raw = input(prompt).strip()
            value = float(raw)
            return value
        except ValueError:
            print(f"Invalid number: '{raw}'. Please enter a valid numeric value.")


def record_and_print(operation_desc: str, result: Any) -> None:
    """Print a result to the user and append an entry to persistent history."""
    print(f"Result: {result}")
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "operation": operation_desc,
        "result": result,
    }
    try:
        storage.append_history(entry)
    except Exception as exc:  # storage has its own error messages, but catch to avoid crash
        print(f"Warning: Failed to save history: {exc}")


def main_menu() -> None:
    """Main interactive loop offering calculator operations until the user exits."""
    print("Welcome to CLI Calculator. Choose an option (type the number) or 0 to exit.")
    while True:
        print("\nMenu:\n"
              "1) Add\n"
              "2) Subtract\n"
              "3) Multiply\n"
              "4) Divide\n"
              "5) Power (a ** b)\n"
              "6) Evaluate expression (safe)\n"
              "7) View history\n"
              "8) Clear history\n"
              "0) Exit")
        choice = input("Select option: ").strip()
        if choice == "0":
            print("Goodbye.")
            break
        elif choice in {"1", "2", "3", "4", "5"}:
            a = prompt_number("Enter first number: ")
            b = prompt_number("Enter second number: ")
            try:
                if choice == "1":
                    res = operations.add(a, b)
                    op_desc = f"add({a}, {b})"
                elif choice == "2":
                    res = operations.subtract(a, b)
                    op_desc = f"subtract({a}, {b})"
                elif choice == "3":
                    res = operations.multiply(a, b)
                    op_desc = f"multiply({a}, {b})"
                elif choice == "4":
                    res = operations.divide(a, b)
                    op_desc = f"divide({a}, {b})"
                else:  # choice == "5"
                    res = operations.power(a, b)
                    op_desc = f"power({a}, {b})"
                record_and_print(op_desc, res)
            except Exception as exc:
                print(f"Error during operation: {exc}")
        elif choice == "6":
            expr = input("Enter arithmetic expression (e.g. 2*(3+4) - 1): ").strip()
            try:
                res = operations.evaluate_expression(expr)
                record_and_print(f"expr: {expr}", res)
            except Exception as exc:
                print(f"Invalid expression or evaluation error: {exc}")
        elif choice == "7":
            try:
                history = storage.load_history()
                if not history:
                    print("History is empty.")
                else:
                    print("History entries (most recent last):")
                    for idx, item in enumerate(history, start=1):
                        ts = item.get("timestamp", "?")
                        op = item.get("operation", "?")
                        res = item.get("result", "?")
                        print(f"{idx}. [{ts}] {op} = {res}")
            except Exception as exc:
                print(f"Failed to load history: {exc}")
        elif choice == "8":
            confirm = input("Type 'yes' to clear history, anything else to cancel: ").strip().lower()
            if confirm == "yes":
                try:
                    storage.save_history([])
                    print("History cleared.")
                except Exception as exc:
                    print(f"Failed to clear history: {exc}")
            else:
                print("Clear cancelled.")
        else:
            print(f"Unknown option: '{choice}'. Please select a valid menu number.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(0)
