# Pytest Deep Dive: Concepts Explained

This guide provides detailed explanations of pytest concepts that might be confusing when you first encounter them.

## Table of Contents
1. [Assert Rewriting](#assert-rewriting)
2. [Fixture Scopes](#fixture-scopes)
3. [Monkeypatch vs Mock](#monkeypatch-vs-mock)
4. [Coverage Types](#coverage-types)
5. [Test Organization](#test-organization)
6. [Common Pitfalls](#common-pitfalls)

---

## Assert Rewriting

**What is it?**
Pytest intercepts and "rewrites" assert statements to provide detailed failure messages.

**Example:**
```python
def test_example():
    x = [1, 2, 3]
    assert x == [1, 2, 4]
```

**Output with pytest:**
```
AssertionError: assert [1, 2, 3] == [1, 2, 4]
  At index 2 diff: 3 != 4
```

**Output with plain Python assert:**
```
AssertionError  (no details!)
```

**Why it matters:** You get automatic, detailed diffs without writing custom error messages.

**How to use:** Just use plain `assert` statements in tests. Pytest handles the rest.

---

## Fixture Scopes

Fixtures can have different lifetimes:

### Function Scope (default)
```python
@pytest.fixture  # or @pytest.fixture(scope="function")
def fresh_data():
    return [1, 2, 3]
```
- **Created:** Before each test function
- **Destroyed:** After each test function  
- **Use when:** Tests need isolated data (most common)
- **Pro:** Perfect test isolation
- **Con:** Slower if setup is expensive

### Class Scope
```python
@pytest.fixture(scope="class")
def shared_db():
    db = Database()
    db.connect()
    yield db
    db.disconnect()
```
- **Created:** Before first test in class
- **Destroyed:** After last test in class
- **Use when:** Tests in a class can share state
- **Pro:** Faster than function scope
- **Con:** Tests can leak state between each other

### Module Scope
```python
@pytest.fixture(scope="module")
def spark_session():
    spark = SparkSession.builder.getOrCreate()
    yield spark
    spark.stop()
```
- **Created:** Before first test in file
- **Destroyed:** After last test in file
- **Use when:** Setup is expensive (Spark, database connection pool)
- **Pro:** Much faster
- **Con:** All tests in file share the object

### Session Scope
```python
@pytest.fixture(scope="session")
def test_database():
    db = create_test_database()
    yield db
    drop_test_database(db)
```
- **Created:** Before any test runs
- **Destroyed:** After all tests complete
- **Use when:** Extremely expensive setup (test database, docker containers)
- **Pro:** Maximum speed
- **Con:** Highest risk of state leakage

**Rule of Thumb:** Start with function scope. Only use wider scopes when tests are slow and you understand the risks.

---

## Monkeypatch vs Mock

Both replace objects in tests, but in different ways:

### Monkeypatch (pytest fixture)
```python
def test_env_var(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    # Automatic cleanup after test
```

**Use for:**
- Environment variables
- Module-level functions
- Dictionary items
- Object attributes

**Pros:**
- Simple syntax
- Automatic cleanup
- Part of pytest (no extra install)

**Cons:**
- Less control than Mock
- Can't inspect calls

### unittest.mock (stdlib)
```python
from unittest.mock import Mock, patch

def test_api_call():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}
        result = fetch_data()
        mock_get.assert_called_once_with("https://api.example.com")
```

**Use for:**
- Tracking function calls
- Complex return values
- Side effects
- Multiple calls

**Pros:**
- Track call count, arguments
- Complex behaviors
- Powerful assertions

**Cons:**
- More complex syntax
- Manual cleanup (or use `with`)

### pytest-mock (plugin)
```python
def test_with_mocker(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"data": "test"}
    # Automatic cleanup
```

**Best of both worlds:**
- Mock's power + pytest's automatic cleanup
- Requires: `pip install pytest-mock`

---

## Coverage Types

### Line Coverage
```python
def divide(a, b):
    if b == 0:          # Line 1: Executed ✅
        return None     # Line 2: NOT executed ❌
    return a / b        # Line 3: Executed ✅
    
# Test only calls divide(10, 2)
# Line coverage: 66% (2/3 lines)
```

### Branch Coverage
```python
def divide(a, b):
    if b == 0:          # Branch 1: True ❌ | Branch 2: False ✅
        return None
    return a / b

# Test only calls divide(10, 2)
# Branch coverage: 50% (1/2 branches)
```

**Line coverage** measures which lines executed.
**Branch coverage** measures which paths (if/else) taken.

**Why it matters:** 100% line coverage can still miss bugs!

```python
def withdraw(amount, balance):
    if amount > balance:  # Line covered ✅
        raise ValueError("Insufficient funds")  
    return balance - amount  # Line covered ✅

# Test: withdraw(50, 100) 
# Line coverage: 100% ✅
# Branch coverage: 50% ❌ (never tested the error path!)
```

**What to aim for:**
- Production code: 80-90% line coverage
- Critical code: 100% branch coverage
- Don't obsess over 100% (diminishing returns)

---

## Test Organization

### Directory Structure (Recommended)
```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── calc.py
│       └── api.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── unit/
│   │   ├── conftest.py      # Unit-specific fixtures
│   │   ├── test_calc.py
│   │   └── test_api.py
│   ├── integration/
│   │   └── test_full_pipeline.py
│   └── fixtures/
│       └── sample_data.csv
├── pytest.ini
└── pyproject.toml
```

### Naming Conventions
- **Test files:** `test_*.py` or `*_test.py`
- **Test functions:** `def test_*()`
- **Test classes:** `class Test*` (no `__init__` method)
- **Fixtures:** Descriptive names (`sample_df`, not `df`)

### Import Patterns
```python
# ✅ GOOD: Explicit imports
from myapp.calc import add, subtract

def test_add():
    assert add(2, 3) == 5

# ❌ BAD: Star imports
from myapp.calc import *  # Which functions exist?
```

---

## Common Pitfalls

### 1. Shared Mutable State
```python
# ❌ BAD: List defined at module level
TEST_DATA = [1, 2, 3]

def test_append():
    TEST_DATA.append(4)
    assert len(TEST_DATA) == 4  # Passes

def test_len():
    assert len(TEST_DATA) == 3  # FAILS! Data still has 4

# ✅ GOOD: Fresh data per test
@pytest.fixture
def test_data():
    return [1, 2, 3]

def test_append(test_data):
    test_data.append(4)
    assert len(test_data) == 4
```

### 2. Testing Implementation Instead of Behavior
```python
# ❌ BAD: Testing internal details
def test_cache_uses_dict():
    cache = Cache()
    assert isinstance(cache._storage, dict)  # Breaks if we switch to OrderedDict

# ✅ GOOD: Testing behavior
def test_cache_stores_and_retrieves():
    cache = Cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"
```

### 3. Not Cleaning Up After Tests
```python
# ❌ BAD: Leaves files around
def test_write_file():
    with open("test.txt", "w") as f:
        f.write("test")
    assert Path("test.txt").exists()
    # File left on disk!

# ✅ GOOD: Use tmp_path
def test_write_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("test")
    assert file_path.exists()
    # Auto-cleaned up
```

### 4. Flaky Tests (Random Failures)
```python
# ❌ BAD: Time-dependent test
import time

def test_timing():
    start = time.time()
    do_something()
    duration = time.time() - start
    assert duration < 1.0  # Sometimes passes, sometimes fails

# ✅ GOOD: Mock time or use tolerances
def test_timing(monkeypatch):
    times = [0, 0.5]
    monkeypatch.setattr(time, "time", lambda: times.pop(0))
    # ... test with deterministic time
```

### 5. Testing Too Much in One Test
```python
# ❌ BAD: One test, many assertions
def test_user_workflow():
    user = create_user()
    user.login()
    user.update_profile()
    user.make_purchase()
    user.logout()
    # If login fails, we never test the rest

# ✅ GOOD: Separate tests
def test_create_user():
    user = create_user()
    assert user.id is not None

def test_login(user):
    assert user.login() == True

def test_update_profile(logged_in_user):
    assert logged_in_user.update_profile(name="Alice") == True
```

---

## Quick Reference

### Running Tests
```bash
# All tests
pytest

# Specific file
pytest tests/test_calc.py

# Specific test
pytest tests/test_calc.py::test_add

# Pattern match
pytest -k "add or subtract"

# Markers
pytest -m "unit"
pytest -m "not slow"

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Verbose
pytest -v

# Very verbose
pytest -vv

# Coverage
pytest --cov=myapp --cov-report=html
```

### Useful Fixtures
```python
tmp_path          # Temporary directory
monkeypatch       # Mock/patch objects
capsys           # Capture stdout/stderr
caplog           # Capture log messages  
request          # Test metadata
mocker           # unittest.mock wrapper (requires pytest-mock)
```

### Markers
```python
@pytest.mark.skip                           # Skip unconditionally
@pytest.mark.skipif(sys.platform == "win32") # Conditional skip
@pytest.mark.xfail                          # Expected to fail
@pytest.mark.parametrize                    # Multiple inputs
@pytest.mark.slow                           # Custom marker
```

---

## When to Google vs Ask

**Google for:**
- Specific error messages
- pytest plugin recommendations
- Advanced patterns (async, benchmarks, property-based testing)

**Ask for help when:**
- Your tests are flaky
- You're not sure what to test
- Coverage is low but you don't know what's missing
- Tests are slow
- You're repeating lots of code

Remember: Good tests make code changes **safe and fast**. Bad tests make them **scary and slow**.
