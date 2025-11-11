# Odibi's @transformation Decorator: Deep Dive

Complete analysis of how Odibi uses decorators for transformation registration.

---

## 📁 Architecture Overview

Odibi's transformation system consists of 4 key modules:

```
odibi/transformations/
├── decorators.py       # @transformation decorator
├── registry.py         # Global registry (singleton)
├── explanation.py      # ExplanationDecorator class
└── context.py          # TransformationContext dataclass
```

---

## 🔍 Part 1: The @transformation Decorator

**File:** `decorators.py`

```python
def transformation(
    name: str,
    version: str = "1.0.0",
    category: Optional[str] = None,
    tags: Optional[list] = None,
):
    """
    Decorator to register a transformation.
    
    Returns:
        Decorated function with .explain() capability
    """
    
    def decorator(func: Callable) -> Callable:
        # 1. Wrap with explanation capability
        wrapped = wrap_with_explanation(func)
        
        # 2. Register in global registry
        registry = get_registry()
        registry.register(
            name=name,
            func=wrapped,
            version=version,
            category=category,
            tags=tags
        )
        
        return wrapped
    
    return decorator
```

### Key Design Decisions

1. **Decorator Factory Pattern**
   - Takes arguments (name, version, category, tags)
   - Returns actual decorator function
   - Enables `@transformation("my_transform", category="filtering")`

2. **Two-Stage Wrapping**
   - First: Wrap with `ExplanationDecorator` (adds `.explain` method)
   - Second: Register in global registry
   - Returns wrapped function (not original)

3. **Separation of Concerns**
   - Decorator handles wrapping + registration
   - Registry handles storage + validation
   - ExplanationDecorator handles `.explain` pattern

---

## 🔍 Part 2: The Registry

**File:** `registry.py`

```python
class TransformationRegistry:
    """Central registry for all transformations."""
    
    def __init__(self):
        self._transformations: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        version: str = "1.0.0",
        category: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> Callable:
        # Validation 1: Unique name
        if name in self._transformations:
            raise ValueError(
                f"Transformation '{name}' already registered. "
                f"Use a unique name or unregister the existing transformation."
            )
        
        # Validation 2: Docstring required
        if not func.__doc__ or len(func.__doc__.strip()) < 10:
            raise ValueError(
                f"Transformation '{name}' must have a docstring (minimum 10 characters).\\n"
                f"Documentation is mandatory in Odibi."
            )
        
        # Store function + metadata separately
        self._transformations[name] = func
        self._metadata[name] = {
            "version": version,
            "category": category,
            "tags": tags or [],
            "docstring": func.__doc__,
        }
        
        return func
```

### Key Design Decisions

1. **Dual Storage**
   - `_transformations`: Maps name → function
   - `_metadata`: Maps name → metadata dict
   - Keeps concerns separated

2. **Mandatory Documentation**
   - Validates docstring exists and is >= 10 chars
   - Documentation is **first-class** in Odibi
   - Enables automatic documentation generation

3. **Semantic Versioning**
   - Every transformation has a version
   - Enables breaking change management
   - Could enable version-specific retrieval

4. **Category + Tags**
   - Enables discovery (`list_by_category()`)
   - Tags for flexible filtering
   - Could power search functionality

---

## 🔍 Part 3: The Explanation System

**File:** `explanation.py`

```python
class ExplanationDecorator:
    """Adds .explain() method to transformation functions."""
    
    def __init__(self, func: Callable):
        self.func = func
        self._explain_func: Optional[Callable] = None
        
        # Copy function metadata (crucial!)
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.__dict__.update(func.__dict__)
        self.__module__ = func.__module__
        self.__qualname__ = func.__qualname__
        self.__annotations__ = func.__annotations__
    
    def __call__(self, *args, **kwargs):
        """Make the wrapper callable."""
        return self.func(*args, **kwargs)
    
    def explain(self, explain_func: Callable) -> Callable:
        """Register explanation function."""
        self._explain_func = explain_func
        return self.func  # Return original for chaining
    
    def get_explanation(self, **kwargs) -> str:
        """Get explanation with context."""
        if self._explain_func is None:
            raise ValueError(
                f"No explanation registered for transformation '{self.func.__name__}'. "
                f"Use @{self.func.__name__}.explain to register one."
            )
        return self._explain_func(**kwargs)
```

### Usage Pattern

```python
@transformation("filter_threshold", category="filtering")
def filter_threshold(df, threshold):
    """Filter records above threshold."""
    return df[df.value > threshold]

@filter_threshold.explain
def explain(threshold, **context):
    plant = context.get('plant', 'Unknown')
    return f"Filter {plant} records above {threshold}"
```

### Key Design Decisions

1. **Class-Based Decorator**
   - Needs state (`_explain_func`)
   - Needs multiple methods (`.explain`, `.get_explanation`)
   - `__call__` makes it behave like original function

2. **Metadata Preservation**
   - Manually copies ALL function attributes
   - More thorough than `@wraps`
   - Ensures introspection works correctly

3. **Explanation as Decorator**
   - `@func.explain` pattern is elegant
   - Keeps explanation close to transformation
   - Explanation function receives context via **kwargs

4. **Lazy Validation**
   - Doesn't require explanation to be registered
   - Only fails when `.get_explanation()` is called
   - Explanations are optional (for now)

---

## 🔍 Part 4: Context Passing

**File:** `context.py`

```python
@dataclass
class TransformationContext:
    """Context passed to transformations and explain() methods."""
    
    # Node-level
    node_name: str
    operation_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    # Pipeline-level
    pipeline_name: Optional[str] = None
    layer: Optional[str] = None
    
    # Project-level (from YAML)
    project: Optional[str] = None
    plant: Optional[str] = None
    asset: Optional[str] = None
    business_unit: Optional[str] = None
    
    # Runtime
    environment: str = "development"
    
    # Additional metadata
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for **kwargs passing."""
        return {
            "node": self.node_name,
            "operation": self.operation_name,
            "params": self.params,
            "pipeline": self.pipeline_name,
            "layer": self.layer,
            "project": self.project,
            "plant": self.plant,
            "asset": self.asset,
            "business_unit": self.business_unit,
            "environment": self.environment,
            **self.extra,
        }
```

### Key Design Decisions

1. **Dataclass for Structure**
   - Clear schema for context
   - Type hints enable validation
   - Default values for optional fields

2. **Three-Level Hierarchy**
   - Node-level: Current operation
   - Pipeline-level: Pipeline metadata
   - Project-level: YAML top-level config

3. **to_dict() for Unpacking**
   - Enables `explain(**context.to_dict())`
   - Flattens nested structure
   - Explanation functions receive flat **kwargs

4. **Extra for Extension**
   - `extra` dict allows custom metadata
   - Unpacked with `**self.extra`
   - Enables future extensibility

---

## 🎯 Complete Example

```python
# 1. Register transformation
@transformation("filter_threshold", category="filtering", version="2.0.0")
def filter_threshold(df, threshold: float):
    """Filter records above threshold value."""
    return df[df.value > threshold]

# 2. Add explanation
@filter_threshold.explain
def explain_filter(threshold, plant=None, **context):
    plant_name = plant or "Unknown"
    return f"Filter {plant_name} records where value > {threshold}"

# 3. Use in pipeline
from odibi.transformations import get_registry

registry = get_registry()
transform = registry.get("filter_threshold")

# Execute transformation
result_df = transform(input_df, threshold=100)

# Generate explanation
from odibi.transformations.context import TransformationContext

context = TransformationContext(
    node_name="filter_high_values",
    operation_name="filter_threshold",
    params={"threshold": 100},
    plant="Indianapolis"
)

explanation = transform.get_explanation(**context.to_dict())
# → "Filter Indianapolis records where value > 100"
```

---

## 🏗️ Why This Architecture?

### 1. Separation of Concerns
- **Decorator** = Wrapping + Registration
- **Registry** = Storage + Lookup
- **ExplanationDecorator** = Explanation pattern
- **Context** = Metadata passing

### 2. Global Registry Pattern
- Enables lookup by name (from YAML)
- Single source of truth
- Testable (can clear registry)

### 3. Explanation as Documentation
- Transformations explain themselves
- Documentation lives with code
- Generated docs use `.get_explanation()`

### 4. Type Safety + Validation
- Pydantic models for configs
- Type hints throughout
- Runtime validation (docstrings, signatures)

### 5. Context-Aware Execution
- Explanations adapt to context (plant, asset)
- Same transform, different explanations
- Enables audit logs

---

## 🎓 Lessons for Your Code

### 1. Use Decorator Factories for Arguments
```python
@register(name="my_func", category="processing")  # ✅
# Not: @register  # ❌ (no arguments)
```

### 2. Validate at Registration Time
```python
# Fail early, not at runtime
if not func.__doc__:
    raise ValueError("Docstring required")  # ✅
```

### 3. Preserve Metadata Thoroughly
```python
# Don't just use @wraps - copy everything
self.__name__ = func.__name__
self.__doc__ = func.__doc__
self.__dict__.update(func.__dict__)  # ✅
```

### 4. Use Classes for Stateful Decorators
```python
# If you need state or multiple methods, use a class
class MyDecorator:
    def __init__(self, func):
        self.func = func
        self.state = {}
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
```

### 5. Context as **kwargs is Flexible
```python
def explain(threshold, plant=None, **context):
    # Named args for required params
    # **context catches everything else
    pass
```

---

## 📚 Further Reading

- [Odibi Transformations Source](c:/Users/hodibi/OneDrive - Ingredion/Desktop/Repos/Odibi/odibi/transformations/)
- [PEP 318 - Decorators](https://peps.python.org/pep-0318/)
- [Python Descriptors (advanced)](https://docs.python.org/3/howto/descriptor.html)
