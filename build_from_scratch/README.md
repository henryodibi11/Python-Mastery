# Build Odibi From Scratch

**Goal:** Apply everything you learned by building your own data pipeline framework incrementally.

---

## Philosophy

You've learned the patterns. Now build the framework.

Each phase builds on the previous, adding complexity gradually. By the end, you'll have a working framework comparable to Odibi.

---

## Phases

### Phase 1: MVP (Week 1)
**Goal:** Basic working pipeline with Pandas + local files

**Features:**
- Read CSV/Parquet from local filesystem
- Transform with Python functions
- Write output to local filesystem
- Simple sequential execution

**~200 lines of code**

[Start Phase 1 →](phase1_mvp/)

---

### Phase 2: Dependency Graph (Week 2)
**Goal:** Add dependency resolution and correct execution order

**Features:**
- Node dependency declaration
- DAG construction and validation
- Topological sort for execution order
- Cycle detection with helpful errors

**+150 lines**

[Start Phase 2 →](phase2_graph/)

---

### Phase 3: Engine Abstraction (Week 3)
**Goal:** Support multiple execution engines (Pandas + Spark)

**Features:**
- Engine ABC
- PandasEngine implementation
- SparkEngine implementation
- Engine-agnostic node execution

**+300 lines**

[Start Phase 3 →](phase3_abstraction/)

---

### Phase 4: Cloud Connections (Week 4)
**Goal:** Add cloud storage support

**Features:**
- Connection abstraction
- Azure ADLS connector
- Delta Lake support
- Credential management

**+250 lines**

[Start Phase 4 →](phase4_connections/)

---

### Phase 5: Advanced Features (Week 5-6)
**Goal:** Production-ready features

**Features:**
- Story generation
- CLI tools (validate, run)
- Rich error messages
- Testing utilities

**+300 lines**

[Start Phase 5 →](phase5_advanced/)

---

### Comparison Analysis
**Goal:** Understand design decisions

Compare your implementation to Odibi:
- What's different?
- Why did Henry make different choices?
- What would you improve?

[View Comparison →](comparison/)

---

## Ground Rules

1. **TDD:** Write tests first, implementation second
2. **No copying:** Implement from understanding, not copy-paste
3. **Document decisions:** Why did you make this choice?
4. **Iterate:** First make it work, then make it good
5. **Refer back:** Use your lessons when stuck

---

## Success Criteria

By the end, you should be able to:
- [ ] Run a Bronze→Silver→Gold pipeline with your framework
- [ ] Swap between Pandas and Spark engines
- [ ] Read/write from Azure ADLS
- [ ] Generate execution stories
- [ ] Validate configs from CLI
- [ ] Explain every design pattern you used

---

## Ready?

Start with [Phase 1: MVP](phase1_mvp/) when you've completed foundations and odibi_deep_dive.

**Estimated total time:** 4-6 weeks
