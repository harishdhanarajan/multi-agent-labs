from calculator import add


def add_numbers(a, b):
    """Add two numbers using the add function and return the result."""
    return add(a, b)


def print_result(operation, a, b, result):
    """Print the result of an arithmetic operation in a user-friendly format."""
    print("=" * 40)
    print(f"  Operation : {operation}")
    print(f"  Operand 1 : {a}")
    print(f"  Operand 2 : {b}")
    print(f"  Result    : {result}")
    print("=" * 40)


if __name__ == "__main__":
    try:
        num1 = float(input("Enter the first number: "))
        num2 = float(input("Enter the second number: "))
        result = add_numbers(num1, num2)
        print_result("Addition", num1, num2, result)
    except ValueError:
        print("\n[Error] Invalid input. Please enter valid numbers.")
