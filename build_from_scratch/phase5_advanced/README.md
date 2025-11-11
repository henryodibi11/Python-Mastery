# Phase 5: Advanced Features

**Goal:** Production-ready features (story generation, CLI, rich errors)

---

## What You'll Add

The polish that makes a framework production-ready:

```bash
# CLI
$ my-framework validate pipeline.yaml  # ✅ Config is valid
$ my-framework run pipeline.yaml       # 🚀 Running pipeline...

# Story generated automatically
$ cat outputs/story_2024-11-10.md
```

---

## Requirements

**Must add:**
- [x] Story generation (execution documentation)
- [x] CLI (validate and run commands)
- [x] Rich error messages
- [x] Config file support (YAML)
- [x] Testing utilities

**Nice to have:**
- Parallel execution (use layers from Phase 2)
- Progress bars
- HTML story output

---

## Architecture Changes

```diff
my_framework/
├── __init__.py
├── node.py
├── pipeline.py
├── context.py
├── graph.py
├── engines/
├── connections/
+ ├── story/
+ │   ├── __init__.py
+ │   ├── generator.py     # StoryGenerator
+ │   └── renderers.py     # Markdown/JSON renderers
+ ├── cli/
+ │   ├── __init__.py
+ │   ├── main.py          # Click CLI
+ │   ├── validate.py
+ │   └── run.py
+ ├── config/
+ │   ├── __init__.py
+ │   └── loader.py        # YAML → Pipeline
├── exceptions.py
```

---

## Tasks

**Week 5-6 Checklist:**

### Week 5: Story Generation
- [ ] Create StoryGenerator class
- [ ] Collect execution metadata (duration, rows, schema)
- [ ] Implement Markdown renderer
- [ ] Auto-generate story on pipeline.run()
- [ ] Test story content

### Week 6 Day 1-2: Config System
- [ ] Create YAML config schema
- [ ] Implement config loader (YAML → Pipeline)
- [ ] Add Pydantic validation
- [ ] Test config loading

### Week 6 Day 3-4: CLI
- [ ] Create CLI with Click
- [ ] Implement `validate` command
- [ ] Implement `run` command
- [ ] Rich error formatting
- [ ] Test CLI commands

### Week 6 Day 5: Polish
- [ ] Add progress indicators
- [ ] Improve error messages
- [ ] Write user documentation
- [ ] Create example configs

---

## Success Criteria

**Story Generation:**
```python
pipeline.run()
# Automatically creates outputs/story.md with:
# - What ran and when
# - Input/output schemas
# - Row counts
# - Duration
# - Any errors
```

**CLI:**
```bash
$ my-framework validate examples/pipeline.yaml
✅ Configuration is valid
  - 3 nodes defined
  - 0 cycles detected
  - Execution order: bronze → silver → gold

$ my-framework run examples/pipeline.yaml
🚀 Running pipeline: sales_etl
  ✅ bronze (2.3s, 10,000 rows)
  ✅ silver (1.5s, 8,500 rows)
  ✅ gold (0.8s, 1 row)
📊 Story saved to outputs/story_2024-11-10.md
```

**Config File:**
```yaml
# pipeline.yaml
engine: pandas

nodes:
  - name: bronze
    read:
      path: data/sales.csv
      format: csv
    
  - name: silver
    depends_on: [bronze]
    transform:
      sql: "SELECT * FROM bronze WHERE amount > 0"
    
  - name: gold
    depends_on: [silver]
    transform:
      sql: "SELECT product, SUM(amount) as total FROM silver GROUP BY product"
    write:
      path: outputs/summary.parquet
      format: parquet
```

---

## Key Features

**Story Generation:**
- Automatic documentation of every run
- Shows what happened, not just what was configured
- Useful for debugging and auditing

**CLI:**
- User-friendly interface
- Validate before running (fail fast)
- Rich output with colors and progress

**Config Files:**
- Declarative pipeline definition
- Version control friendly
- Shareable and reusable

---

## Hints

1. Use Click for CLI (simple, powerful)
2. Story generation: collect metadata in Pipeline.run()
3. Use Pydantic for config validation (already learned!)
4. Refer to odibi_deep_dive/09 and /10
5. Test CLI with Click's test runner

---

## Next Phase

Once complete, move to [Comparison Analysis](../comparison/) to learn from Odibi's design decisions.
