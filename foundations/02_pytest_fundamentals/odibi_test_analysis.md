# 🔍 Odibi Test Architecture Analysis

Deep dive into how Odibi's **416 tests** are organized and what patterns we can learn from them.

## 📊 Test Distribution

### Directory Structure

```
tests/
├── unit/                       # 15 test files
│   ├── test_azure_sql.py
│   ├── test_cli.py
│   ├── test_cli_story.py
│   ├── test_doc_story.py
│   ├── test_explanation.py
│   ├── test_linting.py
│   ├── test_module_structure.py
│   ├── test_operations.py
│   ├── test_registry.py
│   ├── test_story_metadata.py
│   ├── test_story_renderers.py
│   ├── test_templates.py
│   ├── test_themes.py
│   ├── test_transformation_context.py
│   └── __init__.py
├── integration/                # 1 test file
│   ├── test_cli_integration.py
│   └── __init__.py
├── fixtures/                   # Test data
│   ├── sample_data.csv
│   └── __init__.py
├── test_azure_adls_auth.py    # Azure authentication tests
├── test_config.py             # Configuration/Pydantic validation
├── test_connections_paths.py  # Connection string builders
├── test_context.py            # Execution context
├── test_delta_pandas.py       # Delta Lake integration
├── test_extras_imports.py     # Optional dependency handling
├── test_graph.py              # DAG/dependency graph
├── test_pandas_engine_full_coverage.py  # Data engine tests
├── test_pipeline.py           # Pipeline execution
├── test_registry.py           # Function registry
├── test_setup_helpers.py      # Setup utilities
└── __init__.py
```

### Test Categories

| Category | Files | Purpose | Examples |
|----------|-------|---------|----------|
| **Unit** | 15 files | Test individual components | Registry, operations, CLI parsing |
| **Integration** | 1 file | Test component interactions | Full CLI workflow |
| **Top-level** | 11 files | Core functionality | Pipeline, config, connections |
| **Fixtures** | Data files | Test data | sample_data.csv |

**Total**: ~27 test files with **416 individual tests**

## 🏗️ Key Testing Patterns

### 1. Class-Based Organization

**Example from `test_config.py`:**

```python
class TestReadConfig:
    """Test ReadConfig validation."""
    
    def test_valid_read_config_with_path(self):
        """Valid config with path should parse correctly."""
        config = ReadConfig(connection="local", format="csv", path="data/input.csv")
        assert config.connection == "local"
        assert config.format == "csv"
    
    def test_read_config_requires_path_or_table(self):
        """Config must have either path or table."""
        with pytest.raises(ValidationError) as exc_info:
            ReadConfig(connection="local", format="csv")
        assert "Either 'table' or 'path' must be provided" in str(exc_info.value)

class TestWriteConfig:
    """Test WriteConfig validation."""
    
    def test_valid_write_config(self):
        # ...
```

**Benefits**:
- Groups related tests logically
- Clear test organization
- Easy to find specific tests
- Can use `setup_method()` and `teardown_method()`

### 2. Setup/Teardown with Methods

**Example from `test_pipeline.py`:**

```python
class TestPipelineExecution:
    """Test basic pipeline execution."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temp directory
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test data
        test_data = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        test_data.to_csv(self.test_path / "input.csv", index=False)
        
        # Clear registry
        FunctionRegistry._functions.clear()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_simple_read_only_pipeline(self):
        # Test uses self.test_path
        # ...
```

**Benefits**:
- Automatic resource cleanup
- Consistent test environment
- No test pollution
- Clear lifecycle management

### 3. Parametrize for Multiple Scenarios

**Example from `test_pandas_engine_full_coverage.py`:**

```python
@pytest.mark.parametrize(
    "format,options,expected",
    [
        ("csv", {"delimiter": ","}, "PandasEngine"),
        ("parquet", {"engine": "pyarrow"}, "PandasEngine"),
        ("json", {"orient": "records"}, "PandasEngine"),
    ],
)
def test_read_formats(format, options, expected):
    """Test reading different formats."""
    # Test implementation
```

**Benefits**:
- Reduces code duplication
- Tests multiple scenarios
- Easy to add new cases
- Clear test coverage

### 4. Handling Optional Dependencies

**Example from `test_extras_imports.py`:**

```python
@pytest.mark.extras
def test_spark_engine_import_without_pyspark(monkeypatch):
    """Test graceful handling when PySpark not installed."""
    # Hide pyspark module
    import sys
    monkeypatch.setitem(sys.modules, "pyspark", None)
    
    # Should raise friendly error, not crash
    with pytest.raises(ImportError, match="PySpark not installed"):
        from odibi.engines import SparkEngine

@pytest.mark.extras
@pytest.mark.skipif("pyspark" not in sys.modules, reason="PySpark not installed")
def test_spark_engine_import_with_pyspark():
    """Test when PySpark IS available."""
    from odibi.engines import SparkEngine
    assert SparkEngine is not None
```

**Benefits**:
- Tests work with/without optional deps
- Clear marking of extra tests
- Can skip when dependency missing
- Tests graceful degradation

### 5. Custom Markers for Organization

**Common markers in Odibi:**

```python
@pytest.mark.extras        # Tests for optional features
@pytest.mark.skip          # Known issues or WIP
@pytest.mark.skipif        # Conditional skipping
```

**Usage:**

```bash
# Run only core tests (skip extras)
pytest -m "not extras"

# Run only integration tests
pytest tests/integration/ -v

# Skip slow tests
pytest -m "not slow"
```

### 6. Platform-Specific Tests

**Example from `test_cli_integration.py`:**

```python
@pytest.mark.skip(reason="Subprocess crashes on Windows - covered by unit tests")
def test_cli_generate_with_subprocess():
    """Test CLI project generation via subprocess."""
    # This test uses subprocess.run() which has issues on Windows
    # Core functionality still tested via unit tests
```

**Benefits**:
- Tests work across platforms
- Clear documentation of limitations
- Alternative testing approaches for platform issues

### 7. Fixture-Based Test Data

**Example from `test_delta_pandas.py`:**

```python
@pytest.fixture
def sample_dataframe():
    """Provide sample DataFrame for tests."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "value": [10, 20, 30],
        "category": ["A", "B", "A"]
    })

@pytest.fixture
def temp_delta_path(tmp_path):
    """Provide temporary Delta Lake path."""
    delta_path = tmp_path / "delta_table"
    yield delta_path
    # Cleanup handled by tmp_path

def test_write_delta_table(sample_dataframe, temp_delta_path):
    """Test writing to Delta Lake."""
    write_deltalake(temp_delta_path, sample_dataframe)
    assert temp_delta_path.exists()
```

## 📈 Test Coverage Strategy

### What Gets Tested

1. **Configuration Validation** (test_config.py)
   - Pydantic schema validation
   - Required fields
   - Default values
   - Enum constraints

2. **Core Pipeline** (test_pipeline.py)
   - Read operations
   - Transform execution
   - Write operations
   - Full pipeline workflow

3. **Registries** (test_registry.py)
   - Function registration
   - Duplicate prevention
   - Metadata storage
   - Retrieval

4. **Connections** (test_connections_paths.py)
   - Connection string building
   - Azure ADLS URIs
   - SQL connection strings
   - Path resolution

5. **Data Engines** (test_pandas_engine_full_coverage.py)
   - Format reading (CSV, Parquet, JSON)
   - Format writing
   - Engine selection
   - Error handling

6. **CLI** (test_cli.py, test_cli_integration.py)
   - Argument parsing
   - Command execution
   - Project generation
   - End-to-end workflows

### What's NOT Tested (and Why)

1. **External APIs** - Mocked instead
2. **Platform-specific subprocess** - Skipped on Windows
3. **Some edge cases** - Marked with `@pytest.mark.skip` for future work

## 🎯 Key Takeaways for Your Tests

### 1. Organize by Feature, Not File

```python
# Good: Organized by what's being tested
class TestReadConfig:
    def test_valid_config(self): ...
    def test_missing_required_field(self): ...
    def test_invalid_format(self): ...

class TestWriteConfig:
    def test_valid_config(self): ...
    def test_default_mode(self): ...
```

### 2. Use Fixtures for Common Data

```python
@pytest.fixture
def sample_df():
    """Reusable test DataFrame."""
    return pd.DataFrame({"id": [1, 2, 3]})

def test_transform_1(sample_df):
    # Use fixture
    
def test_transform_2(sample_df):
    # Reuse same fixture
```

### 3. Parametrize for Variations

```python
@pytest.mark.parametrize("format,engine", [
    ("csv", "pandas"),
    ("parquet", "pandas"),
    ("delta", "deltalake"),
])
def test_read_formats(format, engine):
    # One test, multiple scenarios
```

### 4. Setup/Teardown for Resources

```python
class TestWithResources:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir)
    
    def test_uses_temp_dir(self):
        # self.temp_dir available and cleaned up
```

### 5. Mark Tests for Organization

```python
@pytest.mark.unit
def test_fast_unit(): ...

@pytest.mark.integration  
def test_slow_integration(): ...

@pytest.mark.skipif(condition, reason="...")
def test_conditional(): ...
```

## 📊 Metrics & Best Practices

### Odibi's Test Metrics

- **Total tests**: 416
- **Execution time**: 5-10 seconds
- **Coverage**: ~85%
- **Test-to-code ratio**: ~1.2:1
- **Average tests per file**: ~15-20

### Recommended Structure

```
your_project/
├── src/
│   └── your_module/
│       ├── __init__.py
│       ├── pipeline.py
│       ├── config.py
│       └── transforms.py
└── tests/
    ├── unit/
    │   ├── test_config.py
    │   ├── test_transforms.py
    │   └── __init__.py
    ├── integration/
    │   ├── test_pipeline.py
    │   └── __init__.py
    ├── fixtures/
    │   ├── sample_data.csv
    │   └── __init__.py
    ├── conftest.py          # Shared fixtures
    └── pytest.ini           # Pytest config
```

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    extras: Tests for optional features

addopts =
    -v
    --strict-markers
    --cov=src
    --cov-report=term-missing
```

## 🚀 Applying Odibi Patterns

### Example: Testing a Data Pipeline

```python
# test_my_pipeline.py
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from my_pipeline import Pipeline, read_csv, transform, write_csv

class TestPipeline:
    """Test pipeline execution."""
    
    def setup_method(self):
        """Create test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Setup test data
        self.sample_df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
        self.sample_df.to_csv(self.test_path / "input.csv", index=False)
    
    def teardown_method(self):
        """Cleanup test environment."""
        shutil.rmtree(self.test_dir)
    
    @pytest.mark.unit
    def test_read_csv(self):
        """Test CSV reading."""
        df = read_csv(self.test_path / "input.csv")
        assert len(df) == 3
        assert "id" in df.columns
    
    @pytest.mark.unit
    @pytest.mark.parametrize("transform_func,expected_columns", [
        (lambda df: df.assign(total=df["value"] * 2), ["id", "value", "total"]),
        (lambda df: df.assign(label="A"), ["id", "value", "label"]),
    ])
    def test_transforms(self, transform_func, expected_columns):
        """Test various transforms."""
        df = self.sample_df.copy()
        result = transform_func(df)
        assert list(result.columns) == expected_columns
    
    @pytest.mark.integration
    def test_full_pipeline(self):
        """Test complete pipeline workflow."""
        pipeline = Pipeline()
        pipeline.add_step("read", read_csv, self.test_path / "input.csv")
        pipeline.add_step("transform", lambda df: df.assign(doubled=df["value"] * 2))
        pipeline.add_step("write", write_csv, self.test_path / "output.csv")
        
        pipeline.run()
        
        # Verify output
        output = pd.read_csv(self.test_path / "output.csv")
        assert "doubled" in output.columns
        assert list(output["doubled"]) == [20, 40, 60]
```

## 🎓 Summary

### Key Patterns from Odibi

1. ✅ **Class-based organization** - Group related tests
2. ✅ **Setup/teardown methods** - Manage test lifecycle
3. ✅ **Parametrize extensively** - Test multiple scenarios
4. ✅ **Custom markers** - Organize test categories
5. ✅ **Fixtures for data** - Reusable test inputs
6. ✅ **Handle optional deps** - Graceful degradation
7. ✅ **Platform awareness** - Skip platform-specific tests
8. ✅ **Integration separation** - Unit vs integration tests

### What Makes Good Tests

- **Fast**: Run in seconds, not minutes
- **Isolated**: Each test independent
- **Reliable**: Same result every time
- **Readable**: Clear what's being tested
- **Maintainable**: Easy to update when code changes

### Next Steps

1. Apply these patterns to your code
2. Aim for 80-90% coverage
3. Organize tests by feature
4. Use markers for test categories
5. Write tests as you code, not after
