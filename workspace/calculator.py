def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def format_result(operation, a, b, result):
    """Return a user-friendly formatted string for an arithmetic result."""
    symbols = {
        "add": "+",
        "subtract": "-",
        "multiply": "×",
        "divide": "÷",
    }
    symbol = symbols.get(operation, "?")
    return f"{a} {symbol} {b} = {result}"


def print_result(operation, a, b, result):
    """Print the result of a calculation in a user-friendly format."""
    print("\n" + "=" * 40)
    print(f"  {format_result(operation, a, b, result)}")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 40)
    print("       Simple Calculator")
    print("=" * 40)

    operations = [
        ("add", add, 10, 5),
        ("subtract", subtract, 10, 5),
        ("multiply", multiply, 10, 5),
        ("divide", divide, 10, 5),
    ]

    for op_name, op_func, a, b in operations:
        result = op_func(a, b)
        print(f"  {format_result(op_name, a, b, result)}")

    print("=" * 40 + "\n")
