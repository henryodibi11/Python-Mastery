# 🧪 Pytest Fundamentals

Master professional testing with pytest - the framework used in production codebases like Odibi (416 tests).

## 📚 What You'll Learn

1. **Pytest Basics** - Assertions, test discovery, running tests
2. **Fixtures** - Setup/teardown, scope, autouse, `tmp_path`
3. **Parametrize** - Data-driven tests with multiple inputs
4. **Mocking** - Isolate dependencies with `monkeypatch`
5. **Coverage** - Measure test completeness with `pytest-cov`
6. **Markers** - Organize and filter tests
7. **Testing Exceptions** - Validate error handling
8. **Odibi Patterns** - Real-world testing patterns from a production framework

## 🎯 Learning Outcomes

After completing this lesson, you will:

- Write comprehensive test suites for Python projects
- Use fixtures to manage test data and setup
- Parametrize tests to reduce duplication
- Mock external dependencies for isolated testing
- Measure and improve code coverage
- Organize large test suites with markers and conftest.py
- Apply professional testing patterns from real codebases

## 📁 Files

- **lesson.ipynb** - Complete tutorial with runnable examples
- **exercises.ipynb** - Practice problems to solidify learning
- **solutions.ipynb** - Solutions with explanations
- **conftest_example.py** - Example shared fixtures configuration
- **odibi_test_analysis.md** - Deep dive into Odibi's 416 test architecture

## 🚀 Quick Start

```bash
# Install dependencies
pip install pytest pytest-cov pytest-mock pandas

# Open lesson
jupyter notebook lesson.ipynb

# Run example tests (from lesson)
pytest test_basic.py -v
pytest test_fixtures.py -v --cov=math_utils
pytest -m "unit"  # Run only unit tests
```

## 📊 Odibi Test Statistics

The Odibi framework has **416 tests** organized as:

- **Unit tests** (15 files in `tests/unit/`) - Test individual components
- **Integration tests** (1 file in `tests/integration/`) - Test component interactions  
- **Top-level tests** (11 files in `tests/`) - Core functionality tests

**Coverage**: ~85%
**Execution time**: 5-10 seconds
**Test-to-code ratio**: ~1.2:1

## 🗺️ Lesson Structure

### Part 1: Pytest Basics (15 min)
- Test discovery and naming conventions
- Assertions and comparisons
- Running tests with pytest CLI

### Part 2: Fixtures (20 min)
- Setup and teardown
- Fixture scopes (function, class, module, session)
- Built-in fixtures (`tmp_path`, `monkeypatch`, etc.)

### Part 3: Parametrize (15 min)
- Data-driven testing
- Multiple parameters
- Named test IDs

### Part 4: Mocking (25 min)
- `monkeypatch` for dependencies
- Mocking environment variables
- Mocking file systems and APIs

### Part 5: Coverage (15 min)
- Running coverage reports
- Interpreting coverage metrics
- Finding untested code paths

### Part 6: Markers & conftest.py (15 min)
- Custom markers for test organization
- Shared fixtures in conftest.py
- Marker-based test filtering

### Part 7: Testing Exceptions (10 min)
- `pytest.raises()` context manager
- Matching exception messages
- Inspecting exception details

### Part 8: Odibi Analysis (20 min)
- Class-based test organization
- Parametrize for multiple scenarios
- Handling optional dependencies
- Integration test patterns

### Build Project (30 min)
- Create complete test suite for mini data pipeline
- Unit, integration, and parametrized tests
- Achieve 90%+ coverage

## 💡 Key Pytest Commands

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run specific file
pytest test_file.py

# Run specific test
pytest test_file.py::test_function

# Run tests matching pattern
pytest -k "test_add"

# Run with markers
pytest -m "unit"                # Only unit tests
pytest -m "not slow"            # Exclude slow tests

# Coverage
pytest --cov=mymodule                     # Basic coverage
pytest --cov=mymodule --cov-report=term-missing  # Show missing lines
pytest --cov=mymodule --cov-report=html          # HTML report

# Debug options
pytest -s              # Show print statements
pytest -x              # Stop on first failure
pytest --pdb           # Drop into debugger on failure
pytest --lf            # Run last failed tests
pytest --ff            # Run failures first, then rest

# Performance
pytest -n auto         # Run tests in parallel (requires pytest-xdist)
pytest --durations=10  # Show 10 slowest tests
```

## 🎓 Testing Best Practices

### Test Naming
- **Files**: `test_*.py` or `*_test.py`
- **Functions**: `test_*()` - descriptive names
- **Classes**: `Test*` - group related tests

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Component interaction tests
├── fixtures/       # Test data files
├── conftest.py     # Shared fixtures
└── test_*.py       # Feature-specific tests
```

### Writing Good Tests
1. **Arrange** - Set up test data
2. **Act** - Execute code under test
3. **Assert** - Verify results

```python
def test_add_column():
    # Arrange
    df = pd.DataFrame({"a": [1, 2]})
    
    # Act
    result = add_column(df, "b", 10)
    
    # Assert
    assert "b" in result.columns
    assert list(result["b"]) == [10, 10]
```

### Test Independence
- Each test should run independently
- Use fixtures for setup, not global state
- Clean up resources in teardown

### Coverage Goals
- **Minimum**: 70% for production code
- **Target**: 80-90% for critical paths
- **Not 100%**: Diminishing returns, hard to maintain

## 🔗 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Real Python - Pytest Guide](https://realpython.com/pytest-python-testing/)
- [Pytest Cheat Sheet](https://gist.github.com/kwmiebach/3fd49612ef7a52b5ce3a)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## 🏆 Exercises Preview

1. **Basic Tests** - Write tests for string utilities
2. **Fixtures** - Create reusable test data fixtures
3. **Parametrize** - Test function with multiple inputs
4. **Mocking** - Mock API calls and file I/O
5. **Coverage** - Achieve 90%+ coverage on given module
6. **Integration** - Build test suite for mini ETL pipeline
7. **Odibi Style** - Refactor tests using Odibi patterns

## 📈 Next Steps

After mastering pytest:
1. **Advanced Pytest** - Plugins, async testing, benchmarking
2. **Property-Based Testing** - Hypothesis library
3. **TDD Workshop** - Test-driven development patterns
4. **CI/CD Integration** - Automated testing in pipelines

---

**Time to complete**: 2-3 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Python basics, functions, classes
