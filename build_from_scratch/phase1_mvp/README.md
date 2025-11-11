# Phase 1: MVP

**Goal:** Build a minimal working pipeline framework in ~200 lines

---

## What You'll Build

A simple but functional data pipeline framework:

```python
# Your framework
from my_framework import Pipeline, Node

pipeline = Pipeline()
pipeline.add_node(Node(
    name="load",
    read="data/input.csv"
))
pipeline.add_node(Node(
    name="clean",
    depends_on=["load"],
    transform=lambda df: df[df['amount'] > 0]
))
pipeline.add_node(Node(
    name="save",
    depends_on=["clean"],
    write="data/output.parquet"
))

pipeline.run()  # ✅ Works!
```

---

## Requirements

**Must have:**
- [x] Read CSV/Parquet from local files
- [x] Transform with Python functions
- [x] Write to local files (CSV/Parquet)
- [x] Sequential execution (simple dependency order)
- [x] Basic error handling
- [x] Tests for all components

**Nice to have:**
- Context for passing data between nodes
- Config validation
- Logging

---

## Architecture

```
my_framework/
├── __init__.py
├── node.py         # Node class (read → transform → write)
├── pipeline.py     # Pipeline class (orchestrates nodes)
├── context.py      # Context class (data passing)
└── exceptions.py   # Custom exceptions

tests/
├── test_node.py
├── test_pipeline.py
└── test_context.py

examples/
└── simple_pipeline.py
```

---

## Tasks

**Week 1 Checklist:**

### Day 1-2: Setup & Node
- [ ] Create project structure
- [ ] Implement Context (dict-based storage)
- [ ] Implement Node (read, transform, write)
- [ ] Write Node tests
- [ ] Test: Load CSV → transform → save Parquet

### Day 3-4: Pipeline
- [ ] Implement Pipeline class
- [ ] Simple dependency resolution (no DAG yet)
- [ ] Execute nodes in order
- [ ] Write Pipeline tests
- [ ] Test: 3-node pipeline works

### Day 5: Polish
- [ ] Add error handling
- [ ] Add logging
- [ ] Create example pipeline
- [ ] Documentation
- [ ] Code review yourself

---

## Success Criteria

You can run this and it works:

```python
from my_framework import Pipeline, Node

# Bronze → Silver → Gold
pipeline = Pipeline()

pipeline.add_node(Node(
    name="bronze",
    read="raw/sales.csv",
    transform=lambda df: df.dropna()
))

pipeline.add_node(Node(
    name="silver", 
    depends_on=["bronze"],
    transform=lambda df: df[df['amount'] > 0]
))

pipeline.add_node(Node(
    name="gold",
    depends_on=["silver"],
    transform=lambda df: df.groupby('product').agg({'amount': 'sum'}),
    write="outputs/summary.parquet"
))

results = pipeline.run()
print(f"✅ {len(results)} nodes executed")
```

---

## Hints

1. Start with Context - it's the simplest
2. Node should use pandas directly (no abstraction yet)
3. Pipeline just loops through nodes in order (no graph yet)
4. Use pytest fixtures for sample data
5. Refer to: foundations/01, 02, 04

---

## Next Phase

Once this works, move to [Phase 2: Dependency Graph](../phase2_graph/) to add proper DAG-based execution.
