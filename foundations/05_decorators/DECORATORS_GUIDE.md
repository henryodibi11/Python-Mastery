# Decorators Deep Dive: From Basics to Advanced

This guide demystifies Python decorators—one of the most powerful yet initially confusing features in Python.

## Table of Contents
1. [What Decorators Actually Are](#what-decorators-actually-are)
2. [The @ Syntax Explained](#the--syntax-explained)
3. [Closures and How They Relate](#closures-and-how-they-relate)
4. [Function Decorators](#function-decorators)
5. [Class Decorators](#class-decorators)
6. [Decorators with Arguments](#decorators-with-arguments)
7. [Built-in Decorators](#built-in-decorators)
8. [Practical Examples](#practical-examples)
9. [Common Mistakes](#common-mistakes)
10. [Real-World Patterns](#real-world-patterns)
11. [Quick Reference](#quick-reference)

---

## What Decorators Actually Are

**Simple Definition:** A decorator is a function that takes another function and extends or modifies its behavior without permanently changing it.

**Core Concept:**
```python
# This decorator...
@timer
def calculate():
    return sum(range(1000))

# ...is just syntactic sugar for this:
def calculate():
    return sum(range(1000))

calculate = timer(calculate)  # Wrap the original function
```

**Mental Model:** Think of decorators like wrapping paper:
- The original function is the gift
- The decorator is the wrapper
- The wrapper adds something (logging, timing, validation)
- You still get the gift inside, just with extras

---

## The @ Syntax Explained

The `@` symbol is just a shorthand that makes code cleaner.

### Without @ syntax
```python
def my_function():
    return "Hello"

my_function = decorator(my_function)
```

### With @ syntax
```python
@decorator
def my_function():
    return "Hello"
```

### Multiple Decorators (Order Matters!)
```python
@decorator1
@decorator2
@decorator3
def my_function():
    pass

# Equivalent to:
my_function = decorator1(decorator2(decorator3(my_function)))
```

**Order:** Bottom-up execution! The decorator closest to the function runs first.

```python
@log_calls      # Applied second (outer wrapper)
@validate_args  # Applied first (inner wrapper)
def process(data):
    return data

# Execution flow:
# 1. validate_args wraps the original function
# 2. log_calls wraps the result from step 1
```

---

## Closures and How They Relate

**Closure:** A function that "remembers" variables from its enclosing scope.

### Closure Example
```python
def outer(x):
    # 'x' is in the outer scope
    def inner(y):
        # 'inner' can access 'x' even after 'outer' returns
        return x + y
    return inner

add_5 = outer(5)
print(add_5(3))  # 8 - 'inner' remembers x=5
```

### How Decorators Use Closures
```python
def repeat(times):
    # 'times' is captured in the closure
    def decorator(func):
        # 'func' is captured in the closure
        def wrapper(*args, **kwargs):
            # Both 'times' and 'func' are accessible here
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello {name}")

greet("Alice")
# Output:
# Hello Alice
# Hello Alice
# Hello Alice
```

**Why This Matters:** Decorators rely on closures to remember the original function and any configuration.

---

## Function Decorators

### Basic Function Decorator
```python
def basic_decorator(func):
    def wrapper(*args, **kwargs):
        # Do something before
        print(f"Calling {func.__name__}")
        
        # Call the original function
        result = func(*args, **kwargs)
        
        # Do something after
        print(f"Finished {func.__name__}")
        
        return result
    return wrapper

@basic_decorator
def greet(name):
    return f"Hello {name}"

greet("Bob")
# Output:
# Calling greet
# Finished greet
```

### Preserving Function Metadata
```python
from functools import wraps

def better_decorator(func):
    @wraps(func)  # Preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@better_decorator
def documented_function():
    """This docstring is preserved."""
    pass

print(documented_function.__name__)  # 'documented_function'
print(documented_function.__doc__)   # 'This docstring is preserved.'
```

**Always use `@wraps(func)`** unless you have a specific reason not to.

---

## Class Decorators

### Decorating Classes (Modify Class Itself)
```python
def add_repr(cls):
    """Adds a __repr__ method to a class."""
    def __repr__(self):
        attrs = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
print(p)  # Point(x=3, y=4)
```

### Decorators as Classes
```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def process():
    return "Processing"

process()  # Call 1 to process
process()  # Call 2 to process
print(process.count)  # 2
```

**Use class decorators when:**
- You need to maintain state (like counting calls)
- The decorator logic is complex
- You want to group related functionality

---

## Decorators with Arguments

### Pattern: Three Levels of Functions
```python
def repeat(times):              # 1. Accepts decorator arguments
    def decorator(func):         # 2. Accepts the function to decorate
        @wraps(func)
        def wrapper(*args, **kwargs):  # 3. Accepts function call arguments
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)  # Calls repeat(3), returns decorator, applies to greet
def greet(name):
    print(f"Hi {name}")
```

### Optional Arguments Pattern
```python
from functools import wraps

def smart_decorator(func=None, *, prefix=">>>"):
    """Can be used with or without arguments."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print(f"{prefix} {f.__name__}")
            return f(*args, **kwargs)
        return wrapper
    
    # Called without arguments: @smart_decorator
    if func is not None:
        return decorator(func)
    
    # Called with arguments: @smart_decorator(prefix="***")
    return decorator

# Both work:
@smart_decorator
def func1():
    pass

@smart_decorator(prefix="***")
def func2():
    pass
```

---

## Built-in Decorators

### @property (Getter/Setter)
```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Get temperature in Celsius."""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Set temperature in Celsius."""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Get temperature in Fahrenheit."""
        return self._celsius * 9/5 + 32

temp = Temperature(25)
print(temp.celsius)      # 25
print(temp.fahrenheit)   # 77.0
temp.celsius = 30        # Uses setter
```

### @staticmethod vs @classmethod
```python
class MathUtils:
    multiplier = 2  # Class variable
    
    @staticmethod
    def add(x, y):
        """Doesn't access class or instance."""
        return x + y
    
    @classmethod
    def create_default(cls):
        """Receives the class as first argument."""
        return cls.multiplier * 10

print(MathUtils.add(5, 3))           # 8
print(MathUtils.create_default())    # 20
```

**When to use:**
- `@staticmethod`: Utility function logically grouped with the class
- `@classmethod`: Factory methods or alternative constructors

### @dataclass (Python 3.7+)
```python
from dataclasses import dataclass, field

@dataclass
class Person:
    name: str
    age: int
    hobbies: list = field(default_factory=list)  # Avoid mutable defaults
    
    def __post_init__(self):
        """Called after __init__."""
        if self.age < 0:
            raise ValueError("Age cannot be negative")

# Automatically gets __init__, __repr__, __eq__
p1 = Person("Alice", 30)
p2 = Person("Alice", 30)
print(p1)         # Person(name='Alice', age=30, hobbies=[])
print(p1 == p2)   # True
```

---

## Practical Examples

### 1. Logging Decorator
```python
import logging
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"{func.__name__} returned {result}")
            return result
        except Exception as e:
            logging.error(f"{func.__name__} raised {e}")
            raise
    return wrapper

@log_calls
def divide(a, b):
    return a / b
```

### 2. Timing Decorator
```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"
```

### 3. Caching/Memoization
```python
from functools import lru_cache

@lru_cache(maxsize=128)  # Built-in caching decorator
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# First call: computes
print(fibonacci(100))  # Fast!

# Second call: cached
print(fibonacci(100))  # Instant!
```

### 4. Validation Decorator
```python
from functools import wraps

def validate_types(**expected_types):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check keyword arguments
            for arg_name, expected_type in expected_types.items():
                if arg_name in kwargs:
                    value = kwargs[arg_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"{arg_name} must be {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int)
def create_user(name, age):
    return {"name": name, "age": age}

create_user(name="Alice", age=30)      # OK
create_user(name="Bob", age="thirty")  # TypeError
```

### 5. Retry Decorator
```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    print(f"Attempt {attempts} failed: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def unstable_api_call():
    # Might fail randomly
    import random
    if random.random() < 0.7:
        raise ConnectionError("API unavailable")
    return {"status": "success"}
```

### 6. Rate Limiting
```python
import time
from functools import wraps

def rate_limit(calls_per_second):
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]  # Use list to allow modification in closure
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)  # Max 2 calls per second
def api_call():
    print(f"API called at {time.time()}")
```

---

## Common Mistakes

### Mistake 1: Forgetting to Return the Wrapper
```python
# WRONG
def broken_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    # Missing: return wrapper

# RIGHT
def correct_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper  # ✓
```

### Mistake 2: Not Using *args, **kwargs
```python
# WRONG - Won't work for functions with different signatures
def bad_decorator(func):
    def wrapper():  # Only works for functions with no arguments
        return func()
    return wrapper

# RIGHT - Works for any function signature
def good_decorator(func):
    def wrapper(*args, **kwargs):  # ✓
        return func(*args, **kwargs)
    return wrapper
```

### Mistake 3: Forgetting @wraps
```python
# WRONG - Loses function metadata
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def my_func():
    """Important docs."""
    pass

print(my_func.__name__)  # 'wrapper' - Wrong!

# RIGHT - Preserves metadata
from functools import wraps

def decorator(func):
    @wraps(func)  # ✓
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### Mistake 4: Decorator Argument Confusion
```python
# WRONG - Missing the third level
def broken_repeat(times):
    def wrapper(*args, **kwargs):
        for _ in range(times):
            result = func(*args, **kwargs)  # 'func' is not defined!
        return result
    return wrapper

# RIGHT - Three levels needed
def working_repeat(times):
    def decorator(func):  # This level captures 'func'
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
```

### Mistake 5: Mutable Default Arguments in Decorators
```python
# WRONG - List is shared across all decorated functions
def track_calls(func, calls=[]):  # Dangerous!
    def wrapper(*args, **kwargs):
        calls.append(time.time())
        return func(*args, **kwargs)
    return wrapper

# RIGHT - Create new list for each decorated function
def track_calls(func):
    calls = []  # New list per function
    def wrapper(*args, **kwargs):
        calls.append(time.time())
        return func(*args, **kwargs)
    wrapper.calls = calls  # Attach to wrapper
    return wrapper
```

---

## Real-World Patterns

### Pattern 1: Transform Decorator (Like Odibi's)
```python
from functools import wraps
from typing import Callable, Any

def transform(transformer: Callable[[Any], Any]):
    """Transforms the output of a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return transformer(result)
        return wrapper
    return decorator

# Usage in data pipeline
@transform(lambda x: x.upper())
def get_username():
    return "alice"

print(get_username())  # "ALICE"

# More complex transformation
@transform(lambda data: [x * 2 for x in data])
def get_scores():
    return [10, 20, 30]

print(get_scores())  # [20, 40, 60]
```

### Pattern 2: Context Manager Decorator
```python
from functools import wraps
import logging

def with_logging_context(func):
    """Wraps function execution in a logging context."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logging.info(f"Completed {func.__name__}")
            return result
        except Exception as e:
            logging.error(f"Failed {func.__name__}: {e}")
            raise
        finally:
            logging.info(f"Cleanup {func.__name__}")
    return wrapper
```

### Pattern 3: Conditional Decorator
```python
def conditional_decorator(condition):
    """Only applies decorator if condition is True."""
    def decorator(func):
        if condition:
            @wraps(func)
            def wrapper(*args, **kwargs):
                print(f"Calling {func.__name__}")
                return func(*args, **kwargs)
            return wrapper
        return func  # Return original if condition is False
    return decorator

# Only log in debug mode
import os
DEBUG = os.getenv("DEBUG") == "1"

@conditional_decorator(DEBUG)
def process():
    return "Processing"
```

### Pattern 4: Decorator Factory with State
```python
class Profiler:
    """Decorator class that maintains profiling state."""
    def __init__(self):
        self.stats = {}
    
    def profile(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            
            if func.__name__ not in self.stats:
                self.stats[func.__name__] = []
            self.stats[func.__name__].append(elapsed)
            
            return result
        return wrapper
    
    def report(self):
        for func_name, times in self.stats.items():
            avg = sum(times) / len(times)
            print(f"{func_name}: avg={avg:.4f}s, calls={len(times)}")

# Usage
profiler = Profiler()

@profiler.profile
def task1():
    time.sleep(0.1)

@profiler.profile
def task2():
    time.sleep(0.2)

task1()
task1()
task2()
profiler.report()
# task1: avg=0.1000s, calls=2
# task2: avg=0.2000s, calls=1
```

### Pattern 5: Stacked Validation
```python
def validate_positive(func):
    @wraps(func)
    def wrapper(value, *args, **kwargs):
        if value <= 0:
            raise ValueError(f"{func.__name__} requires positive value")
        return func(value, *args, **kwargs)
    return wrapper

def validate_type(expected_type):
    def decorator(func):
        @wraps(func)
        def wrapper(value, *args, **kwargs):
            if not isinstance(value, expected_type):
                raise TypeError(f"Expected {expected_type}, got {type(value)}")
            return func(value, *args, **kwargs)
        return wrapper
    return decorator

@validate_type(int)
@validate_positive
def calculate_square(value):
    return value ** 2

calculate_square(5)      # 25
calculate_square(-5)     # ValueError
calculate_square("5")    # TypeError
```

---

## Quick Reference

### Basic Decorator Template
```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Before function call
        result = func(*args, **kwargs)
        # After function call
        return result
    return wrapper
```

### Decorator with Arguments Template
```python
from functools import wraps

def my_decorator(arg1, arg2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use arg1, arg2, func here
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### Class Decorator Template
```python
from functools import wraps

class MyDecorator:
    def __init__(self, func):
        wraps(func)(self)
        self.func = func
    
    def __call__(self, *args, **kwargs):
        # Decorator logic
        return self.func(*args, **kwargs)
```

### Decision Tree: When to Use What

```
Need to modify function behavior?
├─ Is it one-time, simple wrapping?
│  └─ Use function decorator
├─ Need to maintain state across calls?
│  └─ Use class decorator
├─ Need configuration parameters?
│  └─ Use decorator with arguments
└─ Modifying class itself?
   └─ Use class decorator (not function decorator)

Built-in decorators:
├─ Making class attribute act like attribute but computed? → @property
├─ Don't need instance or class data? → @staticmethod
├─ Need class reference for factory/alternative constructor? → @classmethod
├─ Want auto-generated __init__, __repr__, __eq__? → @dataclass
└─ Need memoization? → @lru_cache
```

### Common Use Cases Cheat Sheet

| Use Case | Decorator |
|----------|-----------|
| Measure execution time | `@timer` |
| Cache results | `@lru_cache` |
| Log function calls | `@log_calls` |
| Retry on failure | `@retry` |
| Validate inputs | `@validate` |
| Require authentication | `@requires_auth` |
| Limit call rate | `@rate_limit` |
| Make attribute computed | `@property` |
| Factory method | `@classmethod` |
| Utility function | `@staticmethod` |
| Auto-generate class methods | `@dataclass` |

---

## Key Takeaways

1. **Decorators are just functions** that wrap other functions
2. **The @ syntax** is syntactic sugar for `func = decorator(func)`
3. **Always use @wraps(func)** to preserve function metadata
4. **Use *args, **kwargs** to support any function signature
5. **Three levels** needed for decorators with arguments
6. **Order matters** when stacking decorators (bottom-up)
7. **Closures** are what make decorators remember the original function
8. **Class decorators** are useful when you need to maintain state
9. **Don't overuse** decorators—keep them simple and focused

**Remember:** Decorators should make code more readable and maintainable. If a decorator is too complex, consider a different approach!
