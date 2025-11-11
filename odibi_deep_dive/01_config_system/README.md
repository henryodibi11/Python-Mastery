# 01: Odibi Configuration System Deep Dive

## 🎯 Goal

Master Odibi's type-safe configuration architecture: from YAML files to validated Pydantic models that power production data pipelines.

## 📋 Overview

This is the **foundational deep dive** into Odibi. Everything in the framework starts with configuration:
- Pipelines are defined in YAML
- Loaded and validated with Pydantic
- Used to construct execution graphs
- Errors caught before any code runs

**First Principles:**
- ✅ **Validate early, fail fast** - catch errors in config, not in production
- ✅ **Type safety** - leverage Python's type system with Pydantic
- ✅ **Clear errors** - users should know exactly what's wrong and where
- ✅ **Defaults with overrides** - sensible defaults, explicit customization

## 📚 What You'll Learn

### Core Architecture
1. **Hierarchy**: `ProjectConfig` → `PipelineConfig` → `NodeConfig`
2. **Enums**: Type-safe constants (`EngineType`, `ConnectionType`, `WriteMode`)
3. **Nested Models**: Complex configs using composition (`ReadConfig`, `WriteConfig`, etc.)
4. **Discriminated Unions**: Different connection types based on `type` field

### Advanced Validation
5. **Field Validators**: Validate individual fields
6. **Model Validators**: Cross-field validation (e.g., "table OR path required")
7. **Custom Error Messages**: User-friendly validation failures
8. **Defaults & Inheritance**: Config defaults that cascade

### Practical Skills
9. **YAML → Pydantic**: Load and validate configuration files
10. **Error Handling**: Catch and report validation errors elegantly
11. **Testing Configs**: Write comprehensive config validation tests

## 🗂️ Files

- **lesson.ipynb** - Main interactive lesson (start here!)
- **exercises.ipynb** - Practice extending the config system
- **solutions.ipynb** - Reference solutions
- **odibi_config_reference.md** - Complete config API reference

## 🔍 Real Code Analysis

This lesson uses **actual Odibi production code**:
- Source: `c:/Users/hodibi/OneDrive - Ingredion/Desktop/Repos/Odibi/odibi/config.py`
- 313 lines of battle-tested configuration models
- Powers all Odibi data pipelines

## 🎓 Prerequisites

From `foundations/`:
- `02_pydantic_validation` - Must understand Pydantic basics
- `03_yaml_config` - Must know YAML loading patterns

## ⏱️ Time Estimate

- Lesson: 90-120 minutes
- Exercises: 60-90 minutes
- Total: 2.5-3.5 hours

## 🚀 Getting Started

```bash
jupyter lab lesson.ipynb
```

Or use VS Code with Jupyter extension.

## 💡 Key Takeaways

After this lesson, you'll understand:
1. How Odibi validates entire projects before executing
2. Why enum-based validation prevents typos and mistakes
3. How nested Pydantic models compose complex configurations
4. How model validators enforce business rules
5. Why this architecture scales to enterprise data pipelines

---

**Next**: After mastering config, move to `02_execution_context/` to see how these configs become runtime objects.
