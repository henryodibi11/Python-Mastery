"""Fixture examples."""
import pytest
import pandas as pd
from pathlib import Path

# Simple fixture
@pytest.fixture
def sample_data():
    """Provide sample DataFrame."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10, 20, 30]
    })

def test_data_shape(sample_data):
    assert sample_data.shape == (3, 2)

def test_data_columns(sample_data):
    assert list(sample_data.columns) == ["id", "value"]

# Fixture with setup/teardown
@pytest.fixture
def temp_csv(tmp_path):
    """Create temp CSV file."""
    # Setup
    csv_file = tmp_path / "data.csv"
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df.to_csv(csv_file, index=False)
    
    yield csv_file  # Provide to test
    
    # Teardown (automatic cleanup via tmp_path)
    print(f"Cleaned up {csv_file}")

def test_read_csv(temp_csv):
    df = pd.read_csv(temp_csv)
    assert len(df) == 2
    assert "a" in df.columns

# Fixture scopes: function (default), class, module, session
@pytest.fixture(scope="module")
def expensive_resource():
    """Created once per module."""
    print("\nSetup expensive resource")
    resource = {"data": "expensive to create"}
    yield resource
    print("\nTeardown expensive resource")

def test_resource_1(expensive_resource):
    assert expensive_resource["data"] == "expensive to create"

def test_resource_2(expensive_resource):
    # Uses same instance as test_resource_1
    assert "data" in expensive_resource
