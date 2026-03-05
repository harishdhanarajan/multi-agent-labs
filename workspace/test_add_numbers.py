import pytest
from add_numbers import add_numbers

def test_add_numbers_basic():
    assert add_numbers(2, 3) == 5
    assert add_numbers(-2, 3) == 1
    assert add_numbers(10, 0) == 10
    assert add_numbers(2.5, 3.1) == pytest.approx(5.6)

def test_add_numbers_with_zero():
    assert add_numbers(0, 0) == 0

def test_add_numbers_negative():
    assert add_numbers(-5, -10) == -15
