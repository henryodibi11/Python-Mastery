"""Basic pytest examples."""
import pytest

def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Test functions must start with 'test_'
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_add_floats():
    result = add(0.1, 0.2)
    assert result == pytest.approx(0.3)  # Handle float precision

def test_divide():
    assert divide(10, 2) == 5
    assert divide(9, 3) == 3

def test_divide_by_zero():
    """Test exception handling."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
