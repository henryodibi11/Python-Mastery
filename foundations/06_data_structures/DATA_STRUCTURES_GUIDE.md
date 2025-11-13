# Data Structures Deep Dive: Choosing the Right Tool

This guide helps you understand Python's data structures, when to use each one, and how they perform.

## Table of Contents
1. [Core Data Structures Overview](#core-data-structures-overview)
2. [When to Use Each Structure](#when-to-use-each-structure)
3. [Time Complexity Comparisons](#time-complexity-comparisons)
4. [Memory Usage Patterns](#memory-usage-patterns)
5. [Common Operations & Best Practices](#common-operations--best-practices)
6. [Collections Module Structures](#collections-module-structures)
7. [Graph Representations](#graph-representations)
8. [Trees and Recursive Structures](#trees-and-recursive-structures)
9. [Performance Pitfalls](#performance-pitfalls)
10. [Real-World Examples](#real-world-examples)
11. [Quick Reference](#quick-reference)

---

## Core Data Structures Overview

### List - Dynamic Array
```python
# Ordered, mutable, allows duplicates
numbers = [1, 2, 3, 2, 1]
numbers.append(4)       # Add to end
numbers.insert(0, 0)    # Insert at position
numbers.pop()           # Remove from end
numbers.remove(2)       # Remove first occurrence
```

**Best for:**
- Ordered collections
- Frequent appending to end
- Index-based access
- When you need to maintain insertion order

### Tuple - Immutable Sequence
```python
# Ordered, immutable, allows duplicates
coordinates = (10, 20)
x, y = coordinates      # Unpacking

# Good for dictionary keys (if hashable)
locations = {
    (0, 0): "origin",
    (1, 1): "diagonal"
}
```

**Best for:**
- Data that shouldn't change
- Dictionary keys or set elements
- Function return values (multiple values)
- Memory efficiency vs lists

### Set - Unordered Collection
```python
# Unordered, mutable, unique elements only
unique_ids = {1, 2, 3, 2}  # {1, 2, 3}
unique_ids.add(4)
unique_ids.discard(2)
unique_ids.remove(3)       # Raises KeyError if missing

# Set operations
a = {1, 2, 3}
b = {2, 3, 4}
a & b  # Intersection: {2, 3}
a | b  # Union: {1, 2, 3, 4}
a - b  # Difference: {1}
a ^ b  # Symmetric difference: {1, 4}
```

**Best for:**
- Removing duplicates
- Membership testing
- Set operations (union, intersection)
- When order doesn't matter

### Dict - Key-Value Mapping
```python
# Ordered (Python 3.7+), mutable, unique keys
user = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

user["age"] = 31           # Update
user.get("phone", "N/A")   # Safe access with default
user.setdefault("role", "user")  # Set if not exists

# Dictionary comprehension
squares = {x: x**2 for x in range(5)}
```

**Best for:**
- Fast lookups by key
- Counting occurrences
- Caching/memoization
- Configuration data

---

## When to Use Each Structure

### Decision Tree

```
What do you need?

Fast lookups by key?
├─ Keys are simple (str, int)? → dict
├─ Need default values? → defaultdict
└─ Counting occurrences? → Counter

Unique elements only?
├─ Need set operations? → set
├─ Immutable version? → frozenset
└─ Fast membership testing? → set

Ordered collection?
├─ Need to modify? → list
├─ Never changes? → tuple
├─ Need fast left/right operations? → deque
└─ Priority-based access? → heapq

Key-value pairs?
├─ Need default factory? → defaultdict
├─ Need ordered by insertion? → dict (Python 3.7+)
├─ Need ordered by key? → dict + sorted() or SortedDict
└─ Need to count? → Counter
```

### Concrete Scenarios

| Scenario | Best Choice | Why |
|----------|-------------|-----|
| Store user IDs (no duplicates) | `set` | Fast membership, automatic uniqueness |
| Cache function results | `dict` | O(1) lookup by input parameters |
| Process items FIFO | `deque` | O(1) append/pop from both ends |
| Track word frequencies | `Counter` | Built-in counting logic |
| Config with defaults | `defaultdict` | Automatic default values |
| Coordinate pairs | `tuple` | Immutable, hashable for dict keys |
| Undo/redo stack | `list` | Simple append/pop from end |
| Task priority queue | `heapq` | Efficient min-heap operations |
| Graph adjacency list | `dict[node, list]` | Fast neighbor lookup |
| LRU cache | `OrderedDict` | Maintains order for eviction |

---

## Time Complexity Comparisons

### List Operations
| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `list[i]` | O(1) | Direct index access |
| `list.append(x)` | O(1) amortized | Might resize array |
| `list.insert(0, x)` | O(n) | Shifts all elements |
| `list.pop()` | O(1) | Remove from end |
| `list.pop(0)` | O(n) | Shifts all elements |
| `x in list` | O(n) | Linear search |
| `list.sort()` | O(n log n) | Timsort algorithm |

### Set Operations
| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `x in set` | O(1) average | Hash table lookup |
| `set.add(x)` | O(1) average | Hash table insert |
| `set.remove(x)` | O(1) average | Hash table delete |
| `set1 & set2` | O(min(len(set1), len(set2))) | Intersection |
| `set1 \| set2` | O(len(set1) + len(set2)) | Union |

### Dict Operations
| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `dict[key]` | O(1) average | Hash table lookup |
| `dict[key] = value` | O(1) average | Hash table insert |
| `del dict[key]` | O(1) average | Hash table delete |
| `key in dict` | O(1) average | Check key existence |
| `dict.items()` | O(n) | Iterate all items |

### Deque Operations
| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `deque.append(x)` | O(1) | Add to right |
| `deque.appendleft(x)` | O(1) | Add to left |
| `deque.pop()` | O(1) | Remove from right |
| `deque.popleft()` | O(1) | Remove from left |
| `deque[i]` | O(n) | Not optimized for indexing |

---

## Memory Usage Patterns

### Memory Overhead
```python
import sys

# Lists have overhead for dynamic resizing
list_100 = list(range(100))
print(sys.getsizeof(list_100))  # ~920 bytes

# Tuples are more memory efficient
tuple_100 = tuple(range(100))
print(sys.getsizeof(tuple_100))  # ~864 bytes

# Sets have hash table overhead
set_100 = set(range(100))
print(sys.getsizeof(set_100))  # ~4272 bytes

# Dicts have more overhead (keys + values + hash table)
dict_100 = {i: i for i in range(100)}
print(sys.getsizeof(dict_100))  # ~5088 bytes
```

### Memory Tips
```python
# ✗ BAD - Creates intermediate lists
result = list(range(1000000))  # Loads all into memory
processed = [x * 2 for x in result]

# ✓ GOOD - Use generators for large datasets
result = range(1000000)  # Generator, no memory
processed = (x * 2 for x in result)  # Generator expression

# ✗ BAD - Duplicate storage
original = [1, 2, 3, 4, 5]
copy1 = original  # Just a reference
copy2 = original  # Same reference

# ✓ GOOD - Intentional copying when needed
original = [1, 2, 3, 4, 5]
shallow_copy = original.copy()  # or original[:]
import copy
deep_copy = copy.deepcopy(original)  # For nested structures
```

---

## Common Operations & Best Practices

### List Best Practices
```python
# ✓ GOOD - Preallocate if size known
data = [0] * 1000  # Better than appending 1000 times

# ✓ GOOD - List comprehension
squares = [x**2 for x in range(10)]

# ✗ BAD - Repeated concatenation
result = []
for i in range(1000):
    result = result + [i]  # Creates new list each time!

# ✓ GOOD - Use append
result = []
for i in range(1000):
    result.append(i)

# ✓ GOOD - Extend for multiple items
result.extend([1, 2, 3])

# ✓ GOOD - Use slicing for sublists
middle = data[10:20]
reversed_list = data[::-1]
```

### Dict Best Practices
```python
# ✓ GOOD - Use get() with default
count = counter.get(key, 0) + 1

# ✓ GOOD - setdefault for initialization
graph.setdefault(node, []).append(neighbor)

# ✓ GOOD - Dict comprehension
inverted = {v: k for k, v in original.items()}

# ✓ GOOD - Iterate over items
for key, value in my_dict.items():
    print(f"{key}: {value}")

# ✗ BAD - Check then set
if key not in my_dict:
    my_dict[key] = []
my_dict[key].append(value)

# ✓ GOOD - Use setdefault or defaultdict
my_dict.setdefault(key, []).append(value)
```

### Set Best Practices
```python
# ✓ GOOD - Remove duplicates from list
unique = list(set(items))

# ✓ GOOD - Fast membership testing
valid_ids = {1, 2, 3, 4, 5}
if user_id in valid_ids:  # O(1) instead of list's O(n)
    process(user_id)

# ✓ GOOD - Find common elements
common = set(list1) & set(list2)

# ✓ GOOD - Find unique to first list
unique_to_first = set(list1) - set(list2)

# Note: Sets don't preserve order (use dict.fromkeys() if needed)
unique_ordered = list(dict.fromkeys(items))
```

---

## Collections Module Structures

### defaultdict - Dict with Default Factory
```python
from collections import defaultdict

# Group items by key
grouped = defaultdict(list)
for item in items:
    grouped[item.category].append(item)

# Count occurrences
counter = defaultdict(int)
for word in words:
    counter[word] += 1  # No need to check if key exists

# Graph adjacency list
graph = defaultdict(list)
graph[1].append(2)  # Automatically creates list for new nodes
graph[1].append(3)

# Nested defaultdict
tree = lambda: defaultdict(tree)
users = tree()
users['alice']['settings']['theme'] = 'dark'
```

### Counter - Counting Made Easy
```python
from collections import Counter

# Count occurrences
words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']
counter = Counter(words)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# Most common elements
counter.most_common(2)  # [('apple', 3), ('banana', 2)]

# Combine counters
counter1 = Counter(['a', 'b', 'c'])
counter2 = Counter(['b', 'c', 'd'])
counter1 + counter2  # Counter({'b': 2, 'c': 2, 'a': 1, 'd': 1})

# Subtract counters
counter1 - counter2  # Counter({'a': 1})

# Character frequency in string
text = "hello world"
Counter(text)  # Counter({'l': 3, 'o': 2, 'h': 1, ...})
```

### deque - Double-Ended Queue
```python
from collections import deque

# FIFO queue
queue = deque()
queue.append(1)        # Add to right
queue.append(2)
item = queue.popleft() # Remove from left - O(1)

# Sliding window
window = deque(maxlen=3)  # Fixed size
window.append(1)  # [1]
window.append(2)  # [1, 2]
window.append(3)  # [1, 2, 3]
window.append(4)  # [2, 3, 4] - automatically removes from left

# Rotate elements
d = deque([1, 2, 3, 4, 5])
d.rotate(2)   # [4, 5, 1, 2, 3]
d.rotate(-2)  # [1, 2, 3, 4, 5]

# Use as stack (better than list for both ends)
stack = deque()
stack.append(1)     # Push
stack.pop()         # Pop from right
```

### OrderedDict - Remember Insertion Order
```python
from collections import OrderedDict

# Note: Regular dicts maintain order in Python 3.7+
# OrderedDict still useful for:

# 1. LRU Cache pattern
cache = OrderedDict()
MAX_SIZE = 100

def add_to_cache(key, value):
    if key in cache:
        cache.move_to_end(key)  # Mark as recently used
    cache[key] = value
    if len(cache) > MAX_SIZE:
        cache.popitem(last=False)  # Remove oldest

# 2. Reordering
od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
od.move_to_end('a')  # Move 'a' to end
# OrderedDict([('b', 2), ('c', 3), ('a', 1)])
```

### namedtuple - Lightweight Objects
```python
from collections import namedtuple

# Create a class-like structure
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)

# Access by attribute (more readable than tuple indices)
print(p.x, p.y)  # 10 20

# Still works like tuple
x, y = p
print(p[0])  # 10

# Immutable (can't change p.x = 30)

# Good for:
Person = namedtuple('Person', ['name', 'age', 'email'])
users = [
    Person('Alice', 30, 'alice@example.com'),
    Person('Bob', 25, 'bob@example.com')
]

# CSV row representation
Row = namedtuple('Row', ['date', 'open', 'close', 'volume'])
```

---

## Graph Representations

### Adjacency List (Most Common)
```python
# Best for sparse graphs
# Uses dict of lists

# Undirected graph
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'C', 'D'],
    'C': ['A', 'B', 'D'],
    'D': ['B', 'C']
}

# Directed graph
digraph = {
    'A': ['B', 'C'],
    'B': ['C'],
    'C': ['D'],
    'D': []
}

# Weighted graph
weighted_graph = {
    'A': [('B', 5), ('C', 3)],
    'B': [('C', 2), ('D', 6)],
    'C': [('D', 7)],
    'D': []
}

# Using defaultdict for easy construction
from collections import defaultdict

graph = defaultdict(list)
edges = [('A', 'B'), ('B', 'C'), ('C', 'A')]
for src, dst in edges:
    graph[src].append(dst)

# Class-based representation
class Graph:
    def __init__(self):
        self.adjacency = defaultdict(list)
    
    def add_edge(self, src, dst, weight=1):
        self.adjacency[src].append((dst, weight))
    
    def neighbors(self, node):
        return self.adjacency[node]
    
    def bfs(self, start):
        """Breadth-first search."""
        from collections import deque
        visited = set()
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            yield node
            
            for neighbor, _ in self.neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)
    
    def dfs(self, start):
        """Depth-first search."""
        visited = set()
        
        def _dfs(node):
            if node in visited:
                return
            visited.add(node)
            yield node
            
            for neighbor, _ in self.neighbors(node):
                yield from _dfs(neighbor)
        
        yield from _dfs(start)
```

### Adjacency Matrix
```python
# Best for dense graphs
# Uses 2D array/list

# For n nodes, create n x n matrix
n = 4
matrix = [[0] * n for _ in range(n)]

# Add edge from node i to node j
matrix[0][1] = 1  # Edge A -> B
matrix[1][2] = 1  # Edge B -> C

# Weighted edges
matrix[0][1] = 5  # Edge A -> B with weight 5

# Using numpy for larger graphs
import numpy as np
matrix = np.zeros((1000, 1000), dtype=int)

# Check if edge exists: O(1)
has_edge = matrix[i][j] != 0

# Get all neighbors: O(n)
neighbors = [j for j in range(n) if matrix[i][j] != 0]

# When to use:
# ✓ Dense graphs (many edges)
# ✓ Need fast edge existence checks
# ✓ Matrix operations (graph algorithms)
# ✗ Sparse graphs (wastes space)
```

### Comparison
| Aspect | Adjacency List | Adjacency Matrix |
|--------|---------------|------------------|
| Space | O(V + E) | O(V²) |
| Add vertex | O(1) | O(V²) - need to resize |
| Add edge | O(1) | O(1) |
| Check edge | O(degree) | O(1) |
| Get neighbors | O(1) | O(V) |
| Best for | Sparse graphs | Dense graphs |

---

## Trees and Recursive Structures

### Binary Tree
```python
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

# Build tree
root = TreeNode(1,
    TreeNode(2,
        TreeNode(4),
        TreeNode(5)
    ),
    TreeNode(3)
)

# Traversals
def inorder(node):
    """Left -> Root -> Right"""
    if node:
        yield from inorder(node.left)
        yield node.value
        yield from inorder(node.right)

def preorder(node):
    """Root -> Left -> Right"""
    if node:
        yield node.value
        yield from preorder(node.left)
        yield from preorder(node.right)

def postorder(node):
    """Left -> Right -> Root"""
    if node:
        yield from postorder(node.left)
        yield from postorder(node.right)
        yield node.value

def level_order(root):
    """Breadth-first traversal."""
    from collections import deque
    if not root:
        return
    
    queue = deque([root])
    while queue:
        node = queue.popleft()
        yield node.value
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
```

### N-ary Tree
```python
class NaryNode:
    def __init__(self, value):
        self.value = value
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)

# File system example
root = NaryNode("/")
home = NaryNode("home")
user = NaryNode("user")
docs = NaryNode("documents")

root.add_child(home)
home.add_child(user)
user.add_child(docs)

def traverse(node, depth=0):
    """Depth-first traversal."""
    print("  " * depth + node.value)
    for child in node.children:
        traverse(child, depth + 1)
```

### Trie (Prefix Tree)
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
    
    def starts_with(self, prefix):
        """Find all words with prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Collect all words from this node
        words = []
        self._collect_words(node, prefix, words)
        return words
    
    def _collect_words(self, node, prefix, words):
        if node.is_end:
            words.append(prefix)
        for char, child in node.children.items():
            self._collect_words(child, prefix + char, words)

# Usage
trie = Trie()
for word in ["apple", "app", "application", "apply"]:
    trie.insert(word)

print(trie.starts_with("app"))  # ['app', 'apple', 'application', 'apply']
```

---

## Performance Pitfalls

### Pitfall 1: Using List for Membership Testing
```python
# ✗ BAD - O(n) for each lookup
valid_users = ['alice', 'bob', 'charlie', ...]  # 10,000 users

for user in requests:  # 1,000,000 requests
    if user in valid_users:  # O(n) each time!
        process(user)
# Total: O(n * m) = 10 billion operations

# ✓ GOOD - O(1) for each lookup
valid_users = {'alice', 'bob', 'charlie', ...}

for user in requests:
    if user in valid_users:  # O(1)!
        process(user)
# Total: O(m) = 1 million operations
```

### Pitfall 2: Repeated List Concatenation
```python
# ✗ BAD - Creates new list each time
result = []
for i in range(10000):
    result = result + [i]  # O(n) copy each time!
# Total: O(n²)

# ✓ GOOD - Append is O(1) amortized
result = []
for i in range(10000):
    result.append(i)
# Total: O(n)
```

### Pitfall 3: Using Lists as Queues
```python
# ✗ BAD - pop(0) is O(n)
queue = [1, 2, 3, 4, 5]
while queue:
    item = queue.pop(0)  # Shifts all elements!
    process(item)

# ✓ GOOD - deque popleft() is O(1)
from collections import deque
queue = deque([1, 2, 3, 4, 5])
while queue:
    item = queue.popleft()  # O(1)
    process(item)
```

### Pitfall 4: Nested Dict Access
```python
# ✗ BAD - Repeated checking
data = {}
if 'user' not in data:
    data['user'] = {}
if 'settings' not in data['user']:
    data['user']['settings'] = {}
data['user']['settings']['theme'] = 'dark'

# ✓ GOOD - Use setdefault
data.setdefault('user', {}).setdefault('settings', {})['theme'] = 'dark'

# ✓ BETTER - Use defaultdict for deep nesting
from collections import defaultdict

def nested_dict():
    return defaultdict(nested_dict)

data = nested_dict()
data['user']['settings']['theme'] = 'dark'
```

### Pitfall 5: Sorting When Not Needed
```python
# ✗ BAD - Sort just to get min/max
data = [5, 2, 8, 1, 9]
minimum = sorted(data)[0]  # O(n log n)
maximum = sorted(data)[-1]

# ✓ GOOD - Use min/max
minimum = min(data)  # O(n)
maximum = max(data)  # O(n)

# ✗ BAD - Sort just to get k smallest
k_smallest = sorted(data)[:k]  # O(n log n)

# ✓ GOOD - Use heapq
import heapq
k_smallest = heapq.nsmallest(k, data)  # O(n log k)
```

### Pitfall 6: Deep Copying When Unnecessary
```python
# ✗ BAD - Deep copy for simple iteration
import copy
for item in copy.deepcopy(large_list):
    process(item)

# ✓ GOOD - Iterate directly if not modifying
for item in large_list:
    process(item)

# Only copy if modifying during iteration
for item in large_list.copy():  # Shallow copy sufficient
    if condition:
        large_list.remove(item)
```

---

## Real-World Examples

### Example 1: Dependency Graph (DAG)
```python
from collections import defaultdict, deque

class DependencyGraph:
    """Represents task dependencies."""
    
    def __init__(self):
        self.graph = defaultdict(list)  # task -> dependencies
        self.in_degree = defaultdict(int)
    
    def add_dependency(self, task, depends_on):
        """task depends on depends_on."""
        self.graph[depends_on].append(task)
        self.in_degree[task] += 1
        if depends_on not in self.in_degree:
            self.in_degree[depends_on] = 0
    
    def topological_sort(self):
        """Returns tasks in execution order."""
        # Tasks with no dependencies
        queue = deque([task for task, degree in self.in_degree.items() 
                       if degree == 0])
        result = []
        
        while queue:
            task = queue.popleft()
            result.append(task)
            
            # Process dependent tasks
            for dependent in self.graph[task]:
                self.in_degree[dependent] -= 1
                if self.in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # Check for cycles
        if len(result) != len(self.in_degree):
            raise ValueError("Circular dependency detected!")
        
        return result

# Usage
deps = DependencyGraph()
deps.add_dependency('compile', 'download_deps')
deps.add_dependency('test', 'compile')
deps.add_dependency('deploy', 'test')
deps.add_dependency('compile', 'generate_code')

print(deps.topological_sort())
# ['download_deps', 'generate_code', 'compile', 'test', 'deploy']
```

### Example 2: LRU Cache
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key not in self.cache:
            return None
        # Move to end (mark as recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)

# Usage
cache = LRUCache(capacity=3)
cache.put('a', 1)
cache.put('b', 2)
cache.put('c', 3)
cache.put('d', 4)  # 'a' is evicted
print(cache.get('a'))  # None
print(cache.get('b'))  # 2
```

### Example 3: Word Frequency Analysis
```python
from collections import Counter
import re

def analyze_text(text):
    # Clean and tokenize
    words = re.findall(r'\w+', text.lower())
    
    # Count frequencies
    word_freq = Counter(words)
    
    # Most common words
    top_10 = word_freq.most_common(10)
    
    # Words appearing exactly once
    hapax_legomena = [word for word, count in word_freq.items() if count == 1]
    
    return {
        'total_words': len(words),
        'unique_words': len(word_freq),
        'top_10': top_10,
        'rare_words': len(hapax_legomena)
    }

text = "the quick brown fox jumps over the lazy dog the fox was quick"
print(analyze_text(text))
```

### Example 4: Graph Shortest Path (BFS)
```python
from collections import deque, defaultdict

def shortest_path(graph, start, end):
    """Find shortest path using BFS."""
    if start == end:
        return [start]
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        node, path = queue.popleft()
        
        for neighbor in graph[node]:
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path found

# Social network example
network = {
    'Alice': ['Bob', 'Charlie'],
    'Bob': ['Alice', 'David'],
    'Charlie': ['Alice', 'David', 'Eve'],
    'David': ['Bob', 'Charlie'],
    'Eve': ['Charlie']
}

path = shortest_path(network, 'Alice', 'Eve')
print(path)  # ['Alice', 'Charlie', 'Eve']
```

---

## Quick Reference

### Data Structure Selection Cheat Sheet

```
Need...                          → Use...
─────────────────────────────────────────────────────
Fast lookups by key              → dict, set
Ordered collection               → list, tuple, deque
Unique elements                  → set, frozenset
Count occurrences                → Counter
Group by category                → defaultdict(list)
FIFO queue                       → deque
LIFO stack                       → list (or deque)
Priority queue                   → heapq
Cache with eviction              → OrderedDict
Immutable key-value              → tuple of pairs
Graph (sparse)                   → dict of lists
Graph (dense)                    → 2D list/numpy array
Tree                             → Custom class
Nested data with defaults        → defaultdict recursively
```

### Time Complexity Quick Reference

| Operation | List | Deque | Set | Dict |
|-----------|------|-------|-----|------|
| Access by index | O(1) | O(n) | N/A | N/A |
| Access by key | N/A | N/A | N/A | O(1) |
| Search | O(n) | O(n) | O(1) | O(1) |
| Insert at end | O(1)* | O(1) | O(1) | O(1) |
| Insert at start | O(n) | O(1) | O(1) | O(1) |
| Delete | O(n) | O(n) | O(1) | O(1) |
| Membership | O(n) | O(n) | O(1) | O(1) |

*Amortized

### Import Cheat Sheet

```python
# Built-in
list, tuple, set, dict  # No import needed

# Collections module
from collections import (
    defaultdict,    # Dict with default factory
    Counter,        # Count occurrences
    deque,          # Double-ended queue
    OrderedDict,    # Remember insertion order
    namedtuple,     # Lightweight objects
    ChainMap,       # Chain multiple dicts
)

# Heap queue
import heapq

# Copy utilities
import copy
copy.copy()      # Shallow copy
copy.deepcopy()  # Deep copy
```

---

## Key Takeaways

1. **Use the right tool:** Set for membership, dict for lookups, list for ordered collections
2. **Know your complexity:** Set/dict are O(1) for lookups, list is O(n)
3. **Avoid common pitfalls:** Don't use lists as queues, don't concatenate repeatedly
4. **Collections module is powerful:** defaultdict, Counter, deque solve common problems
5. **Graphs need structure:** Adjacency lists for sparse, matrices for dense
6. **Memory matters:** Generators for large data, tuples over lists when immutable
7. **Benchmark when unsure:** `timeit` module helps measure actual performance
8. **Readability counts:** Use the structure that makes your intent clearest

**Remember:** Premature optimization is evil, but choosing the right data structure from the start saves headaches later!
