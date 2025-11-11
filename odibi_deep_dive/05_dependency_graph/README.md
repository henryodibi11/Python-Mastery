# 05 - Dependency Graph Deep Dive

## Overview

Master the `DependencyGraph` class - the brain of Odibi's pipeline execution engine. This lesson builds directly on [foundations/06_data_structures](../../foundations/06_data_structures/) to show how graph theory enables reliable pipeline orchestration.

## 🎯 The Problem

Given a set of pipeline nodes with dependencies, determine:
1. **Safe execution order** - which nodes must run before others
2. **Parallel execution opportunities** - which nodes can run simultaneously
3. **Dependency violations** - cycles, missing nodes, invalid references

Example pipeline:
```
extract_raw → clean_data → aggregate → report
                ↓
            validate_schema
```

Questions:
- What order should nodes execute?
- Can `validate_schema` and `aggregate` run in parallel?
- What happens if `report` depends on `extract_raw`?

## 🦉 First Principles

### Directed Acyclic Graph (DAG)
- **Directed**: Dependencies flow in one direction (A → B means "A must run before B")
- **Acyclic**: No circular dependencies (prevents deadlock)
- **Graph**: Nodes connected by edges (dependencies)

### Key Guarantees
1. **Topological Sort**: DAG guarantees at least one valid execution order
2. **Execution Layers**: Nodes with same depth can run in parallel
3. **Cycle Detection**: If cycle exists, no valid execution order possible

### Why This Matters
- **Data pipelines**: Wrong execution order = wrong results
- **Build systems**: Compile dependencies in correct sequence
- **Task schedulers**: Maximize parallelism while respecting constraints

## 📚 Learning Path

1. **Read `lesson.ipynb`** - Complete `DependencyGraph` implementation walkthrough
2. **Complete `exercises.ipynb`** - Build your own graph from scratch
3. **Challenge yourself** - Add advanced features (critical path, graph diff)
4. **Explore `advanced_graph_algorithms.md`** - Performance optimizations

## 🔗 Connections

**Builds on:**
- `foundations/06_data_structures` - Graph theory fundamentals
- `odibi_deep_dive/02_config_system` - NodeConfig structure

**Enables:**
- `odibi_deep_dive/07_pipeline` - Actual pipeline execution
- `odibi_deep_dive/08_orchestration` - Advanced scheduling

## 🎓 Key Concepts

### Graph Representation
```python
# Adjacency list: node → list of dependents
adjacency_list = {
    'extract': ['clean', 'validate'],
    'clean': ['aggregate'],
    'validate': [],
    'aggregate': ['report']
}

# Reverse: node → list of dependencies
reverse_adjacency_list = {
    'extract': [],
    'clean': ['extract'],
    'validate': ['extract'],
    'aggregate': ['clean'],
    'report': ['aggregate']
}
```

### Topological Sort (Kahn's Algorithm)
```
1. Find all nodes with in-degree 0 (no dependencies)
2. Process these nodes, removing their edges
3. Repeat until all nodes processed
4. If nodes remain, cycle detected
```

### Execution Layers
```
Layer 1: [extract]           # No dependencies
Layer 2: [clean, validate]   # Depend only on Layer 1
Layer 3: [aggregate]         # Depends on Layer 2
Layer 4: [report]            # Depends on Layer 3
```

## 📁 Files

- **README.md** (this file) - Overview and concepts
- **lesson.ipynb** - Complete implementation walkthrough
- **exercises.ipynb** - Build it yourself with tests
- **solutions.ipynb** - Reference implementations
- **advanced_graph_algorithms.md** - Optimization techniques

## 🚀 Quick Start

```bash
# From Python-Mastery root
cd odibi_deep_dive/05_dependency_graph
jupyter notebook lesson.ipynb
```

## 💡 Real-World Applications

- **Data Engineering**: Airflow, Dagster, Prefect DAGs
- **Build Systems**: Make, Bazel dependency resolution
- **Package Managers**: npm, pip dependency installation
- **CI/CD**: GitHub Actions, CircleCI job ordering

---

**Next:** `06_error_handling` - Graceful failure and recovery strategies
