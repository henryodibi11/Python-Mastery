# Module 06: Node Execution Engine

## Overview
Deep dive into ODIBI's Node execution architecture - the core engine that orchestrates the read → transform → validate → write cycle.

## Learning Objectives
- Understand the Node class architecture and initialization
- Master the 4-phase execution lifecycle
- Learn connection and engine integration patterns
- Implement custom transforms and validations
- Handle errors and collect execution metadata

## Module Structure

### 1. Core Files
- **lesson.ipynb**: Interactive walkthrough of node execution
- **exercises.ipynb**: Hands-on practice with node patterns
- **solutions.ipynb**: Complete solutions with explanations
- **node_lifecycle.md**: Visual execution flow diagrams

### 2. Key Concepts

#### Node Initialization
```python
Node(config, context, engine, connections, config_file)
```
- NodeConfig → executable Node
- Context for data passing
- Engine abstraction (Spark/Pandas)
- Connection registry access

#### Execution Phases
1. **Read Phase**: Load data from sources
2. **Transform Phase**: Apply SQL/function/operation transforms
3. **Validation Phase**: Enforce schema and data quality rules
4. **Write Phase**: Persist results to destinations

#### Result Collection
- NodeResult metadata
- Performance metrics
- Schema tracking
- Error context

## Prerequisites
- Module 01: Config System (NodeConfig understanding)
- Module 02: Connection Layer (connection resolution)
- Module 04: Context API (data passing)

## Time Estimate
- Lesson: 45-60 minutes
- Exercises: 30-45 minutes
- Total: ~90 minutes

## Key Files Referenced
- `odibi/node.py` - Main Node implementation
- `odibi/config.py` - NodeConfig models
- `odibi/exceptions.py` - Error handling

## Quick Start
```bash
jupyter notebook lesson.ipynb
```
