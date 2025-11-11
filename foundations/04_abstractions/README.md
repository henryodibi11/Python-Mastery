# 04 - Abstractions

**Learning Goal**: Master abstraction patterns for building flexible, extensible systems.

## Topics Covered

1. **Abstract Base Classes (ABC)**
   - `@abstractmethod` decorator
   - Enforcing contracts at instantiation
   - When ABC is the right choice

2. **Protocol (Structural Subtyping)**
   - `@runtime_checkable` protocols
   - Duck typing with type safety
   - Working with external types

3. **Composition Over Inheritance**
   - Wrapper/decorator pattern
   - Mixing behaviors flexibly
   - Avoiding rigid hierarchies

4. **Interface Design Patterns**
   - Factory pattern for implementation selection
   - Strategy pattern for swappable algorithms
   - Dependency inversion principle

5. **Odibi's Abstraction Architecture**
   - Engine ABC: Pandas vs Spark
   - Connection ABC: File vs Database
   - Context ABC: Different storage strategies

## Files

- **lesson.ipynb**: Main lesson with theory, examples, and Odibi analysis
- **exercises.ipynb**: Hands-on practice building your own abstractions
- **solutions.ipynb**: Reference implementations
- **odibi_abstractions.md**: Deep dive into Odibi's architecture

## Key Concepts

### The Problem
Without abstractions, adding new implementations requires modifying existing code (if/else chains).

### The Solution
Define interfaces once, implement many times. Depend on abstractions, not concretions.

### ABC vs Protocol

| ABC | Protocol |
|-----|----------|
| Explicit inheritance | Structural typing |
| Enforced at class definition | Checked by type checker |
| Use when you control implementations | Use with external types |
| Runtime errors for incomplete implementations | Type errors at check time |

## Real-World Application: Odibi

Odibi uses ABC to enable multi-engine support:

```python
class Engine(ABC):
    @abstractmethod
    def read(self, connection, format, ...): ...
    
    @abstractmethod
    def write(self, df, connection, ...): ...

# Implementations
class PandasEngine(Engine): ...
class SparkEngine(Engine): ...
```

**Result**: Same pipeline code works with Pandas or Spark by swapping the engine.

## Prerequisites

- Foundations 01: Type System (understanding type hints)
- Foundations 02: Data Classes (dataclass patterns)
- Basic understanding of inheritance

## Next Module

**05 - Functional Programming**: Immutability, pure functions, higher-order patterns
