# Python Mastery for Data Engineering

**Goal:** Build Odibi from scratch. Understand every pattern, every decision, every line of code.

**Timeline:** 10-13 weeks to full competency  
**Approach:** Reverse engineer Odibi by learning patterns, then rebuilding the framework incrementally

---

## 🎯 Learning Philosophy

**Explicit over implicit. Build over consume. Test over hope.**

- Every concept taught through Odibi lens
- No pattern without purpose
- Build working code, not toy examples
- Test-driven from day one
- First principles thinking throughout

---

## 📚 Program Structure

### **Phase 1: Foundations** (2-3 weeks)
Master the Python patterns Odibi depends on:
- Type system (type hints, Pydantic, validation)
- pytest (fixtures, mocking, parametrize, coverage)
- YAML (PyYAML, config management, safe loading)
- Abstractions (ABC, Protocol, composition over inheritance)
- Decorators (functions, factories, context managers)
- Data structures (graphs, topological sort, dependency resolution)
- Design patterns (registry, factory, strategy, decorator)

### **Phase 2: Odibi Deep Dive** (3-4 weeks)
Reverse engineer each Odibi component:
1. Config system (Pydantic models, YAML loading, validation)
2. Connection layer (BaseConnection, Local, Azure ADLS, Delta)
3. Engine abstraction (ABC, Pandas vs Spark, unified API)
4. Context API (cross-engine data passing, isolation)
5. Dependency graph (topological sort, cycle detection, execution layers)
6. Node execution (read → transform → validate → write)
7. Pipeline orchestration (dependency resolution, parallel execution)
8. Registry pattern (transform functions, metadata)
9. Story generation (renderers, metadata tracking)
10. CLI & validation (Click, error handling, rich output)

### **Phase 3: Build From Scratch** (4-6 weeks)
Incrementally rebuild Odibi:
- **Phase 1 MVP:** Pandas + local files (core read-transform-write loop)
- **Phase 2 Graph:** Dependency resolution with topological sort
- **Phase 3 Abstraction:** Engine ABC, add Spark support
- **Phase 4 Connections:** Azure ADLS, Delta Lake, SQL
- **Phase 5 Advanced:** Story generation, CLI tools, testing utilities
- **Comparison:** Your framework vs Odibi (what's different? why?)

---

## 🏗️ Repository Structure

```
Python-Mastery/
├── foundations/
│   ├── 01_type_system/
│   ├── 02_pytest_fundamentals/
│   ├── 03_yaml_config/
│   ├── 04_abstractions/
│   ├── 05_decorators/
│   ├── 06_data_structures/
│   └── 07_design_patterns/
│
├── odibi_deep_dive/
│   ├── 01_config_system/
│   ├── 02_connection_layer/
│   ├── 03_engine_abstraction/
│   ├── 04_context_api/
│   ├── 05_dependency_graph/
│   ├── 06_node_execution/
│   ├── 07_pipeline_orchestration/
│   ├── 08_registry_pattern/
│   ├── 09_story_generation/
│   └── 10_cli_validation/
│
└── build_from_scratch/
    ├── phase1_mvp/
    ├── phase2_graph/
    ├── phase3_abstraction/
    ├── phase4_connections/
    ├── phase5_advanced/
    └── comparison/
```

---

## 📖 Lesson Format

Each lesson follows this structure:

**1. 🎯 The Problem**  
Why does Odibi need this? What problem does it solve?

**2. 🦉 First Principles**  
Core concepts, design decisions, tradeoffs

**3. ⚡ Minimal Example**  
15-30 lines showing the pattern in isolation

**4. 🔍 Odibi Analysis**  
Read actual Odibi code, understand implementation

**5. 🏗️ Build It**  
Replicate the pattern from scratch

**6. ✅ Test It**  
Write pytest tests to validate behavior

**7. 🎯 Exercise**  
Apply the pattern to a new problem

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Basic Python knowledge (functions, classes, modules)
- Git fundamentals
- Text editor / IDE

### Setup
```bash
# Clone this repo
git clone https://github.com/henryodibi11/Python-Mastery.git
cd Python-Mastery

# Install dependencies
pip install -r requirements.txt

# Run your first lesson
cd foundations/01_type_system
jupyter notebook lesson.ipynb  # or python lesson.py
```

### Recommended Path
1. Start with `foundations/01_type_system`
2. Complete all foundations in order
3. Move to `odibi_deep_dive/01_config_system`
4. Complete deep dive modules in sequence
5. Begin `build_from_scratch/phase1_mvp`
6. Iterate through build phases

**Can you skip?** Yes, if confident. Diagnostic quizzes in each section.

---

## 📊 Progress Tracking

Track your progress in [PROGRESS.md](PROGRESS.md)

- [ ] **Foundations** (7 modules)
- [ ] **Odibi Deep Dive** (10 modules)
- [ ] **Build Phase 1** (MVP)
- [ ] **Build Phase 2** (Graph)
- [ ] **Build Phase 3** (Abstraction)
- [ ] **Build Phase 4** (Connections)
- [ ] **Build Phase 5** (Advanced)
- [ ] **Comparison Analysis**

---

## 🎓 Learning Resources

### Odibi Reference
- [Odibi Repository](https://github.com/henryodibi11/Odibi)
- [Odibi Documentation](https://github.com/henryodibi11/Odibi/tree/main/docs)
- [Odibi Phases](https://github.com/henryodibi11/Odibi/blob/main/PHASES.md)

### Python Resources
- [Real Python - Type Checking](https://realpython.com/python-type-checking/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python YAML Guide](https://realpython.com/python-yaml/)
- [Python Patterns](https://python-patterns.guide/)

### Data Engineering
- [The Missing Semester of Your CS Education](https://missing.csail.mit.edu/)
- [Software Engineering at Google](https://abseil.io/resources/swe-book)

---

## 🌍 First Principles

**Think like consultant, write like friend.**

Core engineering principles applied throughout:
- **Explicit over implicit** - No magic, clear dependencies
- **Composition over inheritance** - Flexible, testable design
- **Fail-fast validation** - Errors at config time, not runtime
- **Declarative over imperative** - YAML config, not Python spaghetti
- **Test-driven development** - Tests first, implementation second

---

## 🤝 Contributing

This is a personal learning repo, but improvements welcome:
- Found a bug in lesson code? PR it
- Better explanation? Suggest it
- Missing concept? Open an issue

---

## 📝 License

MIT - Learn freely, build openly

---

**Ready to master Python for data engineering? Start with [foundations/01_type_system](foundations/01_type_system/)**
