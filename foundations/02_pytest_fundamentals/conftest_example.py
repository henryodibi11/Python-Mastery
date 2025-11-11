"""Example conftest.py - Shared test fixtures and configuration.

This file demonstrates pytest configuration patterns used in production codebases.
Place this file in your tests/ directory to share fixtures across all test files.
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, component interaction)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (> 1 second)"
    )
    config.addinivalue_line(
        "markers", "extras: Tests for optional features/dependencies"
    )


# ============================================================================
# Session-Scoped Fixtures (Created Once Per Test Session)
# ============================================================================

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Global test configuration.
    
    Created once per test session, shared across all tests.
    Use for read-only configuration.
    """
    return {
        "env": "test",
        "debug": True,
        "max_retries": 3,
        "timeout": 30,
    }


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory) -> Path:
    """Session-level temporary directory for test data.
    
    Created once, cleaned up after all tests complete.
    """
    data_dir = tmp_path_factory.mktemp("test_data")
    yield data_dir
    # Cleanup handled automatically by tmp_path_factory


# ============================================================================
# Module-Scoped Fixtures (Created Once Per Test Module/File)
# ============================================================================

@pytest.fixture(scope="module")
def sample_csv_data() -> pd.DataFrame:
    """Sample DataFrame for CSV tests.
    
    Created once per module, reused across tests in that module.
    """
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "salary": [50000, 60000, 70000, 80000, 90000],
        "department": ["Sales", "Engineering", "Sales", "Engineering", "HR"]
    })


@pytest.fixture(scope="module")
def sample_json_data() -> Dict[str, Any]:
    """Sample JSON data for API tests."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
            {"id": 3, "name": "Charlie", "active": True},
        ],
        "metadata": {
            "version": "1.0",
            "total": 3
        }
    }


# ============================================================================
# Function-Scoped Fixtures (Created For Each Test - Default)
# ============================================================================

@pytest.fixture
def temp_dir() -> Path:
    """Temporary directory for each test.
    
    Created fresh for each test, cleaned up after test completes.
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Simple DataFrame for testing transforms.
    
    Fresh copy created for each test to prevent test pollution.
    """
    return pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10, 20, 30],
        "category": ["A", "B", "A"]
    })


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """Empty DataFrame for edge case testing."""
    return pd.DataFrame()


@pytest.fixture
def sample_csv_file(tmp_path, sample_dataframe) -> Path:
    """Create temporary CSV file with sample data.
    
    Combines tmp_path (built-in) with sample_dataframe fixture.
    """
    csv_path = tmp_path / "test_data.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_parquet_file(tmp_path, sample_dataframe) -> Path:
    """Create temporary Parquet file with sample data."""
    parquet_path = tmp_path / "test_data.parquet"
    sample_dataframe.to_parquet(parquet_path, index=False)
    return parquet_path


# ============================================================================
# Parameterized Fixtures
# ============================================================================

@pytest.fixture(params=["csv", "parquet", "json"])
def file_format(request):
    """Parametrized fixture for testing multiple file formats.
    
    Tests using this fixture will run once for each format.
    """
    return request.param


@pytest.fixture(params=[
    pd.DataFrame({"a": [1, 2, 3]}),
    pd.DataFrame({"x": [10, 20], "y": [30, 40]}),
    pd.DataFrame({"id": range(100), "value": range(100)}),
])
def various_dataframes(request):
    """Parametrized fixture providing various DataFrame shapes."""
    return request.param


# ============================================================================
# Autouse Fixtures (Automatically Applied)
# ============================================================================

@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment before each test.
    
    Autouse=True means this runs for every test automatically.
    Use sparingly - only for critical setup/teardown.
    """
    # Setup: Reset any global state
    import os
    original_env = os.environ.copy()
    
    yield
    
    # Teardown: Restore environment
    os.environ.clear()
    os.environ.update(original_env)


# ============================================================================
# Composite Fixtures (Fixtures That Use Other Fixtures)
# ============================================================================

@pytest.fixture
def pipeline_test_env(tmp_path, sample_dataframe):
    """Complete test environment for pipeline tests.
    
    Combines multiple fixtures into a ready-to-use test environment.
    """
    # Create directory structure
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create input file
    input_file = input_dir / "data.csv"
    sample_dataframe.to_csv(input_file, index=False)
    
    # Return environment info
    return {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "input_file": input_file,
        "sample_data": sample_dataframe,
    }


# ============================================================================
# Fixtures for Mocking
# ============================================================================

@pytest.fixture
def mock_api_response():
    """Mock API response for testing API clients."""
    from unittest.mock import Mock
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {"id": 1, "name": "Test"}
    }
    return mock_response


@pytest.fixture
def mock_database_connection(monkeypatch):
    """Mock database connection.
    
    Uses monkeypatch to replace database calls with mocks.
    """
    from unittest.mock import MagicMock
    
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
    mock_conn.cursor.return_value = mock_cursor
    
    return mock_conn


# ============================================================================
# Fixtures for Testing Exceptions
# ============================================================================

@pytest.fixture
def invalid_dataframe():
    """DataFrame that should trigger validation errors."""
    return pd.DataFrame({
        "id": [1, 2, None],  # Contains null
        "value": ["a", "b", "c"]  # Wrong type
    })


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture
def cleanup_files():
    """Track files created during test and clean them up.
    
    Use when tests create files outside tmp_path.
    """
    created_files = []
    
    def track_file(filepath: Path):
        created_files.append(filepath)
        return filepath
    
    yield track_file
    
    # Cleanup
    for filepath in created_files:
        if filepath.exists():
            if filepath.is_file():
                filepath.unlink()
            elif filepath.is_dir():
                shutil.rmtree(filepath)


# ============================================================================
# Usage Examples in Tests
# ============================================================================

"""
Example test file using these fixtures:

# test_my_module.py
import pytest
import pandas as pd

def test_with_sample_data(sample_dataframe):
    '''Uses sample_dataframe fixture.'''
    assert len(sample_dataframe) == 3
    assert "id" in sample_dataframe.columns

def test_with_temp_file(sample_csv_file):
    '''Uses sample_csv_file fixture.'''
    df = pd.read_csv(sample_csv_file)
    assert not df.empty

@pytest.mark.unit
def test_fast_unit(sample_dataframe):
    '''Marked as unit test.'''
    result = sample_dataframe["value"].sum()
    assert result == 60

@pytest.mark.integration
def test_full_pipeline(pipeline_test_env):
    '''Uses composite fixture for integration test.'''
    env = pipeline_test_env
    assert env["input_file"].exists()
    assert env["output_dir"].exists()

def test_multiple_formats(file_format):
    '''Runs once for each format in parametrized fixture.'''
    assert file_format in ["csv", "parquet", "json"]

def test_with_cleanup(cleanup_files, tmp_path):
    '''Uses cleanup fixture to track created files.'''
    test_file = cleanup_files(tmp_path / "test.txt")
    test_file.write_text("test data")
    assert test_file.exists()
    # File cleaned up automatically after test
"""
