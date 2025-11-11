# Engine Comparison Reference

## Overview

This document provides a side-by-side comparison of Odibi's engine implementations.

## Engine Architecture Comparison

| Aspect | PandasEngine | SparkEngine | DuckDBEngine (Exercise) |
|--------|--------------|-------------|-------------------------|
| **Execution Model** | Eager, in-memory | Lazy, distributed | Eager, in-process columnar |
| **Primary Use Case** | Small-medium datasets (<10GB) | Large datasets (>100GB) | Medium datasets, analytics |
| **Memory Model** | All data in RAM | Spill to disk, cluster | Memory-mapped, efficient |
| **Parallelism** | Single-threaded (default) | Multi-node cluster | Multi-threaded (single node) |
| **SQL Engine** | DuckDB or pandasql | Spark SQL | Native DuckDB SQL |
| **Installation** | `pip install pandas` | `pip install pyspark` | `pip install duckdb` |

## Method-by-Method Comparison

### read()

#### PandasEngine
```python
if format == "csv":
    return pd.read_csv(full_path, **merged_options)
elif format == "parquet":
    return pd.read_parquet(full_path, **merged_options)
elif format == "delta":
    dt = DeltaTable(full_path, storage_options=storage_opts)
    return dt.to_pandas()
```

**Characteristics:**
- Direct file I/O
- Loads entire file into memory
- Uses `storage_options` for cloud access (ADLS, S3)
- Delta support via `deltalake` library

#### SparkEngine
```python
reader = self.spark.read.format(format)
for key, value in options.items():
    reader = reader.option(key, value)
return reader.load(full_path)
```

**Characteristics:**
- Lazy evaluation (doesn't read until action)
- Can read partitioned data efficiently
- Native Delta Lake support
- Credentials configured at SparkSession level

#### DuckDBEngine (Target)
```python
if format == "csv":
    return self.conn.execute(f"SELECT * FROM read_csv_auto('{full_path}')").df()
elif format == "parquet":
    return self.conn.execute(f"SELECT * FROM read_parquet('{full_path}')").df()
```

**Characteristics:**
- Uses DuckDB's optimized readers
- Returns Pandas DataFrame (zero-copy when possible)
- Auto-detection of schemas
- Efficient columnar storage

---

### write()

#### PandasEngine
```python
if format == "csv":
    mode_param = "w" if mode == "overwrite" else "a"
    df.to_csv(full_path, mode=mode_param, index=False, **merged_options)
elif format == "parquet":
    df.to_parquet(full_path, index=False, **merged_options)
```

**Characteristics:**
- Immediate write to disk
- CSV supports append mode
- Parquet overwrites only (library limitation)

#### SparkEngine
```python
writer = df.write.format(format).mode(mode)
if partition_by:
    writer = writer.partitionBy(*partition_by)
writer.save(full_path)
```

**Characteristics:**
- Writes partitioned data efficiently
- Supports all write modes (overwrite, append, error, ignore)
- Can write to multiple files in parallel

---

### execute_sql()

#### PandasEngine
```python
try:
    import duckdb
    conn = duckdb.connect(":memory:")
    for name in context.list_names():
        conn.register(name, context.get(name))
    return conn.execute(sql).df()
except ImportError:
    from pandasql import sqldf
    return sqldf(sql, locals_dict)
```

**Characteristics:**
- Prefers DuckDB (fast, feature-rich)
- Fallback to pandasql (pure Python, slower)
- Converts DataFrames to SQL tables

#### SparkEngine
```python
for table_name, df in context.items():
    df.createOrReplaceTempView(table_name)
return self.spark.sql(sql)
```

**Characteristics:**
- Uses Spark SQL (Catalyst optimizer)
- Operates on Spark DataFrames natively
- Can leverage distributed joins

---

### Storage Options Handling

#### PandasEngine
```python
def _merge_storage_options(self, connection, options):
    if hasattr(connection, "pandas_storage_options"):
        conn_storage_opts = connection.pandas_storage_options()
        user_storage_opts = options.get("storage_options", {})
        merged_storage_opts = {**conn_storage_opts, **user_storage_opts}
        return {**options, "storage_options": merged_storage_opts}
    return options
```

**Characteristics:**
- Per-operation credential passing
- Uses `fsspec` under the hood
- Explicit storage_options in each call

#### SparkEngine
```python
def _configure_all_connections(self):
    for conn_name, connection in self.connections.items():
        if hasattr(connection, "configure_spark"):
            connection.configure_spark(self.spark)
```

**Characteristics:**
- Credentials configured once at startup
- Global SparkSession configuration
- All file operations use pre-configured credentials

---

## Delta Lake Operations

### VACUUM (remove old files)

| Engine | Implementation | Characteristics |
|--------|----------------|-----------------|
| Pandas | `dt.vacuum(retention_hours, dry_run)` | Uses `deltalake` Python library |
| Spark | `delta_table.vacuum(retention_hours / 24.0)` | Uses `delta-spark` JVM library |

### History (time travel metadata)

| Engine | Implementation | Return Type |
|--------|----------------|-------------|
| Pandas | `dt.history(limit)` | List of dicts (via deltalake) |
| Spark | `delta_table.history(limit).collect()` | List of Row objects → dicts |

### Restore (rollback to version)

| Engine | Implementation |
|--------|----------------|
| Pandas | `dt.restore(version)` |
| Spark | `delta_table.restoreToVersion(version)` |

---

## Performance Characteristics

### Read Performance

| Operation | PandasEngine | SparkEngine | DuckDBEngine |
|-----------|--------------|-------------|--------------|
| CSV (1GB) | 5-10s | 2-5s (distributed) | 3-6s |
| Parquet (1GB) | 1-3s | 0.5-2s | 0.5-1.5s |
| Delta (1GB) | 2-4s | 1-3s | N/A (no native support) |

### SQL Performance

| Query Type | PandasEngine (DuckDB) | SparkEngine | DuckDBEngine |
|------------|----------------------|-------------|--------------|
| Simple SELECT | Fast | Medium (overhead) | Fast |
| Aggregations | Very Fast | Fast (parallel) | Very Fast |
| Joins | Fast (<1GB) | Fast (any size) | Very Fast (<1GB) |
| Window Functions | Fast | Medium | Very Fast |

---

## Schema Handling

### get_schema()

| Engine | Return Type | Example |
|--------|-------------|---------|
| Pandas | `List[str]` | `["id", "name", "value"]` |
| Spark | `List[Tuple[str, str]]` | `[("id", "bigint"), ("name", "string")]` |
| DuckDB | `List[str]` | `["id", "name", "value"]` |

### get_shape()

| Engine | Implementation | Notes |
|--------|----------------|-------|
| Pandas | `df.shape` | Instant |
| Spark | `(df.count(), len(df.columns))` | Count triggers computation |
| DuckDB | `(len(df), len(df.columns))` | Fast if already materialized |

---

## When to Use Each Engine

### PandasEngine ✅
- Datasets < 10GB
- Development and prototyping
- Rapid iteration
- Simple transformations
- Local execution

### SparkEngine ✅
- Datasets > 100GB
- Distributed data sources
- Complex transformations requiring parallelism
- Production ETL pipelines
- Multi-node clusters available

### DuckDBEngine ✅ (Future)
- Datasets 1GB - 100GB
- Analytical workloads (aggregations, window functions)
- SQL-heavy transformations
- Single-node environments with high RAM
- When you need Spark-like speed without the overhead

---

## Extension Points

### Adding a New Engine

To implement a custom engine, you must:

1. **Inherit from Engine ABC**
```python
from odibi.engine.base import Engine

class MyEngine(Engine):
    pass
```

2. **Implement all 9 abstract methods:**
- `read()`
- `write()`
- `execute_sql()`
- `execute_operation()`
- `get_schema()`
- `get_shape()`
- `count_rows()`
- `count_nulls()`
- `validate_schema()`

3. **Register in engine factory** (if making it official)
```python
# odibi/engine/__init__.py
from .my_engine import MyEngine

def get_engine(engine_type: str):
    if engine_type == "pandas":
        return PandasEngine()
    elif engine_type == "spark":
        return SparkEngine()
    elif engine_type == "my_engine":
        return MyEngine()
```

### Candidate Engines

**Polars** - Rust-based DataFrame library
- Benefits: Faster than Pandas, lazy evaluation
- Challenges: Different API, less ecosystem

**Ray** - Distributed Python runtime
- Benefits: Python-native distributed computing
- Challenges: Different paradigm from Spark

**Dask** - Parallel computing with familiar API
- Benefits: Pandas-like API, good for medium data
- Challenges: Less mature than Spark

**Vaex** - Out-of-core DataFrames
- Benefits: Handles data larger than memory
- Challenges: Limited transformation capabilities

---

## Code Patterns

### Error Handling Pattern

All engines follow this pattern for optional dependencies:

```python
def read(self, connection, format, ...):
    if format == "delta":
        try:
            from deltalake import DeltaTable
        except ImportError:
            raise ImportError(
                "Delta Lake support requires 'pip install odibi[pandas]' or 'pip install deltalake'. "
                "See README.md for installation instructions."
            )
        # ... use DeltaTable
```

**Why:**
- Users only install dependencies they need
- Clear error messages guide installation
- Core library stays lightweight

### Option Merging Pattern

Engines merge connection credentials with user options:

```python
# PandasEngine
merged_options = self._merge_storage_options(connection, options)
df = pd.read_parquet(full_path, **merged_options)

# SparkEngine
self._configure_all_connections()  # One-time setup
df = self.spark.read.format(format).load(full_path)
```

**Why:**
- Users don't repeat credentials in every operation
- Connections encapsulate authentication
- User options can override defaults

---

## Testing Engines

### Mock Engine for Unit Tests

```python
class MockEngine(Engine):
    def __init__(self):
        self.reads = []
        self.writes = []
    
    def read(self, connection, format, **kwargs):
        self.reads.append((connection, format, kwargs))
        return pd.DataFrame({"id": [1, 2, 3]})
    
    def write(self, df, connection, format, **kwargs):
        self.writes.append((df, connection, format, kwargs))
    
    # ... implement other methods as no-ops
```

**Usage:**
- Test pipeline logic without real I/O
- Verify read/write operations
- Fast, isolated tests

---

## Summary

The Engine abstraction is Odibi's most powerful architectural decision:
- **Flexibility** - swap engines without code changes
- **Extensibility** - add new engines easily
- **Testability** - mock engines for unit tests
- **Performance** - choose the right tool for the job

Mastering this abstraction unlocks the full power of Odibi.
