# Context Usage Patterns & Best Practices

## ✅ Best Practices

### 1. Always Use Explicit Dependencies

**Good:**
```python
def transform(ctx: Context) -> pd.DataFrame:
    """Transform that explicitly declares context dependency."""
    input_data = ctx.get('raw_data')
    return input_data.copy()
```

**Bad:**
```python
# Global state - avoid!
GLOBAL_DATA = {}

def transform():
    return GLOBAL_DATA['raw_data']
```

**Why:** Explicit dependencies make testing easier, enable parallel execution, and clarify data flow.

---

### 2. Check Existence Before Access

**Good:**
```python
def optional_transform(ctx: Context) -> pd.DataFrame:
    if ctx.has('enrichment_data'):
        extra = ctx.get('enrichment_data')
        return base.merge(extra, how='left')
    return base
```

**Bad:**
```python
def optional_transform(ctx: Context) -> pd.DataFrame:
    try:
        extra = ctx.get('enrichment_data')
        # ...
    except KeyError:
        pass  # Silently fails
```

**Why:** `has()` is explicit intent, not exception-based control flow.

---

### 3. Clear Context in Tests

**Good:**
```python
@pytest.fixture
def context():
    ctx = PandasContext()
    yield ctx
    ctx.clear()  # Cleanup
```

**Bad:**
```python
# Shared context across tests
ctx = PandasContext()

def test_one():
    ctx.register('data', df1)
    # ...

def test_two():
    # Depends on test_one's state!
    data = ctx.get('data')
```

**Why:** Test isolation prevents flaky tests and order dependencies.

---

### 4. Use Descriptive Names

**Good:**
```python
ctx.register('customer_orders_enriched', result)
ctx.register('dim_customers', customers)
```

**Bad:**
```python
ctx.register('df', result)
ctx.register('data1', customers)
```

**Why:** Descriptive names make pipelines self-documenting.

---

### 5. Register Outputs, Not Intermediate Steps

**Good:**
```python
def process_orders(ctx: Context) -> pd.DataFrame:
    raw = ctx.get('raw_orders')
    cleaned = clean(raw)
    validated = validate(cleaned)
    enriched = enrich(validated)
    
    # Only register final result
    ctx.register('processed_orders', enriched)
    return enriched
```

**Bad:**
```python
def process_orders(ctx: Context) -> pd.DataFrame:
    raw = ctx.get('raw_orders')
    
    cleaned = clean(raw)
    ctx.register('orders_cleaned', cleaned)  # Too many!
    
    validated = validate(cleaned)
    ctx.register('orders_validated', validated)
    
    enriched = enrich(validated)
    ctx.register('orders_enriched', enriched)
    
    return enriched
```

**Why:** Context should hold pipeline outputs, not every intermediate step. Reduces memory and naming overhead.

**Exception:** Register intermediates if needed by multiple downstream nodes.

---

## 🚫 Anti-Patterns

### 1. Mutating Retrieved DataFrames

**Problem:**
```python
def bad_transform(ctx: Context) -> pd.DataFrame:
    df = ctx.get('customers')
    df['new_col'] = 0  # Mutates context data!
    return df
```

**Solution:**
```python
def good_transform(ctx: Context) -> pd.DataFrame:
    df = ctx.get('customers').copy()  # Always copy!
    df['new_col'] = 0
    return df
```

**Why:** Mutations create hidden side effects and break idempotency.

---

### 2. Context as Global State

**Problem:**
```python
# Module-level context
CONTEXT = PandasContext()

def node_a():
    df = load_data()
    CONTEXT.register('data', df)

def node_b():
    return CONTEXT.get('data')
```

**Solution:**
```python
def node_a(ctx: Context):
    df = load_data()
    ctx.register('data', df)
    return df

def node_b(ctx: Context):
    return ctx.get('data')
```

**Why:** Passing context as parameter enables testing and parallelism.

---

### 3. Forgetting to Clear in Long-Running Processes

**Problem:**
```python
ctx = PandasContext()

for batch in batches:
    process_batch(ctx, batch)  # Context grows indefinitely!
```

**Solution:**
```python
for batch in batches:
    ctx = PandasContext()  # Fresh context per batch
    process_batch(ctx, batch)
    ctx.clear()
```

**Why:** Prevents memory leaks in long-running jobs.

---

### 4. Returning Context Instead of DataFrame

**Problem:**
```python
def transform(ctx: Context) -> Context:
    df = ctx.get('input')
    result = df.transform()
    ctx.register('output', result)
    return ctx  # Wrong!
```

**Solution:**
```python
def transform(ctx: Context) -> pd.DataFrame:
    df = ctx.get('input')
    result = df.transform()
    ctx.register('output', result)
    return result  # Explicit return
```

**Why:** Functions should return data, not mutate and return context.

---

## 🏗️ Architectural Patterns

### Pattern 1: Context Manager for Auto-Cleanup

```python
from contextlib import contextmanager

@contextmanager
def pipeline_context(engine='pandas', spark_session=None):
    ctx = create_context(engine, spark_session)
    try:
        yield ctx
    finally:
        ctx.clear()

# Usage
with pipeline_context() as ctx:
    run_pipeline(ctx)
# Automatically cleaned
```

---

### Pattern 2: Context Factory for Tests

```python
def make_test_context(**datasets):
    """Create context pre-populated with test data."""
    ctx = PandasContext()
    for name, df in datasets.items():
        ctx.register(name, df)
    return ctx

# Usage
def test_transform():
    ctx = make_test_context(
        customers=pd.DataFrame({'id': [1, 2]}),
        orders=pd.DataFrame({'order_id': [101, 102]})
    )
    result = transform(ctx)
    assert len(result) == 2
```

---

### Pattern 3: Read-Only Context Wrapper

```python
class ReadOnlyContext(Context):
    """Prevent modifications to context."""
    
    def __init__(self, ctx: Context):
        self._ctx = ctx
    
    def register(self, name: str, df: Any) -> None:
        raise RuntimeError("Context is read-only")
    
    def get(self, name: str) -> Any:
        return self._ctx.get(name)
    
    def has(self, name: str) -> bool:
        return self._ctx.has(name)
    
    def list_names(self) -> list[str]:
        return self._ctx.list_names()
    
    def clear(self) -> None:
        raise RuntimeError("Context is read-only")

# Usage: Prevent downstream nodes from polluting context
readonly = ReadOnlyContext(ctx)
untrusted_transform(readonly)
```

---

### Pattern 4: Validation Layer

```python
class ValidatedPipeline:
    """Pipeline with context validation."""
    
    def __init__(self, required_inputs: list[str]):
        self.required_inputs = required_inputs
    
    def validate_context(self, ctx: Context) -> None:
        missing = [name for name in self.required_inputs if not ctx.has(name)]
        if missing:
            raise ValueError(f"Missing required inputs: {missing}")
    
    def run(self, ctx: Context) -> pd.DataFrame:
        self.validate_context(ctx)
        # Run pipeline...
```

---

## 🧪 Testing Strategies

### Strategy 1: Fixture-Based Isolation

```python
import pytest

@pytest.fixture
def fresh_context():
    ctx = PandasContext()
    yield ctx
    ctx.clear()

def test_transform(fresh_context):
    fresh_context.register('input', test_data)
    result = transform(fresh_context)
    assert result is not None
```

---

### Strategy 2: Parameterized Contexts

```python
@pytest.fixture(params=['pandas', 'spark'])
def context(request):
    """Test with both Pandas and Spark contexts."""
    if request.param == 'pandas':
        ctx = PandasContext()
    else:
        ctx = SparkContext(spark_session)
    yield ctx
    ctx.clear()
```

---

### Strategy 3: Mock Context for Unit Tests

```python
class MockContext(Context):
    """Lightweight context for fast tests."""
    
    def __init__(self, data: dict):
        self._data = data
    
    def get(self, name: str):
        return self._data[name]
    
    def has(self, name: str) -> bool:
        return name in self._data
    
    # ... minimal implementation

# Usage
def test_fast():
    ctx = MockContext({'input': test_df})
    result = transform(ctx)
    assert len(result) > 0
```

---

## 📊 Performance Considerations

### 1. Memory Management

**Problem:** Large DataFrames accumulate in context

**Solutions:**
- Register only final outputs
- Use `clear()` between pipeline stages
- Consider `CachingContext` with LRU eviction for long pipelines

---

### 2. DataFrame Copying

**Trade-off:** `.copy()` prevents mutations but uses memory

**Guideline:**
- Copy when modifying data
- Don't copy for read-only operations
- For Spark, copying is lazy (no overhead)

---

### 3. Context Size Limits

**For large pipelines:**
```python
ctx = CachingContext(max_size=20)  # Auto-evict old entries
```

**For batch processing:**
```python
for batch in batches:
    ctx = PandasContext()  # Fresh context per batch
    process(ctx, batch)
    ctx.clear()
```

---

## 🔍 Debugging Tips

### 1. Log Context Operations

```python
class LoggingContext(PandasContext):
    def register(self, name: str, df: pd.DataFrame) -> None:
        logger.info(f"Registering '{name}' ({len(df)} rows)")
        super().register(name, df)
    
    def get(self, name: str) -> pd.DataFrame:
        logger.info(f"Accessing '{name}'")
        return super().get(name)
```

---

### 2. Inspect Context State

```python
def debug_context(ctx: Context):
    print("Context contents:")
    for name in ctx.list_names():
        df = ctx.get(name)
        print(f"  {name}: {len(df)} rows, {list(df.columns)}")
```

---

### 3. Validate Context Expectations

```python
def assert_context_has(ctx: Context, *names):
    """Helper for tests."""
    for name in names:
        assert ctx.has(name), f"Context missing '{name}'"
```

---

## 📚 Summary

| Pattern | When to Use |
|---------|-------------|
| Explicit dependencies | Always pass `ctx: Context` parameter |
| `has()` before `get()` | For optional dependencies |
| `.copy()` | When modifying DataFrames |
| `clear()` | After pipeline runs, in test teardown |
| Context managers | Long-running or production pipelines |
| Read-only wrappers | Prevent pollution from untrusted code |
| Validation layer | Ensure required inputs exist |
| Fresh fixtures | Every test gets isolated context |

**Golden Rule:** Context is for **explicit data passing**, not global state.
