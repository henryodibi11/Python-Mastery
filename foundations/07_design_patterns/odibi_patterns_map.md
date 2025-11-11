# Odibi Patterns Map

Comprehensive mapping of design patterns in the Odibi framework.

## Registry Pattern

### Transform Registry
**Location**: Core transform management  
**Purpose**: Register and discover data transformations  
**Implementation**:
```python
@TransformRegistry.register("my_transform")
def custom_transform(df, **kwargs):
    return df
```

**Key Files**:
- Transform registration decorators
- Dynamic transform discovery
- Plugin system for custom transforms

### Function Registry
**Location**: UDF management  
**Purpose**: Register custom functions for use in expressions  
**Benefits**:
- Extend framework without modifying core
- Discoverable at runtime
- Version and manage custom logic

### Connector Registry
**Location**: Data source/sink management  
**Purpose**: Register different data source adapters  
**Examples**:
- PostgreSQL connector
- Snowflake connector
- S3 connector
- Delta Lake connector

## Factory Pattern

### `create_context()`
**Location**: Main entry point  
**Purpose**: Create execution context based on configuration  
**Signature**:
```python
def create_context(engine: str, **config) -> ExecutionContext:
    if engine == "spark":
        return SparkContext(**config)
    elif engine == "pandas":
        return PandasContext(**config)
    elif engine == "polars":
        return PolarsContext(**config)
```

**Benefits**:
- Hides complex initialization
- Provides consistent interface
- Supports multiple backends

### Connection Factory
**Location**: Connection management  
**Purpose**: Create database/storage connections  
**Implementation**:
```python
ConnectionFactory.create("postgres", host="...", database="...")
ConnectionFactory.create("snowflake", account="...", warehouse="...")
```

### Engine Factory
**Location**: Execution engine creation  
**Purpose**: Instantiate appropriate compute engine  
**Variants**:
- Spark engine (distributed)
- Pandas engine (single-node)
- Polars engine (fast single-node)
- Dask engine (distributed Python)

## Strategy Pattern

### Execution Engines
**Location**: Core execution layer  
**Interface**: Common operations (filter, join, aggregate, etc.)  
**Implementations**:
- `SparkEngine`: Uses PySpark
- `PandasEngine`: Uses pandas
- `PolarsEngine`: Uses Polars

**Benefits**:
- Write once, run on any engine
- Switch engines via config
- Test with lightweight engine, deploy with production engine

### Serialization Strategies
**Location**: Data I/O layer  
**Interface**: Read/write operations  
**Implementations**:
- `ParquetSerializer`: Columnar format
- `CSVSerializer`: Text format
- `JSONSerializer`: Structured text
- `DeltaSerializer`: Delta Lake format

### Validation Strategies
**Location**: Data quality layer  
**Interface**: Validate data against rules  
**Implementations**:
- `SchemaValidator`: Check schema matches
- `RangeValidator`: Check values in range
- `UniquenessValidator`: Check uniqueness constraints
- `CustomValidator`: User-defined rules

## Builder Pattern

### Config Builder
**Location**: Configuration management  
**Purpose**: Fluently construct complex configs  
**Example**:
```python
config = (
    ConfigBuilder()
    .with_source("postgres://...")
    .with_target("s3://...")
    .add_transform("clean_data")
    .add_transform("enrich_data")
    .with_validation(enabled=True)
    .build()
)
```

### Query Builder
**Location**: SQL/query generation  
**Purpose**: Programmatically build queries  
**Example**:
```python
query = (
    QueryBuilder()
    .select("user_id", "COUNT(*) as order_count")
    .from_table("orders")
    .where("status = 'completed'")
    .group_by("user_id")
    .build()
)
```

### Pipeline Builder
**Location**: Pipeline construction  
**Purpose**: Chain transforms into pipeline  
**Example**:
```python
pipeline = (
    PipelineBuilder()
    .source("users_table")
    .transform("filter_active")
    .transform("enrich_with_orders")
    .sink("analytics_db")
    .build()
)
```

## Dependency Injection

### Context Injection
**Location**: Throughout framework  
**Purpose**: Pass execution context to components  
**Pattern**:
```python
class Transform:
    def __init__(self, context: ExecutionContext):
        self.context = context
    
    def execute(self, df):
        # Use context for operations
        return self.context.engine.filter(df, "age > 25")
```

**Benefits**:
- Clear dependencies
- Easy to test (inject mocks)
- Flexible composition

### Config Injection
**Location**: Component initialization  
**Purpose**: Pass configuration to components  
**Example**:
```python
class DataLoader:
    def __init__(self, config: LoaderConfig):
        self.config = config
    
    def load(self):
        return read_table(
            self.config.table_name,
            partitions=self.config.partitions
        )
```

### Connection Injection
**Location**: Data access layer  
**Purpose**: Pass connections to readers/writers  
**Example**:
```python
class PostgresReader:
    def __init__(self, connection: Connection):
        self.connection = connection
    
    def read(self, query: str):
        return self.connection.execute(query)
```

## Adapter Pattern

### Engine Adapters
**Location**: Engine abstraction layer  
**Purpose**: Adapt different engines to common interface  
**Implementation**:
```python
class EngineAdapter(ABC):
    @abstractmethod
    def filter(self, df, condition): pass
    
    @abstractmethod
    def join(self, left, right, on): pass

class SparkAdapter(EngineAdapter):
    def filter(self, df, condition):
        return df.filter(condition)  # PySpark API

class PandasAdapter(EngineAdapter):
    def filter(self, df, condition):
        return df.query(condition)  # Pandas API
```

### Storage Adapters
**Location**: Storage layer  
**Purpose**: Adapt different storage systems  
**Examples**:
- S3 adapter
- HDFS adapter
- Local filesystem adapter
- Azure Blob adapter

## Decorator Pattern

### Transform Decorators
**Location**: Transform enhancement  
**Purpose**: Add functionality to transforms  
**Examples**:
```python
@cache_result
@validate_schema
@log_execution
def my_transform(df):
    return df.transform(...)
```

**Common Decorators**:
- `@cache_result`: Cache transform output
- `@validate_schema`: Validate input/output schema
- `@log_execution`: Log execution time and status
- `@retry`: Retry on failure
- `@parallel`: Execute in parallel

## Observer Pattern

### Event System
**Location**: Event management  
**Purpose**: Notify components of events  
**Events**:
- Pipeline started
- Transform completed
- Data validated
- Error occurred

**Usage**:
```python
context.on("transform_complete", lambda event: log(event))
context.on("error", lambda event: alert(event))
```

## Template Method Pattern

### Base Transform
**Location**: Transform base class  
**Purpose**: Define transform execution template  
**Structure**:
```python
class BaseTransform(ABC):
    def execute(self, df):
        self._validate_input(df)
        result = self._apply(df)
        self._validate_output(result)
        return result
    
    @abstractmethod
    def _apply(self, df):
        pass
```

## Chain of Responsibility

### Validation Chain
**Location**: Data quality  
**Purpose**: Chain validators together  
**Example**:
```python
validation_chain = (
    SchemaValidator()
    .set_next(RangeValidator())
    .set_next(UniquenessValidator())
)
validation_chain.validate(df)
```

## Composite Pattern

### Transform Composition
**Location**: Complex transforms  
**Purpose**: Compose transforms into trees  
**Example**:
```python
class CompositeTransform(Transform):
    def __init__(self, transforms: list[Transform]):
        self.transforms = transforms
    
    def apply(self, df):
        result = df
        for transform in self.transforms:
            result = transform.apply(result)
        return result
```

## Summary Table

| Pattern | Frequency | Primary Use | Key Benefit |
|---------|-----------|-------------|-------------|
| Registry | High | Component discovery | Extensibility |
| Factory | High | Object creation | Abstraction |
| Strategy | High | Swappable algorithms | Flexibility |
| Builder | Medium | Config construction | Readability |
| Dependency Injection | High | Dependency management | Testability |
| Adapter | Medium | Interface translation | Integration |
| Decorator | Medium | Feature enhancement | Composition |
| Observer | Low | Event handling | Decoupling |
| Template Method | Medium | Algorithm structure | Consistency |
| Chain of Responsibility | Low | Sequential processing | Flexibility |
| Composite | Low | Hierarchical structures | Simplification |
| Singleton | Avoid | Global state | (Anti-pattern) |

## Pattern Selection Guide

### When to use each pattern:

**Registry**:
- ✅ Need to discover components at runtime
- ✅ Want plugins/extensions
- ✅ Components added dynamically

**Factory**:
- ✅ Complex object creation
- ✅ Multiple implementations of interface
- ✅ Hide implementation details

**Strategy**:
- ✅ Multiple algorithms for same task
- ✅ Runtime algorithm selection
- ✅ Isolate algorithm logic

**Builder**:
- ✅ Complex object construction
- ✅ Many optional parameters
- ✅ Want fluent API

**Dependency Injection**:
- ✅ Always (default choice!)
- ✅ Need testability
- ✅ Want flexibility

**Avoid Singleton**:
- ❌ Makes testing hard
- ❌ Creates hidden dependencies
- ❌ Global state issues
- ✅ Use DI instead

## References

- Gang of Four Design Patterns
- Martin Fowler's Patterns of Enterprise Application Architecture
- Odibi codebase examples
