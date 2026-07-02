"""
Simple Calculator

Interactive command-line calculator supporting basic operations.
"""
from typing import Optional
import math
import sys


# ------------------ Configuration / Constants ------------------
MENU = (
    "0) Exit",
    "1) Add (a + b)",
    "2) Subtract (a - b)",
    "3) Multiply (a * b)",
    "4) Divide (a / b)",
    "5) Power (a ** b)",
    "6) Square root (sqrt(a))",
)


# ------------------ Helper Functions ------------------
def safe_input(prompt: str) -> str:
    """Read input from stdin, handling EOF/KeyboardInterrupt gracefully."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt) as exc:
        print("\nInput interrupted. Exiting calculator.")
        sys.exit(0)


def parse_number(raw: str) -> float:
    """Parse a string into a float, raising ValueError on failure."""
    raw_stripped = raw.strip()
    if raw_stripped == "":
        raise ValueError("Empty input")
    try:
        return float(raw_stripped)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value: '{raw}'") from exc


def get_numeric_input(prompt: str) -> Optional[float]:
    """Prompt the user for a number; return the parsed float or None if user typed 'back'."""
    while True:
        raw = safe_input(prompt + " (type 'back' to cancel): ")
        if raw.strip().lower() == "back":
            return None
        try:
            return parse_number(raw)
        except ValueError as exc:
            print(f"Error: {exc}. Please enter a valid number or 'back'.")


# ------------------ Operation Functions ------------------
def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference a - b."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return the quotient a / b; raises ZeroDivisionError if b is zero."""
    if b == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    return a / b


def power(a: float, b: float) -> float:
    """Return a raised to the power b."""
    return a ** b


def sqrt(a: float) -> float:
    """Return the square root of a; raises ValueError if a is negative."""
    if a < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    return math.sqrt(a)


# ------------------ Core Interaction Logic ------------------
def print_menu() -> None:
    """Display the calculator menu."""
    print("\nSimple Calculator")
    for line in MENU:
        print(line)


def handle_choice(choice: str) -> None:
    """Handle a single menu choice from the user."""
    choice = choice.strip()
    if choice == "1":
        a = get_numeric_input("Enter first addend")
        if a is None:
            print("Operation cancelled.")
            return
        b = get_numeric_input("Enter second addend")
        if b is None:
            print("Operation cancelled.")
            return
        print(f"Result: {add(a, b)}")

    elif choice == "2":
        a = get_numeric_input("Enter minuend")
        if a is None:
            print("Operation cancelled.")
            return
        b = get_numeric_input("Enter subtrahend")
        if b is None:
            print("Operation cancelled.")
            return
        print(f"Result: {subtract(a, b)}")

    elif choice == "3":
        a = get_numeric_input("Enter first factor")
        if a is None:
            print("Operation cancelled.")
            return
        b = get_numeric_input("Enter second factor")
        if b is None:
            print("Operation cancelled.")
            return
        print(f"Result: {multiply(a, b)}")

    elif choice == "4":
        a = get_numeric_input("Enter dividend")
        if a is None:
            print("Operation cancelled.")
            return
        b = get_numeric_input("Enter divisor")
        if b is None:
            print("Operation cancelled.")
            return
        try:
            print(f"Result: {divide(a, b)}")
        except ZeroDivisionError as exc:
            print(f"Error: {exc}")

    elif choice == "5":
        a = get_numeric_input("Enter base")
        if a is None:
            print("Operation cancelled.")
            return
        b = get_numeric_input("Enter exponent")
        if b is None:
            print("Operation cancelled.")
            return
        try:
            print(f"Result: {power(a, b)}")
        except OverflowError as exc:
            print(f"Error: numeric overflow: {exc}")

    elif choice == "6":
        a = get_numeric_input("Enter value for sqrt")
        if a is None:
            print("Operation cancelled.")
            return
        try:
            print(f"Result: {sqrt(a)}")
        except ValueError as exc:
            print(f"Error: {exc}")

    else:
        print("Invalid selection. Please choose a valid menu number.")


def main() -> None:
    """Main loop for the interactive calculator."""
    while True:
        print_menu()
        raw = safe_input("Select an option (type 0 to exit): ")
        if raw.strip() == "0":
            print("Goodbye!")
            break
        handle_choice(raw)


if __name__ == "__main__":
    main()
