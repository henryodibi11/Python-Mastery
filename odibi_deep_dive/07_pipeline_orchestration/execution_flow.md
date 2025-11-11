# Complete Pipeline Execution Flow

This document provides a comprehensive view of how Odibi executes pipelines from YAML to results.

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  PipelineManager.from_yaml("config.yaml")                       │
│  ├─ Load YAML file                                              │
│  ├─ Parse into ProjectConfig                                    │
│  ├─ Build connection objects                                    │
│  └─ Create Pipeline instances for each pipeline                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  manager.run() or manager.run('pipeline_name')                  │
│  ├─ Determine which pipelines to run                            │
│  ├─ Validate pipeline selection                                 │
│  └─ Execute each pipeline in sequence                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Pipeline.run() - FOR EACH PIPELINE                             │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    [See Detailed Flow Below]
```

## Detailed Pipeline Execution Flow

### Phase 1: Initialization

```
┌─────────────────────────────────────────────────────────────────┐
│  Pipeline.__init__()                                            │
│  ├─ Store pipeline configuration                                │
│  ├─ Initialize Engine (PandasEngine/SparkEngine)                │
│  ├─ Create ExecutionContext                                     │
│  ├─ Build DependencyGraph from node configs                     │
│  └─ Initialize StoryGenerator                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  DependencyGraph Construction                                   │
│  ├─ Parse all nodes from configuration                          │
│  ├─ Build adjacency lists                                       │
│  ├─ Calculate in-degrees for each node                          │
│  └─ Validate no circular dependencies                           │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 2: Execution Planning

```
┌─────────────────────────────────────────────────────────────────┐
│  pipeline.run() starts                                          │
│  ├─ Record start time                                           │
│  ├─ Create PipelineResults object                               │
│  └─ Get execution order from graph                              │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  graph.topological_sort()                                       │
│  ├─ Use Kahn's algorithm                                        │
│  ├─ Process nodes with no remaining dependencies                │
│  ├─ Remove processed nodes from graph                           │
│  └─ Return execution order list                                 │
│                                                                  │
│  Example: [raw_customers, raw_orders, clean_customers,          │
│            clean_orders, customer_orders]                       │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 3: Node-by-Node Execution

```
FOR EACH node_name IN execution_order:

┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Dependency Check                                       │
│  ├─ Get node's dependencies from config                         │
│  ├─ Check if any dependency is in results.failed                │
│  ├─ If yes: Add to results.skipped, continue to next node       │
│  └─ If no: Proceed with execution                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Node Creation                                          │
│  ├─ Create Node instance                                        │
│  ├─ Pass: node_config, context, engine, connections             │
│  └─ Node is now ready to execute                                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Node Execution (node.execute())                        │
│  ├─ STEP 3.1: READ PHASE                                        │
│  │   ├─ If node has 'read' config:                              │
│  │   │   ├─ Get connection object                               │
│  │   │   ├─ Build file path                                     │
│  │   │   ├─ Read data using connection.read()                   │
│  │   │   └─ Store in context                                    │
│  │   └─ Else: No read phase                                     │
│  │                                                               │
│  ├─ STEP 3.2: TRANSFORM PHASE                                   │
│  │   ├─ If node has 'transform' config:                         │
│  │   │   ├─ Get input DataFrames from context                   │
│  │   │   ├─ Load SQL template                                   │
│  │   │   ├─ Execute SQL using engine.execute_sql()              │
│  │   │   └─ Store result in context                             │
│  │   └─ Else: No transform phase                                │
│  │                                                               │
│  └─ STEP 3.3: WRITE PHASE                                       │
│      ├─ If node has 'write' config:                             │
│      │   ├─ Get data from context                               │
│      │   ├─ Get connection object                               │
│      │   ├─ Build output path                                   │
│      │   └─ Write data using connection.write()                 │
│      └─ Else: No write phase                                    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Result Tracking                                        │
│  ├─ Create NodeResult object                                    │
│  │   ├─ success: True/False                                     │
│  │   ├─ rows_affected: count                                    │
│  │   ├─ duration: execution time                                │
│  │   ├─ error_message: if failed                                │
│  │   └─ metadata: additional info                               │
│  ├─ Store in results.node_results[node_name]                    │
│  ├─ If success: Add to results.completed                        │
│  └─ If failure: Add to results.failed                           │
└─────────────────────────────────────────────────────────────────┘

REPEAT FOR NEXT NODE
```

### Phase 4: Post-Execution

```
┌─────────────────────────────────────────────────────────────────┐
│  All nodes processed                                            │
│  ├─ Calculate total duration                                    │
│  ├─ Record end time                                             │
│  └─ Prepare for story generation                                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Story Generation (if enabled)                                  │
│  ├─ story_generator.generate()                                  │
│  │   ├─ Create markdown document                                │
│  │   ├─ Add pipeline summary                                    │
│  │   ├─ Add execution timeline                                  │
│  │   ├─ For each node:                                          │
│  │   │   ├─ Add node details                                    │
│  │   │   ├─ Add SQL transformation                              │
│  │   │   ├─ Add data samples                                    │
│  │   │   └─ Add status                                          │
│  │   └─ Write to output file                                    │
│  └─ Store story path in results                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Return PipelineResults                                         │
│  ├─ completed: List of successful nodes                         │
│  ├─ failed: List of failed nodes                                │
│  ├─ skipped: List of skipped nodes                              │
│  ├─ node_results: Detailed results per node                     │
│  ├─ duration: Total execution time                              │
│  ├─ start_time: ISO timestamp                                   │
│  ├─ end_time: ISO timestamp                                     │
│  └─ story_path: Path to generated documentation                 │
└─────────────────────────────────────────────────────────────────┘
```

## Context Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ExecutionContext                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Internal Storage: Dict[str, DataFrame]                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Node A (Read):                                                 │
│    Connection.read() → DataFrame → context.register("A")        │
│                                                                  │
│  Node B (Read):                                                 │
│    Connection.read() → DataFrame → context.register("B")        │
│                                                                  │
│  Node C (Transform - depends on A, B):                          │
│    context.get("A") → DataFrame A                               │
│    context.get("B") → DataFrame B                               │
│    engine.execute_sql(A, B) → DataFrame C                       │
│    context.register("C") → Store C                              │
│                                                                  │
│  Node D (Write - depends on C):                                 │
│    context.get("C") → DataFrame C                               │
│    Connection.write(C) → File written                           │
└─────────────────────────────────────────────────────────────────┘
```

## Error Propagation Example

```
Execution Order: [A, B, C, D, E]
Dependencies:
  A: []
  B: []
  C: [A]
  D: [B]
  E: [C, D]

Timeline:
┌─────────────────────────────────────────────────────────────────┐
│ Node A: Execute → ✅ SUCCESS → results.completed.append("A")    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Node B: Execute → ❌ FAILED → results.failed.append("B")        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Node C:                                                          │
│   Check dependencies: A in results.failed? No                   │
│   → Execute → ✅ SUCCESS → results.completed.append("C")        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Node D:                                                          │
│   Check dependencies: B in results.failed? YES                  │
│   → SKIP → results.skipped.append("D")                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Node E:                                                          │
│   Check dependencies: C in results.failed? No                   │
│   Check dependencies: D in results.failed? No                   │
│   BUT: D in results.skipped (not checked, would still fail)     │
│   → Actually: D is a dependency, and D was skipped because      │
│      B failed. Since D didn't execute, E can't get its data.    │
│   → The actual check is: any(dep in results.failed)             │
│   → D is not in failed, but D didn't complete                   │
│   → E would attempt to execute and fail because D's data        │
│      isn't in context                                           │
│                                                                  │
│   CORRECTION in real implementation:                            │
│   If any dependency is in (failed OR skipped), we skip.         │
│   → SKIP → results.skipped.append("E")                          │
└─────────────────────────────────────────────────────────────────┘

Final Results:
  completed: [A, C]
  failed: [B]
  skipped: [D, E]
```

## Layer-Based Execution (Future Parallel Support)

```
Graph: A → C → E
       B → D ↗

Layers:
┌─────────────────────────────────────────────────────────────────┐
│  Layer 0: [A, B]  (No dependencies - could run in parallel)     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: [C, D]  (Depend only on Layer 0 - could parallel)     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: [E]     (Depends on Layer 1 - sequential)             │
└─────────────────────────────────────────────────────────────────┘

Current: Executed sequentially in topological order
Future: Could execute each layer in parallel
```

## Multi-Pipeline Execution

```
PipelineManager with 3 pipelines:
├─ bronze_to_silver (no dependencies)
├─ silver_to_gold (no dependencies)
└─ analytics (no dependencies)

┌─────────────────────────────────────────────────────────────────┐
│  manager.run()                                                  │
│  ├─ For pipeline "bronze_to_silver":                            │
│  │   ├─ Print header                                            │
│  │   ├─ Execute pipeline.run()                                  │
│  │   ├─ Store results                                           │
│  │   └─ Print summary                                           │
│  │                                                               │
│  ├─ For pipeline "silver_to_gold":                              │
│  │   ├─ Print header                                            │
│  │   ├─ Execute pipeline.run()                                  │
│  │   ├─ Store results                                           │
│  │   └─ Print summary                                           │
│  │                                                               │
│  └─ For pipeline "analytics":                                   │
│      ├─ Print header                                            │
│      ├─ Execute pipeline.run()                                  │
│      ├─ Store results                                           │
│      └─ Print summary                                           │
│                                                                  │
│  Return: Dict[str, PipelineResults]                             │
└─────────────────────────────────────────────────────────────────┘
```

## Component Integration Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                         YAML Config                              │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                      ProjectConfig                              │
│  ├─ engine: "pandas"                                            │
│  ├─ connections: {...}                                          │
│  ├─ pipelines: [...]                                            │
│  └─ story: {...}                                                │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                    PipelineManager                              │
│  ├─ Builds connections from config                             │
│  ├─ Creates Pipeline instances                                 │
│  └─ Orchestrates execution                                      │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                        Pipeline                                 │
│  ├─ DependencyGraph (execution order)                          │
│  ├─ ExecutionContext (data sharing)                            │
│  ├─ Engine (data processing)                                   │
│  ├─ Connections (I/O)                                           │
│  └─ StoryGenerator (documentation)                             │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                       For Each Node                             │
│  ├─ Node instance created                                      │
│  ├─ Read → Transform → Write                                   │
│  ├─ NodeResult generated                                       │
│  └─ Data stored in Context                                     │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                    PipelineResults                              │
│  ├─ Completed nodes                                            │
│  ├─ Failed nodes                                               │
│  ├─ Skipped nodes                                              │
│  ├─ Detailed node results                                      │
│  ├─ Timing information                                         │
│  └─ Story path                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Key Takeaways

1. **Pipeline is the Conductor**: Orchestrates all components
2. **Graph Determines Order**: Topological sort ensures correct execution
3. **Context Enables Sharing**: DataFrames passed between nodes
4. **Engine Processes Data**: SQL transformations executed
5. **Connections Handle I/O**: Read and write operations
6. **Results Track Everything**: Complete execution audit trail
7. **Story Documents**: Automatic execution documentation
8. **Failure Propagates**: Failed nodes skip downstream dependencies

---

**This is the complete Odibi execution lifecycle!**
