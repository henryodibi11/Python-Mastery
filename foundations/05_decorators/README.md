# Python Decorators

Master function enhancement patterns used in Odibi's transformation registry.

## 🎯 What You'll Learn

- Function decorators basics (wrapping functions)
- Decorators with arguments
- Decorator factories
- Class decorators
- functools.wraps (preserving metadata)
- Context managers (@contextmanager)
- Property decorators
- **Odibi's @transformation decorator** (registry pattern)

## 📁 Files

- **lesson.ipynb** - Main lesson with theory and examples
- **exercises.ipynb** - Practice exercises
- **solutions.ipynb** - Exercise solutions
- **odibi_transform_decorator.md** - Deep dive into Odibi's decorator pattern

## 🔍 Real-World Application

Odibi uses decorators extensively:
- `@transformation` - Register functions in global registry
- `.explain` - Add documentation to transformations
- Context passing with **kwargs
- Validation and metadata management

## 🚀 Quick Start

1. Open `lesson.ipynb`
2. Follow along with examples
3. Complete `exercises.ipynb`
4. Study `odibi_transform_decorator.md` to see production patterns

## 💡 Key Concepts

**Decorators** = Functions that wrap functions to add behavior (logging, validation, registration)

```python
@timer
def process_data():
    # Function is automatically timed
    pass
```

**Decorator factories** = Functions that return decorators (for arguments)

```python
@retry(max_attempts=3)
def fetch_data():
    # Function retries automatically
    pass
```

**Registry pattern** = Decorators register functions in global dict

```python
@transformation("filter_records")
def my_transform(df, threshold):
    return df[df.value > threshold]
```
