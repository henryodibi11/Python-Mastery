# Phase 2: Dependency Graph

**Goal:** Add proper dependency resolution using DAG + topological sort

---

## What You'll Add

Replace simple sequential execution with graph-based dependency resolution:

```python
# Phase 1: Nodes run in order you add them ❌
pipeline.add_node(...)  # Runs first
pipeline.add_node(...)  # Runs second

# Phase 2: Nodes run based on dependencies ✅
pipeline.add_node(Node(name="C", depends_on=["A", "B"]))  # Runs after A and B
pipeline.add_node(Node(name="A"))  # Runs first (no deps)
pipeline.add_node(Node(name="B"))  # Runs first (no deps)

# C waits for both A and B, order doesn't matter!
```

---

## Requirements

**Must add:**
- [x] DependencyGraph class (from foundations/06)
- [x] Topological sort for execution order
- [x] Cycle detection with clear errors
- [x] Execution layers (identify parallelizable nodes)
- [x] Update Pipeline to use graph

**Tests:**
- [x] Test cycle detection
- [x] Test complex dependency scenarios
- [x] Test execution order correctness

---

## Architecture Changes

```diff
my_framework/
├── __init__.py
├── node.py
├── pipeline.py
├── context.py
+ ├── graph.py          # NEW: DependencyGraph class
├── exceptions.py
```

---

## Tasks

**Week 2 Checklist:**

### Day 1-2: Implement Graph
- [ ] Create graph.py with DependencyGraph class
- [ ] Implement add_node, add_edge
- [ ] Implement topological_sort (Kahn's algorithm)
- [ ] Implement cycle detection
- [ ] Write graph tests (lots of them!)

### Day 3: Execution Layers
- [ ] Implement get_execution_layers
- [ ] Test layer calculation
- [ ] Document how parallel execution would work (don't implement yet)

### Day 4: Integrate with Pipeline
- [ ] Update Pipeline to build graph from nodes
- [ ] Use topological sort for execution order
- [ ] Handle graph errors (cycles, missing deps)
- [ ] Update pipeline tests

### Day 5: Edge Cases
- [ ] Test diamond dependencies (A → B,C → D)
- [ ] Test long chains
- [ ] Test disconnected graphs
- [ ] Update examples

---

## Success Criteria

This pipeline detects the cycle and fails with a clear error:

```python
pipeline = Pipeline()
pipeline.add_node(Node(name="A", depends_on=["C"]))
pipeline.add_node(Node(name="B", depends_on=["A"]))
pipeline.add_node(Node(name="C", depends_on=["B"]))

pipeline.run()  # ❌ DependencyError: Cycle detected: A → B → C → A
```

This pipeline executes in correct order (B,C first, then A):

```python
pipeline = Pipeline()
pipeline.add_node(Node(name="A", depends_on=["B", "C"]))  # Added first
pipeline.add_node(Node(name="C"))  # Added second
pipeline.add_node(Node(name="B"))  # Added third

# Execution order: C, B, then A (or B, C, then A)
pipeline.run()  # ✅ Works!
```

---

## Hints

1. Copy your graph implementation from foundations/06
2. Pipeline.run() should:
   - Build graph from node dependencies
   - Validate graph (check for cycles)
   - Get execution order from topological sort
   - Execute nodes in that order
3. Don't implement parallel execution yet - just calculate layers
4. Use exceptions from exceptions.py for graph errors

---

## Next Phase

Once graph works, move to [Phase 3: Engine Abstraction](../phase3_abstraction/) to support Spark.
