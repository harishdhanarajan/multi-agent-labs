import pytest
from calculator import add, subtract, multiply, divide

def test_add():
    # Basic addition tests
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    # Additional tests for edge cases
    assert add(1e10, 1) == 1e10 + 1
    assert add(-1e10, -1) == -1e10 - 1

def test_subtract():
    # Basic subtraction tests
    assert subtract(5, 3) == 2
    assert subtract(0, 1) == -1
    assert subtract(-1, -1) == 0
    # Additional tests for edge cases
    assert subtract(1e10, 1) == 1e10 - 1
    assert subtract(-1e10, -1) == -1e10 + 1

def test_multiply():
    # Basic multiplication tests
    assert multiply(2, 3) == 6
    assert multiply(-1, 1) == -1
    assert multiply(0, 10) == 0
    # Additional tests for edge cases
    assert multiply(1e10, 2) == 2e10
    assert multiply(1, 0) == 0
    assert multiply(-1, -1) == 1

def test_divide():
    # Basic division tests
    assert divide(6, 3) == 2
    assert divide(-6, -3) == 2
    assert divide(0, 1) == 0
    # Additional tests for edge cases
    assert divide(1e10, 2) == 5e9
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(1, 0)

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(1, 0)
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(0, 0)
