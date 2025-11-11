# Odibi's Abstraction Architecture

Deep dive into how Odibi uses ABC to enable multi-engine extensibility.

## Overview

Odibi is a data processing library that supports multiple execution engines (Pandas, Spark). Its architecture uses Abstract Base Classes to define contracts that each engine must implement.

## Three Core Abstractions

### 1. Engine (`odibi/engine/base.py`)

**Purpose**: Define a complete contract for data processing engines.

**Pattern**: ABC with 9 abstract methods

```python
class Engine(ABC):
    @abstractmethod
    def read(self, connection, format, table=None, path=None, options=None) -> Any: ...
    
    @abstractmethod
    def write(self, df, connection, format, table=None, path=None, mode="overwrite", options=None) -> None: ...
    
    @abstractmethod
    def execute_sql(self, sql: str, context: Context) -> Any: ...
    
    @abstractmethod
    def execute_operation(self, operation: str, params: dict, df: Any) -> Any: ...
    
    @abstractmethod
    def get_schema(self, df: Any) -> list[str]: ...
    
    @abstractmethod
    def get_shape(self, df: Any) -> tuple: ...
    
    @abstractmethod
    def count_rows(self, df: Any) -> int: ...
    
    @abstractmethod
    def count_nulls(self, df: Any, columns: list[str]) -> dict[str, int]: ...
    
    @abstractmethod
    def validate_schema(self, df: Any, schema_rules: dict) -> list[str]: ...
```

**Design Decisions**:

1. **Return Type `Any`**: Pandas returns `pd.DataFrame`, Spark returns `pyspark.sql.DataFrame`. The abstraction doesn't force a single type.

2. **Optional Parameters**: `table` OR `path` depending on source type (SQL vs files)

3. **Context Passing**: `execute_sql()` receives Context to access registered DataFrames

4. **Metadata Methods**: `get_schema`, `get_shape`, `count_rows` for introspection

5. **Validation**: `validate_schema()` returns list of errors (empty = valid)

**Why ABC instead of Protocol?**
- ✅ Odibi controls implementations (PandasEngine, SparkEngine)
- ✅ Forces complete implementation (can't forget methods)
- ✅ Clear documentation of required interface
- ✅ Prevents partial implementations

### 2. Connection (`odibi/connections/base.py`)

**Purpose**: Abstract how to resolve paths/tables across different storage systems.

**Pattern**: Minimal ABC with 2 methods

```python
class BaseConnection(ABC):
    @abstractmethod
    def get_path(self, relative_path: str) -> str:
        """Resolve relative path to full path."""
        pass
    
    @abstractmethod
    def validate(self) -> None:
        """Validate connection configuration."""
        pass
```

**Why So Minimal?**

Different connection types have vastly different needs:
- **FileConnection**: Just needs `base_directory`
- **DatabaseConnection**: Needs `host`, `port`, `credentials`, connection pooling
- **CloudConnection**: Needs `auth_tokens`, `bucket`, `region`

The abstraction only defines what **all** connections must provide:
1. Path resolution (`get_path`)
2. Configuration validation (`validate`)

**Concrete Implementations**:

```python
# FileConnection
def get_path(self, relative_path: str) -> str:
    return str(Path(self.base_directory) / relative_path)

# DatabaseConnection
def get_path(self, relative_path: str) -> str:
    return f"{self.schema}.{relative_path}"  # Returns qualified table name

# S3Connection
def get_path(self, relative_path: str) -> str:
    return f"s3://{self.bucket}/{self.prefix}/{relative_path}"
```

Same method, completely different implementations!

### 3. Context (`odibi/context.py`)

**Purpose**: Manage DataFrames shared between pipeline steps (e.g., for SQL queries).

**Pattern**: ABC with 5 methods + concrete implementations

```python
class Context(ABC):
    @abstractmethod
    def register(self, name: str, df: Any) -> None: ...
    
    @abstractmethod
    def get(self, name: str) -> Any: ...
    
    @abstractmethod
    def has(self, name: str) -> bool: ...
    
    @abstractmethod
    def list_names(self) -> list[str]: ...
    
    @abstractmethod
    def clear(self) -> None: ...
```

**Why Context Matters**:

When executing SQL like `SELECT * FROM sales JOIN customers ON ...`, engines need to find the `sales` and `customers` DataFrames by name.

**Implementation Difference**:

#### PandasContext
Stores DataFrames in an in-memory dictionary:

```python
class PandasContext(Context):
    def __init__(self):
        self._data: dict[str, pd.DataFrame] = {}
    
    def register(self, name: str, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas.DataFrame, got {type(df)}")
        self._data[name] = df
    
    def get(self, name: str) -> pd.DataFrame:
        if name not in self._data:
            raise KeyError(f"DataFrame '{name}' not found")
        return self._data[name]
```

SQL execution (using DuckDB):
```python
import duckdb
duckdb.query("SELECT * FROM sales", context._data)
```

#### SparkContext
Uses Spark's catalog with temporary views:

```python
class SparkContext(Context):
    def __init__(self, spark_session):
        self.spark = spark_session
        self._registered_views: set[str] = set()
    
    def register(self, name: str, df):
        df.createOrReplaceTempView(name)  # Register in Spark catalog
        self._registered_views.add(name)
    
    def get(self, name: str):
        if name not in self._registered_views:
            raise KeyError(f"DataFrame '{name}' not found")
        return self.spark.table(name)  # Retrieve from catalog
```

SQL execution:
```python
spark.sql("SELECT * FROM sales")  # Uses temp view
```

**Same interface, completely different storage!**

## How It All Works Together

### Example Pipeline

```python
# 1. User writes engine-agnostic code
config = {
    "connection": FileConnection(base_directory="./data"),
    "engine": "pandas",  # or "spark"
    "source": {"format": "csv", "path": "sales.csv"}
}

# 2. Factory creates appropriate engine
engine = create_engine(config["engine"])  # Returns PandasEngine or SparkEngine

# 3. Engine uses abstraction methods
context = create_context(config["engine"])
df = engine.read(connection=config["connection"], format="csv", path="sales.csv")
context.register("sales", df)

# 4. Execute SQL query
result = engine.execute_sql("SELECT * FROM sales WHERE amount > 1000", context)
```

### What Happens Under the Hood

**With PandasEngine**:
```python
def execute_sql(self, sql: str, context: PandasContext):
    import duckdb
    return duckdb.query(sql, context._data).to_df()  # Query dict of DataFrames
```

**With SparkEngine**:
```python
def execute_sql(self, sql: str, context: SparkContext):
    return context.spark.sql(sql)  # Query Spark catalog
```

**User code doesn't change!** The abstraction handles the differences.

## Key Design Patterns

### 1. Dependency Inversion
High-level pipeline code depends on `Engine` abstraction, not `PandasEngine` or `SparkEngine` directly.

### 2. Factory Pattern
```python
def create_engine(engine_type: str) -> Engine:
    if engine_type == "pandas":
        return PandasEngine()
    elif engine_type == "spark":
        return SparkEngine()
```

### 3. Strategy Pattern
Different engines are strategies for the same operations (read, write, execute_sql).

### 4. Type Variance
`Engine.read()` returns `Any` because concrete types differ:
- PandasEngine → `pd.DataFrame`
- SparkEngine → `pyspark.sql.DataFrame`

### 5. Error Handling
Abstract methods define what errors to raise:
```python
def get(self, name: str) -> Any:
    """Raises: KeyError if name not found"""
```

Both implementations honor this contract.

## Benefits of This Architecture

### 1. **Add New Engines Without Modifying Existing Code**
Want to add DuckDBEngine? Just implement the `Engine` ABC:
```python
class DuckDBEngine(Engine):
    def read(self, connection, format, ...): ...
    def write(self, df, connection, ...): ...
    # ... implement all 9 methods
```

No changes to pipeline code needed!

### 2. **Compile-Time Safety**
```python
class IncompleteEngine(Engine):
    def read(self, ...): ...
    # Missing other methods
```
**Result**: `TypeError: Can't instantiate abstract class IncompleteEngine with abstract methods write, execute_sql, ...`

### 3. **Testability**
```python
class MockEngine(Engine):
    def read(self, ...): return pd.DataFrame({"a": [1, 2, 3]})
    def write(self, ...): pass
    # ... minimal implementations for testing
```

Test pipelines without real Spark clusters!

### 4. **Documentation**
The ABC serves as documentation of the complete engine contract. New contributors know exactly what to implement.

### 5. **Swappable at Runtime**
```python
# Dev: Use Pandas
engine = PandasEngine()

# Prod: Use Spark
engine = SparkEngine()

# Same pipeline code works with both!
```

## When to Use This Pattern

Use ABC when:
- ✅ You control both interface AND implementations
- ✅ Need compile-time enforcement
- ✅ Want clear contracts for contributors
- ✅ Building plugin/extensible architecture

Don't use ABC when:
- ❌ Working with external types (use Protocol)
- ❌ Need structural typing (use Protocol)
- ❌ Interfaces frequently change (too rigid)
- ❌ Simple one-off abstractions (duck typing ok)

## Further Reading

1. **Odibi Source Code**:
   - Engine implementations: `odibi/engine/pandas_engine.py`, `odibi/engine/spark_engine.py`
   - Connection types: `odibi/connections/file.py`, `odibi/connections/database.py`
   - Context usage: `odibi/nodes/sql_node.py`

2. **Design Patterns**:
   - Strategy Pattern
   - Factory Pattern
   - Dependency Inversion Principle (SOLID)

3. **Python ABC Documentation**:
   - https://docs.python.org/3/library/abc.html
