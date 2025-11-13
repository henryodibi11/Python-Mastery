# Abstractions Deep Dive: ABC, Protocol, and Duck Typing Explained

## Why Abstractions Matter (The Real Reason)

**Problem:** You're building a data pipeline framework that needs to support multiple engines (Pandas, Spark, Polars).

**Without abstractions:**
```python
def read_data(engine_name, path):
    if engine_name == "pandas":
        return pd.read_csv(path)
    elif engine_name == "spark":
        return spark.read.csv(path)
    elif engine_name == "polars":
        return pl.read_csv(path)
    # What about Dask? DuckDB? Modin?
    # Every new engine = modify this function!
```

**With abstractions:**
```python
class Engine(ABC):
    @abstractmethod
    def read_csv(self, path): ...

def read_data(engine: Engine, path):
    return engine.read_csv(path)
    # Works with ANY engine! Add new ones without changing this code!
```

---

## The Three Abstraction Patterns

Python gives you three ways to achieve polymorphism (same interface, different implementations):

### 1. Duck Typing (The Python Way)
**Philosophy:** "If it walks like a duck and quacks like a duck, it's a duck"

```python
# No inheritance needed!
class CSVReader:
    def read(self, path):
        return pd.read_csv(path)

class JSONReader:
    def read(self, path):
        return pd.read_json(path)

# Works with anything that has a read() method
def load_data(reader, path):
    return reader.read(path)

load_data(CSVReader(), "data.csv")   # Works!
load_data(JSONReader(), "data.json") # Works!
load_data("not a reader", "data")     # Runtime error!
```

**Pros:**
- ✅ Flexible, Pythonic
- ✅ Works with any object (even external libraries)
- ✅ No boilerplate

**Cons:**
- ❌ No compile-time checks (typos discovered at runtime)
- ❌ No IDE autocomplete
- ❌ Hard to know what methods are required

**When to use:** Quick scripts, prototypes, working with external types

---

### 2. Protocol (Structural Typing)
**Philosophy:** "Define the shape, not the inheritance"

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Readable(Protocol):
    """Anything with a read() method is Readable"""
    def read(self, path: str) -> pd.DataFrame: ...

class CSVReader:  # No inheritance needed!
    def read(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)

def load_data(reader: Readable, path: str):
    return reader.read(path)

# Type checker validates CSVReader has read() method
# Runtime check also works:
assert isinstance(CSVReader(), Readable)  # True!
```

**Pros:**
- ✅ Type checking without inheritance
- ✅ Works with external types
- ✅ IDE autocomplete
- ✅ Flexible

**Cons:**
- ❌ Runtime checks need `@runtime_checkable`
- ❌ Less explicit than ABC
- ❌ Can't enforce implementation (no `NotImplementedError`)

**When to use:** 
- Working with external libraries (file-like objects, database connections)
- Want type safety without forcing inheritance
- Public APIs where users might pass their own implementations

---

### 3. ABC (Abstract Base Classes)
**Philosophy:** "Explicit contract enforced at class definition time"

```python
from abc import ABC, abstractmethod

class Engine(ABC):
    @abstractmethod
    def read_csv(self, path: str) -> pd.DataFrame:
        """Read CSV file into DataFrame"""
        pass
    
    @abstractmethod
    def write_csv(self, df: pd.DataFrame, path: str):
        """Write DataFrame to CSV"""
        pass

# ❌ Can't instantiate abstract class
# engine = Engine()  # TypeError!

class PandasEngine(Engine):
    def read_csv(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)
    
    def write_csv(self, df: pd.DataFrame, path: str):
        df.to_csv(path, index=False)

# ✅ All abstract methods implemented
engine = PandasEngine()  # Works!
```

**Pros:**
- ✅ Enforced contract (can't forget methods)
- ✅ Clear documentation of required methods
- ✅ Fails fast (at class definition, not at runtime)
- ✅ IDE support
- ✅ Can provide default implementations

**Cons:**
- ❌ Requires inheritance
- ❌ More boilerplate
- ❌ Can't work with external types without wrappers

**When to use:**
- Internal framework code (you control the implementations)
- Need strict contracts (data pipeline engines, plugin systems)
- Want to provide default behavior
- Building a library used by others

---

## When to Use Which?

| Use Case | Best Choice | Why |
|----------|-------------|-----|
| Internal framework with multiple implementations | **ABC** | Strict contract, catch errors early |
| Working with file-like objects | **Protocol** | External types, structural typing |
| Quick prototype | **Duck Typing** | Fast, flexible |
| Public API | **ABC** or **Protocol** | Clear expectations |
| Testing with mocks | **Protocol** or **Duck Typing** | Easy to fake |
| Plugin system | **ABC** | Enforced interface |

---

## Deep Dive: ABC Features

### Abstract Properties
```python
class DataSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Data source name (must be implemented)"""
        pass
    
    @property
    @abstractmethod
    def schema(self) -> dict:
        """Data schema (must be implemented)"""
        pass

class CSVSource(DataSource):
    @property
    def name(self) -> str:
        return "CSV"
    
    @property
    def schema(self) -> dict:
        return {"type": "csv", "columns": []}
```

### Abstract Class Methods
```python
class Engine(ABC):
    @classmethod
    @abstractmethod
    def from_config(cls, config: dict):
        """Factory method (must be implemented)"""
        pass

class PandasEngine(Engine):
    @classmethod
    def from_config(cls, config: dict):
        return cls(**config)
```

### Default Implementations
```python
class Engine(ABC):
    @abstractmethod
    def read(self, path: str):
        """Must be implemented"""
        pass
    
    def read_with_retry(self, path: str, retries: int = 3):
        """Default implementation (can be overridden)"""
        for attempt in range(retries):
            try:
                return self.read(path)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{retries}")
```

### Multiple Abstract Methods
```python
class FullEngine(ABC):
    @abstractmethod
    def read(self, path): ...
    
    @abstractmethod
    def write(self, df, path): ...
    
    @abstractmethod
    def transform(self, df): ...

# Must implement ALL three to instantiate!
```

---

## Deep Dive: Protocol Features

### Runtime Checkable Protocols
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class FileHandler:
    def close(self):
        print("Closing file")

handler = FileHandler()
assert isinstance(handler, Closeable)  # True!

# Without @runtime_checkable, isinstance doesn't work
```

### Protocol with Multiple Methods
```python
@runtime_checkable
class DataReader(Protocol):
    def read(self, path: str) -> pd.DataFrame: ...
    def get_schema(self) -> dict: ...
    def close(self) -> None: ...

# Any class with these three methods satisfies the protocol
```

### Generic Protocols
```python
from typing import Protocol, TypeVar, Generic

T = TypeVar('T')

class Readable(Protocol, Generic[T]):
    def read(self, path: str) -> T: ...

class CSVReader:
    def read(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)

# Type checker knows read() returns pd.DataFrame
reader: Readable[pd.DataFrame] = CSVReader()
```

---

## Common Patterns

### Pattern 1: Strategy Pattern with ABC
```python
class CompressionStrategy(ABC):
    @abstractmethod
    def compress(self, data: bytes) -> bytes: ...
    
    @abstractmethod
    def decompress(self, data: bytes) -> bytes: ...

class GzipCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        import gzip
        return gzip.compress(data)
    
    def decompress(self, data: bytes) -> bytes:
        import gzip
        return gzip.decompress(data)

class ZstdCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        import zstandard
        return zstandard.compress(data)
    
    def decompress(self, data: bytes) -> bytes:
        import zstandard
        return zstandard.decompress(data)

# Use anywhere:
def save_compressed(data: bytes, strategy: CompressionStrategy):
    compressed = strategy.compress(data)
    # ... save to file
```

### Pattern 2: Adapter Pattern
```python
# External library you can't modify
class ThirdPartyDB:
    def query(self, sql):
        return [{"data": "..."}]

# Your engine interface
class Engine(ABC):
    @abstractmethod
    def read(self, query: str) -> pd.DataFrame: ...

# Adapter: makes ThirdPartyDB work with your interface
class ThirdPartyDBAdapter(Engine):
    def __init__(self, db: ThirdPartyDB):
        self.db = db
    
    def read(self, query: str) -> pd.DataFrame:
        result = self.db.query(query)
        return pd.DataFrame(result)

# Now it works with your code!
db = ThirdPartyDB()
engine = ThirdPartyDBAdapter(db)
df = engine.read("SELECT * FROM users")
```

### Pattern 3: Template Method
```python
class DataPipeline(ABC):
    def run(self):
        """Template method: defines the algorithm structure"""
        self.extract()
        self.transform()
        self.load()
        self.cleanup()
    
    @abstractmethod
    def extract(self): ...
    
    @abstractmethod
    def transform(self): ...
    
    @abstractmethod
    def load(self): ...
    
    def cleanup(self):
        """Default implementation (can be overridden)"""
        print("Cleaning up...")

class CSVPipeline(DataPipeline):
    def extract(self):
        self.data = pd.read_csv("input.csv")
    
    def transform(self):
        self.data = self.data[self.data['amount'] > 0]
    
    def load(self):
        self.data.to_csv("output.csv", index=False)
```

---

## Combining ABC + Protocol

Sometimes you want both!

```python
# Protocol for external users (flexible)
@runtime_checkable
class Readable(Protocol):
    def read(self, path: str) -> pd.DataFrame: ...

# ABC for internal implementations (strict)
class InternalReader(ABC):
    @abstractmethod
    def read(self, path: str) -> pd.DataFrame: ...
    
    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool: ...

# Function accepts anything Readable (including external types)
def load_data(reader: Readable, path: str) -> pd.DataFrame:
    return reader.read(path)

# Internal implementations must follow stricter contract
class CSVReader(InternalReader):
    def read(self, path: str) -> pd.DataFrame:
        return pd.read_csv(path)
    
    def validate(self, df: pd.DataFrame) -> bool:
        return not df.empty
```

---

## Testing with Abstractions

### Mocking Abstract Classes
```python
class Engine(ABC):
    @abstractmethod
    def read(self, path: str) -> pd.DataFrame: ...

# In tests:
class FakeEngine(Engine):
    def read(self, path: str) -> pd.DataFrame:
        return pd.DataFrame({"test": [1, 2, 3]})

def test_pipeline():
    engine = FakeEngine()
    result = run_pipeline(engine)
    assert len(result) == 3
```

### Protocol-based Mocking
```python
@runtime_checkable
class Readable(Protocol):
    def read(self, path: str) -> pd.DataFrame: ...

def test_with_mock():
    from unittest.mock import Mock
    
    mock_reader = Mock(spec=Readable)
    mock_reader.read.return_value = pd.DataFrame({"test": [1, 2]})
    
    result = load_data(mock_reader, "fake.csv")
    assert len(result) == 2
    mock_reader.read.assert_called_once_with("fake.csv")
```

---

## Common Mistakes

### Mistake 1: Forgetting @abstractmethod
```python
# ❌ BAD: No @abstractmethod
class Engine(ABC):
    def read(self, path):
        pass  # Subclasses can forget to implement!

# ✅ GOOD: Use @abstractmethod
class Engine(ABC):
    @abstractmethod
    def read(self, path):
        pass  # Subclasses MUST implement
```

### Mistake 2: Calling super().__init__() on ABC
```python
# ❌ Unnecessary
class PandasEngine(Engine):
    def __init__(self):
        super().__init__()  # ABC has no __init__ to call

# ✅ Only call super() if base class has __init__
class PandasEngine(Engine):
    def __init__(self):
        # No super() needed for plain ABC
        self.name = "pandas"
```

### Mistake 3: Over-abstracting
```python
# ❌ Too many abstractions
class Readable(ABC):
    @abstractmethod
    def read(self): ...

class Writable(ABC):
    @abstractmethod
    def write(self): ...

class Closeable(ABC):
    @abstractmethod
    def close(self): ...

class FileHandler(Readable, Writable, Closeable):  # Complex!
    ...

# ✅ Start simple
class FileHandler(ABC):
    @abstractmethod
    def read(self): ...
    
    @abstractmethod
    def write(self): ...
    
    @abstractmethod
    def close(self): ...
```

### Mistake 4: Making Everything Abstract
```python
# ❌ BAD: Utils don't need abstractions
class StringUtils(ABC):  # Why?!
    @abstractmethod
    def upper(self, s: str) -> str: ...

# ✅ GOOD: Just use functions or concrete classes
def upper(s: str) -> str:
    return s.upper()
```

---

## Real-World Example: Odibi Engine System

```python
# odibi/core/engine.py
class Engine(ABC):
    """Base engine for all data processing backends"""
    
    @abstractmethod
    def read(self, source: Source) -> DataFrame:
        """Read data from source"""
        pass
    
    @abstractmethod
    def write(self, df: DataFrame, destination: Destination):
        """Write data to destination"""
        pass
    
    @abstractmethod
    def transform(self, df: DataFrame, operation: Operation) -> DataFrame:
        """Apply transformation"""
        pass
    
    def run_pipeline(self, pipeline: Pipeline):
        """Template method (same for all engines)"""
        df = self.read(pipeline.source)
        for operation in pipeline.operations:
            df = self.transform(df, operation)
        self.write(df, pipeline.destination)

# odibi/engines/pandas.py
class PandasEngine(Engine):
    def read(self, source):
        if source.format == "csv":
            return pd.read_csv(source.path)
        elif source.format == "parquet":
            return pd.read_parquet(source.path)
    
    def write(self, df, destination):
        if destination.format == "csv":
            df.to_csv(destination.path, index=False)
        elif destination.format == "parquet":
            df.to_parquet(destination.path)
    
    def transform(self, df, operation):
        # Pandas-specific implementation
        ...

# odibi/engines/spark.py
class SparkEngine(Engine):
    def read(self, source):
        if source.format == "csv":
            return self.spark.read.csv(source.path)
        elif source.format == "parquet":
            return self.spark.read.parquet(source.path)
    
    def write(self, df, destination):
        if destination.format == "csv":
            df.write.csv(destination.path)
        elif destination.format == "parquet":
            df.write.parquet(destination.path)
    
    def transform(self, df, operation):
        # Spark-specific implementation
        ...

# User code works with ANY engine!
def run_job(engine: Engine, pipeline: Pipeline):
    engine.run_pipeline(pipeline)

# Swap engines without changing code
run_job(PandasEngine(), my_pipeline)  # Small data
run_job(SparkEngine(), my_pipeline)   # Big data
```

---

## Summary

| Pattern | Inheritance Required | Type Checking | Runtime Check | Best For |
|---------|---------------------|---------------|---------------|----------|
| **Duck Typing** | No | No | No | Prototypes, external types |
| **Protocol** | No | Yes | Optional | Flexible interfaces, external types |
| **ABC** | Yes | Yes | Yes | Strict contracts, internal code |

**Mental Model:**
- **Duck Typing** = "Hope it works" (runtime discovery)
- **Protocol** = "Check the shape" (structural typing)
- **ABC** = "Enforce the contract" (explicit inheritance)

**Rule of Thumb:**
1. Start with **duck typing** for prototypes
2. Add **Protocol** when you need type hints
3. Use **ABC** when building a framework with strict contracts

The key is knowing when each tool is appropriate, not using one everywhere!
