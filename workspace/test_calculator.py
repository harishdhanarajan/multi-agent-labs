import pytest
import calculator

def test_add():
    assert calculator.add(1, 2) == 3
    assert calculator.add(-1, -2) == -3
    assert calculator.add(0, 0) == 0

def test_subtract():
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(-1, -2) == 1

def test_multiply():
    assert calculator.multiply(3, 4) == 12
    assert calculator.multiply(-2, 3) == -6

def test_divide():
    assert calculator.divide(8, 2) == 4
    assert calculator.divide(-9, 3) == -3
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calculator.divide(2, 0)

def test_format_result():
    assert calculator.format_result("add", 2, 3, 5) == "2 + 3 = 5"
    assert calculator.format_result("subtract", 8, 2, 6) == "8 - 2 = 6"
    assert calculator.format_result("multiply", 2, 5, 10) == "2 × 5 = 10"
    assert calculator.format_result("divide", 9, 3, 3) == "9 ÷ 3 = 3"

def test_format_result_unknown():
    assert calculator.format_result("other", 1, 2, 3) == "1 ? 2 = 3"
