# 03: Odibi Engine Abstraction Deep Dive

## 🎯 Goal

Master Odibi's engine abstraction layer: how a single ABC enables seamless swapping between Pandas, Spark, and DuckDB without changing pipeline code.

## 📋 Overview

This is the **architecture deep dive** that reveals Odibi's superpower: write once, run anywhere.
- Single `Engine` ABC defines the contract
- PandasEngine, SparkEngine implement the same interface
- Pipeline code stays identical regardless of execution engine
- Switch engines with a single config change

**First Principles:**
- ✅ **Abstraction** - hide implementation details behind a stable interface
- ✅ **Polymorphism** - treat different engines uniformly
- ✅ **Dependency Inversion** - depend on abstractions, not concrete implementations
- ✅ **Open/Closed** - open for extension (new engines), closed for modification

## 📚 What You'll Learn

### Core Architecture
1. **Engine ABC**: The 9 abstract methods that define an engine
2. **PandasEngine**: In-memory, single-node implementation
3. **SparkEngine**: Distributed, lazy-evaluation implementation
4. **Engine Factory**: How Odibi selects the right engine at runtime

### Abstraction Benefits
5. **Interface Stability**: Why the ABC hasn't changed in 2+ years
6. **Engine Swapping**: Switch from Pandas → Spark with zero code changes
7. **Testing**: Mock engines for unit tests
8. **Extensibility**: Build custom engines (DuckDB, Polars, etc.)

### Implementation Deep Dive
9. **read()**: How each engine handles CSV, Parquet, Delta formats
10. **write()**: Mode handling (overwrite/append) across engines
11. **execute_sql()**: DuckDB for Pandas, Spark SQL for Spark
12. **Storage Options**: Cloud credential handling per engine

## 🗂️ Files

- **lesson.ipynb** - Main interactive lesson (start here!)
- **exercises.ipynb** - Build DuckDBEngine from scratch
- **solutions.ipynb** - Reference solutions
- **engine_comparison.md** - Side-by-side engine comparison table

## 🔍 Real Code Analysis

This lesson uses **actual Odibi production code**:
- Source: `c:/Users/hodibi/OneDrive - Ingredion/Desktop/Repos/Odibi/odibi/engine/`
- `base.py` - 146 lines defining the Engine ABC
- `pandas_engine.py` - 571 lines of Pandas implementation
- `spark_engine.py` - 293 lines of Spark implementation

## 🎓 Prerequisites

From `odibi_deep_dive/`:
- `01_config_system` - Must understand EngineType enum
- `02_connection_layer` - Must know how connections work

From `foundations/`:
- `06_abc` - Must master abstract base classes

## ⏱️ Time Estimate

- Lesson: 90-120 minutes
- Exercises: 90-120 minutes (building DuckDBEngine)
- Total: 3-4 hours

## 🚀 Getting Started

```bash
jupyter lab lesson.ipynb
```

Or use VS Code with Jupyter extension.

## 💡 Key Takeaways

After this lesson, you'll understand:
1. How abstraction enables code reusability and flexibility
2. Why the Engine ABC is the foundation of Odibi's portability
3. How different engines implement the same operations differently
4. The tradeoffs between Pandas (simple) and Spark (scalable)
5. How to design your own engine implementations

## 🏗️ Exercise Preview

You'll build a **DuckDBEngine** that:
- Implements the Engine ABC
- Uses DuckDB for in-process analytical queries
- Supports reading CSV, Parquet, and Delta
- Leverages DuckDB's zero-copy integration with Pandas
- Demonstrates a third execution model alongside Pandas and Spark

---

**Next**: After mastering engines, move to `04_context_api/` to see how engines receive data from the context.
