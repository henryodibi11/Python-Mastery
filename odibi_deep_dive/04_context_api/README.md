# 04 - Context API Deep Dive

## Overview
Learn how Odibi's Context API manages data flow between nodes without global state.

## 🎯 Learning Objectives
- Understand the Context ABC and its contract
- Compare PandasContext (dict-based) vs SparkContext (temp view)
- Implement custom context with advanced features (caching, LRU eviction)
- Master context isolation patterns for testing
- Apply memory management best practices

## 📚 Content Structure

### Main Lesson: `lesson.ipynb`
1. **Problem Statement**: Why we need explicit context vs global variables
2. **First Principles**: Dependency injection, namespace isolation
3. **Code Analysis**: Deep dive into `context.py`
4. **Build Project**: CachingContext with LRU eviction
5. **Testing**: Context lifecycle and isolation patterns

### Practice: `exercises.ipynb`
- Exercise 1: Implement context snapshots
- Exercise 2: Add context serialization (pickle)
- Exercise 3: Build context observer pattern
- Exercise 4: Create context validation layer

### Reference: `context_patterns.md`
Best practices and anti-patterns for context usage

## 🔑 Key Concepts
- **Abstract Base Class**: Polymorphic context for Pandas/Spark
- **Factory Pattern**: `create_context()` for engine selection
- **Isolation**: Each pipeline run gets fresh context
- **Memory Management**: Clear temp views, release DataFrames
- **Type Safety**: Runtime validation of DataFrame types

## 🛠️ Prerequisites
- Completion of 01-03 or equivalent Odibi knowledge
- Understanding of ABC (Abstract Base Classes)
- Basic knowledge of Pandas and optionally Spark

## 📖 Files
- `lesson.ipynb` - Main tutorial with executable code
- `exercises.ipynb` - Practice problems
- `solutions.ipynb` - Exercise solutions with explanations
- `context_patterns.md` - Best practices guide

## ⏱️ Estimated Time
- Lesson: 45 minutes
- Exercises: 60 minutes
- Total: ~2 hours
