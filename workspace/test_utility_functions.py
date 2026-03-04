import pytest
from utility_functions import greet, reverse_string

def test_greet():
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Bob!"
    assert greet("") == "Hello, !"

def test_reverse_string():
    assert reverse_string("hello") == "olleh"
    assert reverse_string("Python") == "nohtyP"
    assert reverse_string("") == ""
    assert reverse_string("a") == "a"
