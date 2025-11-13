"""
Shared test fixtures and configuration.

conftest.py is a special pytest file that:
1. Shares fixtures across multiple test files
2. Automatically discovered by pytest (no imports needed)
3. Can be placed at any level (project root or subdirectory)
4. Fixtures are available to all tests in the same directory and below

Example structure:
  project/
    conftest.py          # Root-level fixtures (available everywhere)
    tests/
      unit/
        conftest.py      # Unit test fixtures only
        test_calc.py     # Uses fixtures from both conftest.py files
      integration/
        test_api.py
"""

import pandas as pd
import pytest
from pathlib import Path


# Sample data fixtures
@pytest.fixture
def sample_df():
    """Sample DataFrame for testing data operations."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10, 20, 30],
        "category": ["A", "B", "A"]
    })


@pytest.fixture
def sample_csv(tmp_path, sample_df):
    """Sample CSV file in temporary directory."""
    csv_path = tmp_path / "data.csv"
    sample_df.to_csv(csv_path, index=False)
    return csv_path


# Environment fixtures
@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("DEBUG", "true")
    return monkeypatch


# Helper functions (not fixtures, just shared utilities)
def assert_dataframes_equal(df1, df2, **kwargs):
    """Helper to compare DataFrames with better error messages."""
    pd.testing.assert_frame_equal(
        df1, 
        df2,
        check_dtype=True,
        check_names=True,
        **kwargs
    )
