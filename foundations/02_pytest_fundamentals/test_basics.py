"""
Basic pytest patterns.

Topics:
- Simple assertions
- Test discovery
- Running tests
- Assert introspection
- Testing exceptions
- Test organization
"""

import pytest


def test_assert_equality():
    """Simple equality assertion."""
    assert 1 + 1 == 2


def test_assert_inequality():
    """Inequality assertion."""
    assert 3 != 4


def test_assert_greater():
    """Comparison assertion."""
    assert 10 > 5
    assert 10 >= 10


def test_assert_in():
    """Membership assertion."""
    assert "hello" in "hello world"
    assert 3 in [1, 2, 3, 4]


def test_assert_boolean():
    """Boolean assertion."""
    assert True
    assert not False
    assert bool([1, 2, 3])  # non-empty list is truthy
    assert not bool([])  # empty list is falsy


def test_assert_with_message():
    """Assertion with custom message."""
    value = 10
    assert value > 0, f"Expected positive value, got {value}"


def test_multiple_assertions():
    """Multiple assertions in one test."""
    result = {"name": "Alice", "age": 30}
    assert "name" in result
    assert result["name"] == "Alice"
    assert result["age"] > 0


def test_approximate_equality():
    """Test floating point equality with tolerance."""
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert 0.1 + 0.2 != 0.3  # This is why pytest.approx exists!


def test_exception_raised():
    """Test that an exception is raised."""
    with pytest.raises(ValueError):
        raise ValueError("Something went wrong")


def test_exception_with_message():
    """Test exception with specific message."""
    with pytest.raises(ValueError, match="invalid input"):
        raise ValueError("invalid input provided")


def test_exception_with_regex():
    """Test exception message with regex."""
    with pytest.raises(ValueError, match=r"error code: \d+"):
        raise ValueError("error code: 404")


def test_exception_not_raised():
    """Test that no exception is raised."""
    try:
        result = 1 + 1
        assert result == 2
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


def test_none():
    """Test None values."""
    result = None
    assert result is None
    assert result == None  # Works but 'is None' preferred


def test_type_checking():
    """Test types."""
    value = "hello"
    assert isinstance(value, str)
    assert type(value) == str  # Works but isinstance preferred


class TestCalculator:
    """Test class for organizing related tests."""

    def test_addition(self):
        """Test addition."""
        assert 2 + 2 == 4

    def test_subtraction(self):
        """Test subtraction."""
        assert 5 - 3 == 2

    def test_multiplication(self):
        """Test multiplication."""
        assert 3 * 4 == 12

    def test_division(self):
        """Test division."""
        assert 10 / 2 == 5

    def test_division_by_zero(self):
        """Test division by zero raises exception."""
        with pytest.raises(ZeroDivisionError):
            _ = 10 / 0


class TestStringOperations:
    """Test class for string operations."""

    def test_concatenation(self):
        """Test string concatenation."""
        assert "hello" + " " + "world" == "hello world"

    def test_uppercase(self):
        """Test uppercase conversion."""
        assert "hello".upper() == "HELLO"

    def test_split(self):
        """Test string split."""
        result = "a,b,c".split(",")
        assert result == ["a", "b", "c"]
        assert len(result) == 3

    def test_strip(self):
        """Test string strip."""
        assert "  hello  ".strip() == "hello"

    def test_startswith(self):
        """Test string startswith."""
        assert "hello world".startswith("hello")
        assert not "hello world".startswith("world")


def test_list_operations():
    """Test list operations."""
    my_list = [1, 2, 3]

    my_list.append(4)
    assert my_list == [1, 2, 3, 4]

    my_list.remove(2)
    assert my_list == [1, 3, 4]

    assert len(my_list) == 3
    assert 3 in my_list


def test_dict_operations():
    """Test dictionary operations."""
    my_dict = {"a": 1, "b": 2}

    assert my_dict["a"] == 1
    assert "a" in my_dict
    assert "c" not in my_dict

    my_dict["c"] = 3
    assert len(my_dict) == 3


@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    """Test for feature not yet implemented."""
    assert False


@pytest.mark.skipif(True, reason="Skip in certain conditions")
def test_conditional_skip():
    """Test that is conditionally skipped."""
    assert True


@pytest.mark.xfail(reason="Known bug")
def test_known_bug():
    """Test for known bug (expected to fail)."""
    assert False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
