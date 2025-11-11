# Module 7: Pipeline Orchestration

**Where Everything Comes Together**

The Pipeline is the conductor of your data symphony - coordinating Nodes, Graphs, Context, and Engine into a harmonious execution flow.

## 🎯 Learning Objectives

By the end of this module, you will:
- Understand Pipeline class architecture and responsibilities
- Master PipelineManager for multi-pipeline execution
- Build dependency graphs from configurations
- Implement layer-based parallel execution strategies
- Manage context across pipeline execution
- Handle errors and recovery mechanisms
- Collect and analyze PipelineResults
- Trigger automated story generation

## 📚 What You'll Learn

### 1. Pipeline Architecture
- Single-responsibility design
- Dependency injection pattern
- Configuration-driven execution
- Separation of concerns

### 2. PipelineManager
- Multi-pipeline orchestration
- YAML-based configuration loading
- Connection management
- Pipeline selection and execution

### 3. Graph Construction
- DependencyGraph integration
- Topological sorting for execution order
- Layer-based grouping
- Cycle detection and validation

### 4. Execution Flow
- Sequential node execution
- Dependency tracking
- Failure propagation
- Node skipping logic

### 5. Context Management
- Cross-node data sharing
- DataFrame registration
- Context lifecycle
- Memory optimization

### 6. Error Handling
- Graceful failure handling
- Partial pipeline completion
- Error aggregation
- Recovery strategies

### 7. Results Collection
- PipelineResults dataclass
- Node result tracking
- Success/failure/skipped categorization
- Duration and timestamp tracking

### 8. Story Generation
- Automated documentation
- Execution narrative creation
- Integration with StoryGenerator
- Output path configuration

## 🔄 Integration Points

```
Pipeline brings together:
├── Config: Pipeline definition
├── Graph: Dependency resolution
├── Context: Data sharing
├── Engine: Data processing
├── Node: Individual execution units
├── Connections: Data I/O
└── Story: Documentation generation
```

## 📖 Files in This Module

- **lesson.ipynb**: Deep dive into Pipeline architecture and execution
- **exercises.ipynb**: Hands-on pipeline orchestration challenges
- **solutions.ipynb**: Complete solutions with explanations
- **execution_flow.md**: Complete execution flow diagram

## 🚀 Key Concepts

### Pipeline vs PipelineManager

**Pipeline**: Executes a single pipeline with its nodes
```python
pipeline = Pipeline(pipeline_config, engine="pandas")
results = pipeline.run()
```

**PipelineManager**: Orchestrates multiple pipelines
```python
manager = PipelineManager.from_yaml("config.yaml")
results = manager.run(['bronze_to_silver', 'silver_to_gold'])
```

### Execution Layers

Nodes are grouped into layers based on dependencies:
```
Layer 0: [raw_customers, raw_orders]      # No dependencies
Layer 1: [clean_customers, clean_orders]  # Depend on Layer 0
Layer 2: [customer_orders]                # Depends on Layer 1
```

### Error Propagation

When a node fails:
1. Node marked as `failed`
2. Downstream dependent nodes are `skipped`
3. Independent nodes continue execution
4. Final results contain complete status

## 💡 Real-World Scenarios

This module covers:
- Multi-stage ETL pipelines (bronze → silver → gold)
- Parallel data processing strategies
- Production error handling
- Automated documentation generation
- Pipeline validation before execution

## 🔗 Prerequisites

- Module 3: Configuration System
- Module 4: Context & Data Sharing
- Module 5: Graph & Dependencies
- Module 6: Node Execution & Engine

## 📝 Next Steps

After completing this module, you'll understand the complete Odibi execution lifecycle and be ready to build production-grade data pipelines!

---

**Start with**: `lesson.ipynb`
