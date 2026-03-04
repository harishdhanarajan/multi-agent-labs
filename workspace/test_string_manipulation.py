# This file does not deal with arithmetic operations, so no changes are needed.
from utility_functions import reverse_string, greet

def test_greet():
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Bob!"
    assert greet("") == "Hello, !"
