# 03: YAML Configuration Management

**Master configuration files for production data pipelines**

## 🎯 Why YAML?

YAML is the industry standard for configuration management in data engineering, DevOps, and MLOps. Every major tool uses it: Airflow DAGs, Kubernetes manifests, Docker Compose, dbt profiles, and **Odibi pipelines**.

**Why not JSON or Python?**
- ✅ Human-readable (comments, no quotes, clean nesting)
- ✅ Supports complex structures (anchors, references, multiline strings)
- ✅ Language-agnostic (works across Python, Go, Java, etc.)
- ❌ JSON: No comments, too verbose
- ❌ Python: Not declarative, requires execution to parse

## 📚 What You'll Learn

### 1. YAML Fundamentals
- Scalars, lists, dictionaries
- Multiline strings (literal `|` vs folded `>`)
- Anchors & aliases (DRY configs)
- Type coercion gotchas

### 2. Python Integration
- `PyYAML` vs `ruamel.yaml`
- `safe_load()` vs `load()` (security!)
- Schema validation with Pydantic
- Environment variable interpolation

### 3. Real-World Patterns
- Multi-environment configs (dev/staging/prod)
- Config inheritance and includes
- Secret management (never commit keys!)
- Validation and error handling

### 4. Odibi's YAML Architecture
Analysis of actual production configs:
- Connection patterns (local, ADLS, Azure SQL)
- Pipeline structure and node dependencies
- Delta Lake configurations
- Story generation settings

## 📂 Files

| File | Purpose |
|------|---------|
| `lesson.ipynb` | **Main lesson** - Interactive tutorial |
| `exercises.ipynb` | Practice problems |
| `solutions.ipynb` | Solutions with explanations |
| `odibi_config_patterns.md` | Deep dive into Odibi's YAML structure |
| `example_configs/` | Sample YAML files for testing |

## 🚀 Quick Start

```bash
# Install dependencies
pip install pyyaml pydantic python-dotenv

# Open the main lesson
jupyter notebook lesson.ipynb
```

## 🦉 First Principles

**Declarative > Imperative**

YAML describes *what* you want, not *how* to do it:

```yaml
# GOOD: Declarative
pipelines:
  - pipeline: etl
    nodes:
      - name: load_data
        read:
          connection: bronze
          format: parquet

# BAD: Imperative (this belongs in code, not config)
# steps:
#   - connect_to_storage()
#   - open_file("data.parquet")
#   - read_into_dataframe()
```

## 🔑 Key Takeaways

1. **Security**: Always use `safe_load()`, never commit secrets
2. **Validation**: Use Pydantic to catch errors early
3. **DRY**: Use anchors/aliases to avoid duplication
4. **Separation**: Config (YAML) vs Code (Python) vs Secrets (env vars)
5. **Evolution**: Plan for multi-environment configs from day 1

## 🎯 By the End of This Lesson

You will:
- ✅ Read and write complex YAML configurations
- ✅ Validate configs with Pydantic schemas
- ✅ Understand Odibi's config architecture
- ✅ Build your own validated config system
- ✅ Avoid common YAML pitfalls (Norway problem, type coercion)

---

**Next Steps**: Open [lesson.ipynb](lesson.ipynb) to start learning! 🚀
