# 01: Python Type System & Validation

## 🎯 Objectives

By the end of this lesson, you will:

1. **Understand Python's Type System**
   - Static vs dynamic typing
   - Gradual typing with type hints
   - Type checking with mypy

2. **Master Type Annotations**
   - Primitives: `int`, `str`, `bool`, `float`
   - Collections: `List`, `Dict`, `Set`, `Tuple`
   - Advanced: `Optional`, `Union`, `Literal`
   - Callable and generic types

3. **Build Validated Models with Pydantic**
   - BaseModel fundamentals
   - Field validation and constraints
   - Custom validators
   - Model composition

4. **Apply to Real-World Data Engineering**
   - Analyze Odibi's configuration system
   - Implement fail-fast validation
   - Create type-safe config models
   - Handle nested configurations

## 📚 Prerequisites

- Basic Python knowledge
- Understanding of classes and inheritance
- Familiarity with dictionaries and lists

## 🗂️ Files

- **lesson.ipynb** - Main interactive lesson
- **exercises.ipynb** - Practice problems
- **solutions.ipynb** - Exercise solutions
- **odibi_snippets.py** - Real-world examples from Odibi

## 🚀 Getting Started

1. Ensure you have the required packages:
   ```bash
   pip install pydantic mypy
   ```

2. Open `lesson.ipynb` in Jupyter:
   ```bash
   jupyter notebook lesson.ipynb
   ```

3. Work through each section, running the code cells

4. Complete the exercises in `exercises.ipynb`

5. Check your work against `solutions.ipynb`

## 🔑 Key Concepts

### Why Type Hints Matter for Data Engineering

- **Fail Fast**: Catch errors before runtime
- **Self-Documentation**: Code explains itself
- **IDE Support**: Better autocomplete and refactoring
- **Maintainability**: Easier to understand complex configs
- **Runtime Validation**: Pydantic validates at runtime

### Pydantic vs Dataclasses

| Feature | Dataclasses | Pydantic |
|---------|-------------|----------|
| Type hints | Yes | Yes |
| Runtime validation | No | **Yes** |
| Parsing/coercion | No | **Yes** |
| JSON serialization | Manual | **Built-in** |
| Custom validators | Manual | **Decorators** |
| Performance | Faster | Good enough |

**For data engineering**: Use Pydantic for configs, dataclasses for simple DTOs

## 💡 Real-World Application

The Odibi framework uses Pydantic extensively for:
- Connection configurations (Azure, Delta, SQL Server)
- Node definitions (Read, Transform, Write)
- Pipeline orchestration
- Validation rules

This ensures data pipelines fail fast with clear error messages, not hours into execution.

## 📖 Additional Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [mypy Documentation](https://mypy.readthedocs.io/)
