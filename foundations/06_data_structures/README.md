# Data Structures: Graphs & Dependency Resolution

Master graph algorithms essential for pipeline execution and dependency management.

## 🎯 Learning Objectives

1. **Graph Theory Fundamentals**
   - Directed graphs and DAGs (Directed Acyclic Graphs)
   - Adjacency lists vs matrices
   - Graph representation tradeoffs

2. **Graph Traversal**
   - Depth-First Search (DFS)
   - Breadth-First Search (BFS)
   - Cycle detection

3. **Topological Sorting**
   - Kahn's algorithm
   - DFS-based topological sort
   - Dependency ordering

4. **Dependency Resolution**
   - Build dependency graphs
   - Detect circular dependencies
   - Calculate execution layers for parallel processing

5. **Odibi's DependencyGraph**
   - Analyze production-grade graph implementation
   - Understand execution layer generation
   - Learn validation strategies

## 📚 Files

- **lesson.ipynb** - Main tutorial with theory and examples
- **exercises.ipynb** - Practice problems
- **solutions.ipynb** - Complete solutions
- **odibi_graph_analysis.md** - Deep dive into Odibi's implementation

## 🔑 Key Concepts

### DAG (Directed Acyclic Graph)
A directed graph with no cycles - perfect for dependency management.

### Topological Sort
Linear ordering of vertices such that for every edge u→v, u comes before v.

### Kahn's Algorithm
1. Find nodes with in-degree 0
2. Process them, reducing in-degree of dependents
3. Repeat until all nodes processed

### Execution Layers
Group independent nodes for parallel execution.

## 💡 Why This Matters

- **Pipeline Execution**: Nodes must run in correct dependency order
- **Parallel Processing**: Identify which nodes can run simultaneously
- **Validation**: Detect circular dependencies before execution
- **Debugging**: Understand data flow through the system

## 🚀 Getting Started

Start with [lesson.ipynb](lesson.ipynb) for a complete walkthrough.
