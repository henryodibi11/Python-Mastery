# Phase 3: Engine Abstraction

**Goal:** Support both Pandas and Spark with the same pipeline code

---

## What You'll Add

Abstract the execution engine so pipelines work on both:

```python
# Same pipeline code, different engines!

# Run on Pandas (small data, local)
pipeline = Pipeline(engine="pandas")
pipeline.run()

# Run on Spark (big data, distributed)
pipeline = Pipeline(engine="spark")  
pipeline.run()  # Same code, different execution!
```

---

## Requirements

**Must add:**
- [x] Engine ABC (abstract base class)
- [x] PandasEngine (refactor existing code)
- [x] SparkEngine (new implementation)
- [x] Update Node to use engine interface
- [x] Update Context for Spark (temp views)
- [x] Engine factory

**Tests:**
- [x] Test engine interface compliance
- [x] Test both engines with same pipeline
- [x] Test engine-specific features

---

## Architecture Changes

```diff
my_framework/
├── __init__.py
├── node.py
├── pipeline.py
├── context.py
├── graph.py
+ ├── engines/
+ │   ├── __init__.py
+ │   ├── base.py        # Engine ABC
+ │   ├── pandas_engine.py
+ │   └── spark_engine.py
├── exceptions.py
```

---

## Tasks

**Week 3 Checklist:**

### Day 1: Design Engine ABC
- [ ] Create engines/base.py with Engine ABC
- [ ] Define methods: read(), write(), execute_sql(), transform()
- [ ] Document interface contract
- [ ] Refer to odibi_deep_dive/03

### Day 2: Pandas Refactor
- [ ] Move pandas logic from Node to PandasEngine
- [ ] Implement all Engine methods
- [ ] Update tests to use engine
- [ ] Ensure backwards compatibility

### Day 3: Spark Implementation
- [ ] Implement SparkEngine (read, write, execute_sql)
- [ ] Update Context for Spark (PandasContext vs SparkContext)
- [ ] Test Spark engine in isolation

### Day 4: Integration
- [ ] Add engine parameter to Pipeline
- [ ] Update Node to use engine
- [ ] Create engine factory (create_engine function)
- [ ] Test same pipeline on both engines

### Day 5: Polish
- [ ] Test format support (CSV, Parquet for both)
- [ ] Add engine comparison docs
- [ ] Update examples
- [ ] Performance comparison (pandas vs spark)

---

## Success Criteria

Same pipeline runs on both engines:

```python
# Define once
def create_pipeline(engine):
    p = Pipeline(engine=engine)
    p.add_node(Node(name="load", read="data/sales.csv"))
    p.add_node(Node(
        name="clean",
        depends_on=["load"],
        transform="SELECT * FROM load WHERE amount > 0"  # SQL works on both!
    ))
    p.add_node(Node(name="save", depends_on=["clean"], write="output.parquet"))
    return p

# Run on Pandas
pandas_pipeline = create_pipeline("pandas")
pandas_pipeline.run()  # ✅

# Run on Spark  
spark_pipeline = create_pipeline("spark")
spark_pipeline.run()  # ✅ Same behavior!
```

---

## Key Insights

**Why abstraction matters:**
- Write pipeline once, run anywhere
- Test on Pandas locally, deploy on Spark
- Swap engines without changing pipeline code

**Design principles:**
- Depend on abstractions (Engine), not implementations (Pandas)
- Interfaces should be minimal but complete
- Hide engine-specific details behind abstraction

---

## Hints

1. Study odibi_deep_dive/03 carefully
2. Start with Engine ABC - get interface right first
3. PandasEngine is easier - refactor existing code
4. SparkEngine reads from temp views, not dicts
5. Use factory pattern for engine creation

---

## Next Phase

Once abstraction works, move to [Phase 4: Cloud Connections](../phase4_connections/) to add Azure support.
