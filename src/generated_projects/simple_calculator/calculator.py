def add(a: float, b: float) -> float:
    """Returns the sum of two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Returns the difference of two numbers."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Returns the product of two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Returns the quotient of two numbers. Raises ValueError on division by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def calculator(operation: str, a: float, b: float) -> float:
    """Performs the specified operation on two numbers."""
    operations = {
        'add': add,
        'subtract': subtract,
        'multiply': multiply,
        'divide': divide
    }

    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}. Allowed operations: {list(operations.keys())}")
    return operations[operation](a, b)


def main() -> None:
    """Main function for executing the calculator with predefined test values."""
    try:
        print("Addition (3 + 5):", calculator('add', 3, 5))
        print("Subtraction (10 - 4):", calculator('subtract', 10, 4))
        print("Multiplication (2 * 6):", calculator('multiply', 2, 6))
        print("Division (8 / 2):", calculator('divide', 8, 2))
        print("Division by zero (8 / 0):", calculator('divide', 8, 0))
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()