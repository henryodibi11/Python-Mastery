# Odibi DependencyGraph Analysis

Deep dive into Odibi's production graph implementation.

## 📍 Location
`c:/Users/hodibi/OneDrive - Ingredion/Desktop/Repos/Odibi/odibi/graph.py`

## 🏗️ Architecture

### Data Structures

```python
self.nodes: Dict[str, NodeConfig]           # Node name -> config
self.adjacency_list: Dict[str, List[str]]   # Node -> dependents
self.reverse_adjacency_list: Dict[str, List[str]]  # Node -> dependencies
```

**Why both adjacency lists?**
- `adjacency_list`: Forward edges (dependency → dependent) for topological sort
- `reverse_adjacency_list`: Backward edges (dependent → dependency) for querying dependencies

## 🔍 Key Algorithms

### 1. Graph Construction (`_build_graph`)

```python
for node in self.nodes.values():
    for dependency in node.depends_on:
        # Forward edge: dependency -> node
        self.adjacency_list[dependency].append(node.name)
        # Reverse edge: node -> dependency
        self.reverse_adjacency_list[node.name].append(dependency)
```

**Edge direction**: `dependency → node` (data flows from dependency to dependent)

### 2. Cycle Detection (`_check_cycles`)

**Algorithm**: DFS with recursion stack
- **visited**: Nodes fully processed
- **rec_stack**: Nodes in current DFS path
- **Cycle detected**: Node found in `rec_stack`

**Why DFS?** Cycles exist if we revisit a node in the current path.

```python
def visit(node: str, path: List[str]) -> Optional[List[str]]:
    if node in rec_stack:  # Back edge = cycle
        cycle_start = path.index(node)
        return path[cycle_start:] + [node]
    
    if node in visited:  # Already processed
        return None
    
    visited.add(node)
    rec_stack.add(node)
    path.append(node)
    
    for dependent in self.adjacency_list[node]:
        cycle = visit(dependent, path[:])
        if cycle:
            return cycle
    
    rec_stack.remove(node)  # Backtrack
    return None
```

### 3. Topological Sort (`topological_sort`)

**Algorithm**: Kahn's Algorithm (BFS-based)

**Steps**:
1. Calculate in-degree (number of dependencies) for each node
2. Queue all nodes with in-degree 0 (no dependencies)
3. Process queue:
   - Remove node from queue
   - Add to sorted list
   - Decrease in-degree of all dependents
   - If dependent's in-degree becomes 0, add to queue

**Time Complexity**: O(V + E)

```python
# Calculate in-degrees
in_degree = {name: 0 for name in self.nodes.keys()}
for node in self.nodes.values():
    for dependency in node.depends_on:
        in_degree[node.name] += 1

# Queue nodes with no dependencies
queue = deque([name for name, degree in in_degree.items() if degree == 0])
sorted_nodes = []

while queue:
    node_name = queue.popleft()
    sorted_nodes.append(node_name)
    
    # Reduce in-degree for dependents
    for dependent in self.adjacency_list[node_name]:
        in_degree[dependent] -= 1
        if in_degree[dependent] == 0:
            queue.append(dependent)
```

### 4. Execution Layers (`get_execution_layers`)

**Purpose**: Group nodes that can run in parallel

**Key Insight**: Nodes in same layer have no dependencies on each other

**Algorithm**:
1. Find all nodes with in-degree 0 → Layer 1
2. Remove Layer 1, recalculate in-degrees
3. Find nodes with in-degree 0 → Layer 2
4. Repeat until all nodes placed

```python
layers = []
remaining = set(self.nodes.keys())

while remaining:
    # Nodes with no dependencies in remaining set
    current_layer = [name for name in remaining if in_degree[name] == 0]
    
    if not current_layer:
        raise DependencyError("Cannot create execution layers (likely cycle)")
    
    layers.append(current_layer)
    
    for node_name in current_layer:
        remaining.remove(node_name)
        
        # Reduce in-degree for dependents
        for dependent in self.adjacency_list[node_name]:
            if dependent in remaining:
                in_degree[dependent] -= 1

return layers
```

**Example**:
```
Layer 1: [A, B]      # No dependencies
Layer 2: [C, D]      # Depend only on A, B
Layer 3: [E]         # Depends on C, D
```

### 5. Dependency Queries

**Get all dependencies** (`get_dependencies`):
- BFS from node using `reverse_adjacency_list`
- Returns transitive closure of dependencies

**Get all dependents** (`get_dependents`):
- BFS from node using `adjacency_list`
- Returns all nodes that depend on this node

## 🎯 Design Patterns

### 1. Validation in Constructor
Graph validates itself during construction:
- Check missing dependencies
- Detect cycles
- Fail fast before any operations

### 2. Bidirectional Adjacency
Maintain both forward and reverse edges for efficient queries:
- Forward: "What depends on this node?"
- Reverse: "What does this node depend on?"

### 3. Separation of Concerns
- `_build_graph()`: Construction
- `_validate_graph()`: Validation
- `topological_sort()`: Ordering
- `get_execution_layers()`: Parallelization

## 📊 Time Complexities

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Build graph | O(V + E) | O(V + E) |
| Cycle detection | O(V + E) | O(V) |
| Topological sort | O(V + E) | O(V) |
| Execution layers | O(V + E) | O(V) |
| Get dependencies | O(V + E) | O(V) |

Where:
- V = number of nodes
- E = number of edges (dependencies)

## 💡 Key Takeaways

1. **DAGs are perfect for dependencies** - No cycles means clear execution order
2. **Kahn's algorithm is elegant** - Simple BFS-based topological sort
3. **Execution layers enable parallelism** - Group independent nodes
4. **Validation is critical** - Catch errors before execution
5. **Bidirectional graphs optimize queries** - Store both directions for O(1) access

## 🔧 Usage in Odibi Pipeline

1. **Parse YAML** → Create `NodeConfig` objects
2. **Build graph** → `DependencyGraph(nodes)`
3. **Validate** → Automatic in constructor
4. **Get layers** → `graph.get_execution_layers()`
5. **Execute** → Run each layer in parallel, layers in sequence

This ensures:
- Correct execution order
- Maximum parallelism
- Early error detection
- Clear dependency visualization
