# Design Patterns Deep Dive: Practical Python Patterns

This guide covers essential design patterns for Python developers, especially those working with data pipelines and engineering systems.

## Table of Contents
1. [What Are Design Patterns?](#what-are-design-patterns)
2. [When to Use Patterns](#when-to-use-patterns)
3. [Factory Pattern](#factory-pattern)
4. [Strategy Pattern](#strategy-pattern)
5. [Observer Pattern](#observer-pattern)
6. [Singleton Pattern](#singleton-pattern)
7. [Builder Pattern](#builder-pattern)
8. [Adapter Pattern](#adapter-pattern)
9. [Decorator Pattern](#decorator-pattern)
10. [Command Pattern](#command-pattern)
11. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
12. [Combining Patterns](#combining-patterns)
13. [Real-World Examples](#real-world-examples)
14. [When NOT to Use Patterns](#when-not-to-use-patterns)
15. [Quick Reference](#quick-reference)

---

## What Are Design Patterns?

**Design patterns are reusable solutions to common programming problems.**

They're not code you can copy-paste, but rather templates for how to solve problems in various situations.

### Three Categories

1. **Creational Patterns** - How objects are created
   - Factory, Singleton, Builder

2. **Structural Patterns** - How objects are composed
   - Adapter, Decorator, Facade

3. **Behavioral Patterns** - How objects interact
   - Strategy, Observer, Command

### Why Learn Them?

```python
# Without pattern: Rigid, hard to extend
def process_data(data, format):
    if format == "csv":
        # CSV processing code
        pass
    elif format == "json":
        # JSON processing code
        pass
    elif format == "xml":
        # XML processing code
        pass
    # Adding new format? Modify this function!

# With pattern (Strategy): Flexible, easy to extend
class CSVProcessor:
    def process(self, data): ...

class JSONProcessor:
    def process(self, data): ...

def process_data(data, processor):
    processor.process(data)  # Adding new format? Just create new class!
```

**Key insight:** Patterns help you write code that's easier to extend, test, and maintain.

---

## When to Use Patterns

### Decision Framework

```
Should I use a design pattern?

Is my code hard to change?
├─ Yes → Consider Strategy or Factory
└─ No → Maybe you don't need a pattern yet

Do I have many similar objects with different behaviors?
├─ Yes → Strategy Pattern
└─ No → Keep reading

Do I need to create different types of objects?
├─ Simple creation logic → Factory Pattern
├─ Complex creation with many options → Builder Pattern
└─ Just one instance globally → Singleton Pattern

Do objects need to react to changes?
├─ Yes → Observer Pattern
└─ No → Keep reading

Do I need to make incompatible interfaces work together?
├─ Yes → Adapter Pattern
└─ No → Keep reading
```

### Red Flags That Suggest Patterns

1. **Many if/elif statements** based on type → Strategy or Factory
2. **Copying similar code** → Template Method or Strategy
3. **Complex object creation** → Builder or Factory
4. **Need to notify multiple objects** → Observer
5. **Wrapping existing class** → Decorator or Adapter

---

## Factory Pattern

**Problem:** Creating objects without specifying exact class.

**Solution:** Define an interface for creating objects, let subclasses decide which class to instantiate.

### Simple Factory
```python
# Without Factory: Client knows about all implementations
if data_source == "postgres":
    connection = PostgresConnection(host, port)
elif data_source == "mysql":
    connection = MySQLConnection(host, port)
elif data_source == "mongodb":
    connection = MongoConnection(host, port)

# With Factory: Client doesn't know implementation details
class DatabaseFactory:
    @staticmethod
    def create_connection(db_type, **config):
        if db_type == "postgres":
            return PostgresConnection(**config)
        elif db_type == "mysql":
            return MySQLConnection(**config)
        elif db_type == "mongodb":
            return MongoConnection(**config)
        else:
            raise ValueError(f"Unknown database type: {db_type}")

# Clean usage
connection = DatabaseFactory.create_connection("postgres", host="localhost")
```

### Factory Method Pattern
```python
from abc import ABC, abstractmethod

class DataProcessor(ABC):
    """Abstract base class."""
    
    def process_pipeline(self, data):
        # Template method
        reader = self.create_reader()  # Factory method
        writer = self.create_writer()  # Factory method
        
        raw_data = reader.read(data)
        processed = self.transform(raw_data)
        writer.write(processed)
    
    @abstractmethod
    def create_reader(self):
        """Factory method for creating reader."""
        pass
    
    @abstractmethod
    def create_writer(self):
        """Factory method for creating writer."""
        pass
    
    def transform(self, data):
        # Default transformation
        return data

class CSVProcessor(DataProcessor):
    def create_reader(self):
        return CSVReader()
    
    def create_writer(self):
        return CSVWriter()

class JSONProcessor(DataProcessor):
    def create_reader(self):
        return JSONReader()
    
    def create_writer(self):
        return JSONWriter()

# Usage
processor = CSVProcessor()
processor.process_pipeline("data.csv")
```

### Registry-Based Factory (Python-Specific)
```python
class DataSourceRegistry:
    """Register data sources dynamically."""
    
    _sources = {}
    
    @classmethod
    def register(cls, name):
        """Decorator to register a data source."""
        def decorator(source_class):
            cls._sources[name] = source_class
            return source_class
        return decorator
    
    @classmethod
    def create(cls, name, **kwargs):
        """Create a data source by name."""
        if name not in cls._sources:
            raise ValueError(f"Unknown source: {name}")
        return cls._sources[name](**kwargs)

# Register sources
@DataSourceRegistry.register("postgres")
class PostgresSource:
    def __init__(self, host, port):
        self.host = host
        self.port = port

@DataSourceRegistry.register("s3")
class S3Source:
    def __init__(self, bucket, region):
        self.bucket = bucket
        self.region = region

# Clean, extensible usage
source = DataSourceRegistry.create("postgres", host="localhost", port=5432)
```

**When to use:**
- Creating objects based on input (file type, config, user choice)
- Hiding complex initialization logic
- Supporting multiple implementations of same interface
- Plugin architectures

---

## Strategy Pattern

**Problem:** Multiple algorithms for the same task, chosen at runtime.

**Solution:** Define a family of algorithms, encapsulate each one, and make them interchangeable.

### Basic Strategy
```python
from abc import ABC, abstractmethod

# Strategy interface
class CompressionStrategy(ABC):
    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        pass

# Concrete strategies
class GzipCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        import gzip
        return gzip.compress(data)

class ZlibCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        import zlib
        return zlib.compress(data)

class NoCompression(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        return data

# Context that uses strategy
class FileUploader:
    def __init__(self, compression_strategy: CompressionStrategy):
        self.compression = compression_strategy
    
    def upload(self, data: bytes):
        compressed = self.compression.compress(data)
        # Upload compressed data
        print(f"Uploading {len(compressed)} bytes")

# Usage - Strategy chosen at runtime
uploader = FileUploader(GzipCompression())
uploader.upload(b"some data")

# Change strategy
uploader.compression = ZlibCompression()
uploader.upload(b"more data")
```

### Function-Based Strategy (Pythonic)
```python
# In Python, functions are first-class objects
# We can use functions directly as strategies

import gzip
import zlib

class FileUploader:
    def __init__(self, compression_fn):
        self.compress = compression_fn
    
    def upload(self, data: bytes):
        compressed = self.compress(data)
        print(f"Uploading {len(compressed)} bytes")

# Functions as strategies
def gzip_compress(data):
    return gzip.compress(data)

def zlib_compress(data):
    return zlib.compress(data)

def no_compress(data):
    return data

# Usage
uploader = FileUploader(gzip_compress)
uploader.upload(b"some data")

# Or use lambda
uploader = FileUploader(lambda x: zlib.compress(x))
```

### Strategy with Configuration
```python
class DataValidator:
    """Validate data with pluggable rules."""
    
    def __init__(self):
        self.strategies = []
    
    def add_strategy(self, strategy):
        self.strategies.append(strategy)
        return self  # Fluent interface
    
    def validate(self, data):
        errors = []
        for strategy in self.strategies:
            error = strategy(data)
            if error:
                errors.append(error)
        return errors

# Define validation strategies
def check_not_empty(data):
    if not data:
        return "Data cannot be empty"

def check_max_length(max_len):
    def validator(data):
        if len(data) > max_len:
            return f"Data exceeds {max_len} characters"
    return validator

def check_format(pattern):
    import re
    def validator(data):
        if not re.match(pattern, data):
            return f"Data doesn't match pattern {pattern}"
    return validator

# Usage with fluent interface
validator = (DataValidator()
    .add_strategy(check_not_empty)
    .add_strategy(check_max_length(100))
    .add_strategy(check_format(r'^\w+$'))
)

errors = validator.validate("test@data")
```

**When to use:**
- Multiple ways to do the same thing
- Avoiding large if/elif chains
- Runtime algorithm selection
- Different processing based on configuration

**Data Engineering Examples:**
- Data format parsers (CSV, JSON, Parquet)
- Compression algorithms
- Encryption methods
- Data validation rules
- Cost calculation strategies

---

## Observer Pattern

**Problem:** Multiple objects need to be notified when something changes.

**Solution:** Define a one-to-many dependency so when one object changes state, all dependents are notified.

### Basic Observer
```python
from abc import ABC, abstractmethod
from typing import List

# Observer interface
class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

# Subject (Observable)
class DataPipeline:
    def __init__(self):
        self._observers: List[Observer] = []
        self._state = None
    
    def attach(self, observer: Observer):
        self._observers.append(observer)
    
    def detach(self, observer: Observer):
        self._observers.remove(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
    
    def run(self, data):
        self._state = "processing"
        self.notify()
        
        # Process data
        result = self._process(data)
        
        self._state = "completed"
        self.notify()
        
        return result
    
    def _process(self, data):
        return data  # Actual processing

# Concrete observers
class Logger(Observer):
    def update(self, subject: DataPipeline):
        print(f"[LOG] Pipeline state: {subject._state}")

class MetricsCollector(Observer):
    def __init__(self):
        self.events = []
    
    def update(self, subject: DataPipeline):
        import time
        self.events.append({
            'state': subject._state,
            'timestamp': time.time()
        })

class EmailNotifier(Observer):
    def update(self, subject: DataPipeline):
        if subject._state == "completed":
            print(f"[EMAIL] Pipeline completed successfully")

# Usage
pipeline = DataPipeline()
pipeline.attach(Logger())
pipeline.attach(MetricsCollector())
pipeline.attach(EmailNotifier())

pipeline.run("some data")
# [LOG] Pipeline state: processing
# [LOG] Pipeline state: completed
# [EMAIL] Pipeline completed successfully
```

### Event-Driven Observer (Pythonic)
```python
class EventEmitter:
    """Simple event system."""
    
    def __init__(self):
        self._listeners = {}
    
    def on(self, event_name, callback):
        """Register event listener."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
    
    def off(self, event_name, callback):
        """Remove event listener."""
        if event_name in self._listeners:
            self._listeners[event_name].remove(callback)
    
    def emit(self, event_name, *args, **kwargs):
        """Trigger event."""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kwargs)

class DataPipeline(EventEmitter):
    def run(self, data):
        self.emit('start', data=data)
        
        try:
            result = self._process(data)
            self.emit('success', result=result)
            return result
        except Exception as e:
            self.emit('error', error=e)
            raise
        finally:
            self.emit('complete')
    
    def _process(self, data):
        return data

# Usage with functions as listeners
pipeline = DataPipeline()

pipeline.on('start', lambda **kw: print(f"Starting with {kw['data']}"))
pipeline.on('success', lambda **kw: print(f"Success: {kw['result']}"))
pipeline.on('error', lambda **kw: print(f"Error: {kw['error']}"))
pipeline.on('complete', lambda: print("Pipeline complete"))

pipeline.run("test data")
```

**When to use:**
- Multiple components react to state changes
- Logging, monitoring, notifications
- Event-driven architectures
- Decoupling components

**Data Engineering Examples:**
- Pipeline monitoring
- Data quality alerts
- Metrics collection
- Audit logging

---

## Singleton Pattern

**Problem:** Need exactly one instance of a class globally.

**Solution:** Ensure class has only one instance and provide global access point.

### Classic Singleton
```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Called only once."""
        print("Initializing database connection")
        self.connection = self._connect()
    
    def _connect(self):
        # Expensive connection setup
        return "connection"

# Usage
db1 = DatabaseConnection()  # Initializing database connection
db2 = DatabaseConnection()  # Uses existing instance
assert db1 is db2  # True - same instance
```

### Decorator-Based Singleton
```python
def singleton(cls):
    """Decorator to make a class a singleton."""
    instances = {}
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class Configuration:
    def __init__(self):
        print("Loading configuration")
        self.settings = self._load_settings()
    
    def _load_settings(self):
        return {"debug": True}

# Usage
config1 = Configuration()  # Loading configuration
config2 = Configuration()  # Uses existing
assert config1 is config2  # True
```

### Module-Level Singleton (Pythonic)
```python
# config.py - The module itself is a singleton!

_settings = None

def get_settings():
    global _settings
    if _settings is None:
        _settings = _load_settings()
    return _settings

def _load_settings():
    print("Loading settings")
    return {"debug": True}

# Usage
from config import get_settings

settings1 = get_settings()  # Loading settings
settings2 = get_settings()  # Uses cached
assert settings1 is settings2  # True
```

### Thread-Safe Singleton
```python
import threading

class ConfigManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:  # Thread-safe
                if cls._instance is None:  # Double-check
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config = {}
```

**When to use:**
- Configuration management
- Logging
- Connection pools
- Cache managers

**⚠️ Warning:** Singletons can make testing harder. Consider dependency injection instead.

**Better Alternative:**
```python
# Instead of Singleton
class App:
    def __init__(self):
        self.config = ConfigManager()  # Global singleton

# Use Dependency Injection
class App:
    def __init__(self, config):
        self.config = config  # Passed in, easy to test

# Somewhere at app startup
config = load_config()
app = App(config)
```

---

## Builder Pattern

**Problem:** Creating complex objects with many optional parameters.

**Solution:** Separate construction from representation, build step-by-step.

### Basic Builder
```python
class QueryBuilder:
    """Build SQL queries step by step."""
    
    def __init__(self):
        self._select = []
        self._from = None
        self._where = []
        self._order_by = []
        self._limit = None
    
    def select(self, *columns):
        self._select.extend(columns)
        return self  # Return self for chaining
    
    def from_table(self, table):
        self._from = table
        return self
    
    def where(self, condition):
        self._where.append(condition)
        return self
    
    def order_by(self, column, desc=False):
        direction = "DESC" if desc else "ASC"
        self._order_by.append(f"{column} {direction}")
        return self
    
    def limit(self, count):
        self._limit = count
        return self
    
    def build(self):
        """Build the final query."""
        parts = []
        
        # SELECT
        if self._select:
            parts.append(f"SELECT {', '.join(self._select)}")
        else:
            parts.append("SELECT *")
        
        # FROM
        if not self._from:
            raise ValueError("FROM table is required")
        parts.append(f"FROM {self._from}")
        
        # WHERE
        if self._where:
            parts.append(f"WHERE {' AND '.join(self._where)}")
        
        # ORDER BY
        if self._order_by:
            parts.append(f"ORDER BY {', '.join(self._order_by)}")
        
        # LIMIT
        if self._limit:
            parts.append(f"LIMIT {self._limit}")
        
        return " ".join(parts)

# Usage - Fluent interface
query = (QueryBuilder()
    .select("name", "email", "created_at")
    .from_table("users")
    .where("active = true")
    .where("age >= 18")
    .order_by("created_at", desc=True)
    .limit(10)
    .build()
)

print(query)
# SELECT name, email, created_at FROM users 
# WHERE active = true AND age >= 18 
# ORDER BY created_at DESC LIMIT 10
```

### Builder with Director
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DataPipeline:
    """Complex object to build."""
    source: str
    transformations: List[callable]
    destination: str
    error_handler: Optional[callable] = None
    validators: List[callable] = None

class PipelineBuilder:
    """Builder for DataPipeline."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._source = None
        self._transformations = []
        self._destination = None
        self._error_handler = None
        self._validators = []
    
    def set_source(self, source):
        self._source = source
        return self
    
    def add_transformation(self, transform):
        self._transformations.append(transform)
        return self
    
    def set_destination(self, destination):
        self._destination = destination
        return self
    
    def set_error_handler(self, handler):
        self._error_handler = handler
        return self
    
    def add_validator(self, validator):
        self._validators.append(validator)
        return self
    
    def build(self) -> DataPipeline:
        """Construct the pipeline."""
        if not self._source or not self._destination:
            raise ValueError("Source and destination required")
        
        pipeline = DataPipeline(
            source=self._source,
            transformations=self._transformations,
            destination=self._destination,
            error_handler=self._error_handler,
            validators=self._validators
        )
        self.reset()  # Reset for next build
        return pipeline

# Director - knows how to build specific configurations
class PipelineDirector:
    """Constructs common pipeline types."""
    
    def __init__(self, builder: PipelineBuilder):
        self.builder = builder
    
    def build_etl_pipeline(self, source, destination):
        """Standard ETL pipeline."""
        return (self.builder
            .set_source(source)
            .add_transformation(lambda x: x.strip())
            .add_transformation(lambda x: x.upper())
            .add_validator(lambda x: len(x) > 0)
            .set_destination(destination)
            .set_error_handler(lambda e: print(f"Error: {e}"))
            .build()
        )
    
    def build_simple_pipeline(self, source, destination):
        """Simple pass-through pipeline."""
        return (self.builder
            .set_source(source)
            .set_destination(destination)
            .build()
        )

# Usage
builder = PipelineBuilder()
director = PipelineDirector(builder)

# Build specific pipeline types
etl = director.build_etl_pipeline("s3://input", "s3://output")
simple = director.build_simple_pipeline("file.csv", "output.csv")
```

**When to use:**
- Objects with many optional parameters
- Step-by-step construction
- Different representations of same data
- Complex initialization logic

**Data Engineering Examples:**
- SQL query builders
- Data pipeline configuration
- Report generators
- API request builders

---

## Adapter Pattern

**Problem:** Make incompatible interfaces work together.

**Solution:** Create adapter class that translates one interface to another.

### Class Adapter
```python
# Legacy system with old interface
class OldDataSource:
    def fetch_data(self):
        return "legacy data format"
    
    def get_metadata(self):
        return {"version": "1.0"}

# New interface expected by our system
class DataSource(ABC):
    @abstractmethod
    def read(self) -> dict:
        pass

# Adapter makes old source work with new interface
class LegacyDataAdapter(DataSource):
    def __init__(self, old_source: OldDataSource):
        self.old_source = old_source
    
    def read(self) -> dict:
        # Translate old interface to new
        legacy_data = self.old_source.fetch_data()
        metadata = self.old_source.get_metadata()
        
        return {
            "data": legacy_data,
            "metadata": metadata
        }

# Usage
old_source = OldDataSource()
adapter = LegacyDataAdapter(old_source)
data = adapter.read()  # Uses new interface!
```

### Real-World Example: Database Adapters
```python
from abc import ABC, abstractmethod

class Database(ABC):
    """Common interface for all databases."""
    
    @abstractmethod
    def query(self, sql: str) -> list:
        pass
    
    @abstractmethod
    def execute(self, sql: str) -> int:
        pass

class PostgresAdapter(Database):
    def __init__(self, connection):
        self.conn = connection
    
    def query(self, sql: str) -> list:
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    
    def execute(self, sql: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        return cursor.rowcount

class MongoAdapter(Database):
    """Adapt MongoDB to SQL-like interface."""
    
    def __init__(self, client, database):
        self.db = client[database]
    
    def query(self, collection: str) -> list:
        # Simplified - real adapter would parse SQL
        return list(self.db[collection].find())
    
    def execute(self, collection: str) -> int:
        # Simplified
        result = self.db[collection].delete_many({})
        return result.deleted_count

# Usage - same interface for different databases
def process_data(database: Database):
    results = database.query("SELECT * FROM users")
    # Process results...

postgres = PostgresAdapter(pg_connection)
mongo = MongoAdapter(mongo_client, "mydb")

process_data(postgres)  # Works
process_data(mongo)     # Also works!
```

**When to use:**
- Working with third-party libraries
- Legacy code integration
- Multiple data sources with different APIs
- Creating common interface for similar services

---

## Decorator Pattern

**Problem:** Add behavior to objects dynamically without affecting other instances.

**Solution:** Wrap objects with decorator objects that add new behavior.

**Note:** This is different from Python's `@decorator` syntax, though the concept is similar.

### Functional Decorator Pattern
```python
class DataTransformer:
    def transform(self, data):
        return data

class UppercaseDecorator:
    def __init__(self, transformer):
        self.transformer = transformer
    
    def transform(self, data):
        result = self.transformer.transform(data)
        return result.upper()

class StripDecorator:
    def __init__(self, transformer):
        self.transformer = transformer
    
    def transform(self, data):
        result = self.transformer.transform(data)
        return result.strip()

class ReplaceDecorator:
    def __init__(self, transformer, old, new):
        self.transformer = transformer
        self.old = old
        self.new = new
    
    def transform(self, data):
        result = self.transformer.transform(data)
        return result.replace(self.old, self.new)

# Stack decorators
transformer = DataTransformer()
transformer = StripDecorator(transformer)
transformer = UppercaseDecorator(transformer)
transformer = ReplaceDecorator(transformer, "DATA", "INFO")

result = transformer.transform("  some data  ")
# "  SOME INFO  " → stripped → "SOME INFO" → replaced → "SOME INFO"
```

### Python's @ Decorator (Recommended)
```python
# Use Python's built-in decorator syntax
def uppercase(func):
    def wrapper(data):
        return func(data).upper()
    return wrapper

def strip(func):
    def wrapper(data):
        return func(data).strip()
    return wrapper

@strip
@uppercase
def transform(data):
    return data

result = transform("  hello  ")  # "HELLO"
```

**See the [DECORATORS_GUIDE.md](../05_decorators/DECORATORS_GUIDE.md) for comprehensive decorator examples.**

---

## Command Pattern

**Problem:** Encapsulate requests as objects, enabling queuing, logging, and undo.

**Solution:** Turn requests into objects with common interface.

### Basic Command
```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class LoadDataCommand(Command):
    def __init__(self, source):
        self.source = source
        self.data = None
    
    def execute(self):
        print(f"Loading data from {self.source}")
        self.data = f"data from {self.source}"
        return self.data
    
    def undo(self):
        print(f"Unloading data from {self.source}")
        self.data = None

class TransformCommand(Command):
    def __init__(self, data, transformation):
        self.data = data
        self.transformation = transformation
        self.original = None
    
    def execute(self):
        self.original = self.data.copy() if hasattr(self.data, 'copy') else self.data
        print(f"Transforming data")
        return self.transformation(self.data)
    
    def undo(self):
        print(f"Reverting transformation")
        return self.original

# Command executor with history
class CommandExecutor:
    def __init__(self):
        self.history = []
    
    def execute(self, command: Command):
        result = command.execute()
        self.history.append(command)
        return result
    
    def undo(self):
        if not self.history:
            print("Nothing to undo")
            return
        command = self.history.pop()
        command.undo()

# Usage
executor = CommandExecutor()

load_cmd = LoadDataCommand("database")
executor.execute(load_cmd)

transform_cmd = TransformCommand([1, 2, 3], lambda x: [i * 2 for i in x])
executor.execute(transform_cmd)

executor.undo()  # Undo transformation
executor.undo()  # Undo load
```

### Queue-Based Commands (Data Pipeline)
```python
from queue import Queue
import threading

class PipelineCommand(ABC):
    @abstractmethod
    def execute(self, context):
        pass

class ExtractCommand(PipelineCommand):
    def __init__(self, source):
        self.source = source
    
    def execute(self, context):
        print(f"Extracting from {self.source}")
        context['data'] = f"data from {self.source}"

class TransformCommand(PipelineCommand):
    def __init__(self, transformer):
        self.transformer = transformer
    
    def execute(self, context):
        print(f"Transforming data")
        context['data'] = self.transformer(context['data'])

class LoadCommand(PipelineCommand):
    def __init__(self, destination):
        self.destination = destination
    
    def execute(self, context):
        print(f"Loading to {self.destination}")
        # Save context['data'] to destination

class Pipeline:
    def __init__(self):
        self.commands = Queue()
        self.context = {}
    
    def add_command(self, command: PipelineCommand):
        self.commands.put(command)
    
    def run(self):
        while not self.commands.empty():
            command = self.commands.get()
            command.execute(self.context)

# Usage
pipeline = Pipeline()
pipeline.add_command(ExtractCommand("s3://bucket/data"))
pipeline.add_command(TransformCommand(lambda x: x.upper()))
pipeline.add_command(LoadCommand("database"))
pipeline.run()
```

**When to use:**
- Implementing undo/redo
- Queuing operations
- Logging/auditing operations
- Delayed execution
- Transaction-like behavior

---

## Anti-Patterns to Avoid

### 1. God Object
```python
# ✗ BAD - One class does everything
class DataManager:
    def connect_database(self): ...
    def read_csv(self): ...
    def validate_data(self): ...
    def transform_data(self): ...
    def train_model(self): ...
    def send_email(self): ...
    def generate_report(self): ...
    # 1000 more methods...

# ✓ GOOD - Single responsibility
class DatabaseConnector:
    def connect(self): ...

class CSVReader:
    def read(self): ...

class DataValidator:
    def validate(self): ...
```

### 2. Cargo Cult Programming
```python
# ✗ BAD - Using pattern because "best practice"
# when simple solution works fine

# Don't need Factory for 2 simple classes
class AnimalFactory:
    def create(self, type):
        if type == "dog":
            return Dog()
        return Cat()

# ✓ GOOD - Just use direct instantiation
dog = Dog()
cat = Cat()
```

### 3. Pattern Overload
```python
# ✗ BAD - Too many patterns for simple task
class SingletonFactoryBuilderAdapter:
    # What is this even doing?
    pass

# ✓ GOOD - Use simple, clear code
def process_data(data):
    return data.upper()
```

### 4. Premature Abstraction
```python
# ✗ BAD - Creating abstract interface for one implementation
class PaymentProcessor(ABC):
    @abstractmethod
    def process(self): ...

class StripePaymentProcessor(PaymentProcessor):
    def process(self): ...
    # Only implementation!

# ✓ GOOD - Add abstraction when second implementation needed
class StripePaymentProcessor:
    def process(self): ...
    # Simple until we add another processor
```

### 5. Magic Happens Here
```python
# ✗ BAD - Over-engineered decorator magic
def auto_cache_with_ttl_and_invalidation(
    ttl=3600, 
    cache_backend="redis",
    invalidation_strategy="LRU",
    serialization="pickle"
):
    # 200 lines of complex logic
    pass

# ✓ GOOD - Use simple, tested library
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(x):
    return x * 2
```

---

## Combining Patterns

Patterns often work together:

### Factory + Strategy
```python
class ProcessorFactory:
    """Factory creates different strategies."""
    
    @staticmethod
    def create(format_type):
        if format_type == "csv":
            return CSVProcessor()  # Strategy
        elif format_type == "json":
            return JSONProcessor()  # Strategy
        else:
            raise ValueError(f"Unknown format: {format_type}")

processor = ProcessorFactory.create("csv")
processor.process(data)
```

### Observer + Command
```python
class Pipeline(EventEmitter):
    def execute_command(self, command):
        self.emit('command_start', command)
        result = command.execute()
        self.emit('command_complete', command, result)
        return result
```

### Builder + Factory
```python
class PipelineFactory:
    @staticmethod
    def create_etl_pipeline():
        """Factory uses builder internally."""
        return (PipelineBuilder()
            .set_source("database")
            .add_transformation(clean_data)
            .set_destination("warehouse")
            .build()
        )
```

---

## Real-World Examples

### Example 1: Plugin System (Factory + Registry)
```python
class PluginRegistry:
    """Discover and load plugins."""
    
    _plugins = {}
    
    @classmethod
    def register(cls, name):
        def decorator(plugin_class):
            cls._plugins[name] = plugin_class
            return plugin_class
        return decorator
    
    @classmethod
    def load(cls, name, **config):
        if name not in cls._plugins:
            raise ValueError(f"Plugin {name} not found")
        return cls._plugins[name](**config)
    
    @classmethod
    def list_plugins(cls):
        return list(cls._plugins.keys())

# Plugins auto-register
@PluginRegistry.register("email")
class EmailPlugin:
    def __init__(self, smtp_host):
        self.smtp_host = smtp_host
    
    def send(self, message):
        print(f"Sending email via {self.smtp_host}")

@PluginRegistry.register("slack")
class SlackPlugin:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send(self, message):
        print(f"Sending to Slack: {self.webhook_url}")

# Usage
print(PluginRegistry.list_plugins())  # ['email', 'slack']
notifier = PluginRegistry.load("email", smtp_host="smtp.gmail.com")
notifier.send("Hello!")
```

### Example 2: Data Pipeline (Strategy + Observer + Command)
```python
class DataPipeline(EventEmitter):
    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        self.commands = []
    
    def add_step(self, command):
        self.commands.append(command)
    
    def run(self, data):
        self.emit('start', data=data)
        
        current = data
        for i, command in enumerate(self.commands):
            self.emit('step_start', step=i, command=command)
            current = command.execute(current)
            self.emit('step_complete', step=i, result=current)
        
        # Use strategy for final processing
        result = self.strategy.process(current)
        
        self.emit('complete', result=result)
        return result
```

### Example 3: Configuration Manager (Singleton + Builder)
```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def builder(cls):
        return ConfigBuilder(cls())

class ConfigBuilder:
    def __init__(self, config):
        self.config = config
    
    def set_database(self, url):
        self.config.database_url = url
        return self
    
    def set_cache(self, backend):
        self.config.cache_backend = backend
        return self
    
    def build(self):
        return self.config

# Usage
config = (Config.builder()
    .set_database("postgresql://localhost")
    .set_cache("redis")
    .build()
)
```

---

## When NOT to Use Patterns

### YAGNI Principle
**"You Aren't Gonna Need It"**

```python
# ✗ Premature: Building extensible system for 1 user
class AbstractUserRepositoryFactory:
    ...

# ✓ Start simple
users = {"alice": User("alice")}

# Add patterns when complexity demands it
```

### Signs You're Over-Engineering

1. **More interfaces than implementations**
2. **Can't explain pattern choice in one sentence**
3. **Code is harder to read with pattern than without**
4. **Testing becomes harder**
5. **"Future-proofing" for imaginary requirements**

### When to Refactor TO Patterns

```
Refactor to pattern when:
├─ Same code appears 3+ times → Strategy/Factory
├─ Function has 5+ if/elif → Strategy
├─ Adding features requires editing existing code → Open/Closed violation
├─ Tests are difficult → Dependency issues, need Injection
└─ Can't understand code in 30 seconds → Too complex, need simplification
```

---

## Quick Reference

### Pattern Selection Guide

| Problem | Pattern | When to Use |
|---------|---------|-------------|
| Create different object types | Factory | Based on input/config |
| Many algorithms for same task | Strategy | Runtime selection |
| Notify multiple objects | Observer | Event-driven, monitoring |
| One global instance | Singleton | Config, logging, pools |
| Complex object construction | Builder | Many optional parameters |
| Incompatible interfaces | Adapter | Third-party integration |
| Add behavior dynamically | Decorator | Extend without modification |
| Encapsulate requests | Command | Undo, queue, logging |

### Python-Specific Alternatives

| Pattern | Pythonic Alternative |
|---------|---------------------|
| Strategy | Functions as first-class objects |
| Singleton | Module-level variables |
| Factory | Class methods, `__new__` |
| Builder | Keyword arguments, dataclasses |
| Observer | Callbacks, generators |
| Command | Functions, closures |
| Decorator | `@decorator` syntax |

### Red Flags Checklist

- [ ] Can simple function/class do this?
- [ ] Will pattern make code harder to understand?
- [ ] Am I solving actual problem or hypothetical one?
- [ ] Can I explain pattern choice clearly?
- [ ] Will this make testing easier or harder?

---

## Key Takeaways

1. **Patterns are tools, not rules** - Use when they solve real problems
2. **Start simple** - Add patterns when complexity demands it
3. **Python has alternatives** - Functions, decorators, modules can replace classical patterns
4. **Readability counts** - Pattern should make code clearer, not more complex
5. **Test first** - If pattern makes testing harder, reconsider
6. **YAGNI** - Don't build for imaginary future requirements
7. **Combine carefully** - Patterns can work together, but don't overdo it
8. **Know your domain** - Some patterns fit data engineering better than others

**Remember:** The best pattern is often no pattern—just clean, simple code that solves the problem at hand!
