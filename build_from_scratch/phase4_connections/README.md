# Phase 4: Cloud Connections

**Goal:** Read/write from cloud storage (Azure ADLS, Delta Lake)

---

## What You'll Add

Support cloud storage with same node syntax:

```python
# Local files (already works)
Node(name="load", read="data/input.csv")

# Azure ADLS (new!)
Node(name="load", read="abfss://container@account.dfs.core.windows.net/data/input.csv")

# Delta Lake (new!)
Node(name="load", read="delta://my_table")
```

---

## Requirements

**Must add:**
- [x] Connection abstraction
- [x] LocalConnection (refactor existing)
- [x] AzureADLSConnection
- [x] DeltaConnection
- [x] Connection factory
- [x] Update engines to use connections

**Tests:**
- [x] Test each connection type
- [x] Mock cloud connections (no real Azure calls)
- [x] Test credential handling

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
+ ├── connections/
+ │   ├── __init__.py
+ │   ├── base.py          # Connection ABC
+ │   ├── local.py
+ │   ├── azure_adls.py
+ │   └── delta.py
├── exceptions.py
```

---

## Tasks

**Week 4 Checklist:**

### Day 1: Connection Abstraction
- [ ] Create connections/base.py with BaseConnection ABC
- [ ] Define methods: get_path(), validate(), get_storage_options()
- [ ] Refer to odibi_deep_dive/02

### Day 2: Local Refactor
- [ ] Implement LocalConnection
- [ ] Move path logic from engines
- [ ] Test local connection

### Day 3: Azure ADLS
- [ ] Implement AzureADLSConnection
- [ ] Handle abfss:// URLs
- [ ] Mock credential fetching (don't actually call Azure)
- [ ] Test path resolution

### Day 4: Delta Lake
- [ ] Implement DeltaConnection
- [ ] Support delta:// protocol
- [ ] Test read/write with delta-spark library
- [ ] Test time travel (versionAsOf)

### Day 5: Integration
- [ ] Update engines to use connections
- [ ] Add connection parameter to Pipeline/Node
- [ ] Create connection factory
- [ ] Test multi-connection pipeline

---

## Success Criteria

Pipeline uses multiple connection types:

```python
pipeline = Pipeline(engine="spark")

# Load from Azure
pipeline.add_node(Node(
    name="bronze",
    connection=AzureADLSConnection(
        account="mystorageaccount",
        container="raw"
    ),
    read="sales/2024/data.parquet"
))

# Transform
pipeline.add_node(Node(
    name="silver",
    depends_on=["bronze"],
    transform="SELECT * FROM bronze WHERE amount > 0"
))

# Save to Delta
pipeline.add_node(Node(
    name="gold",
    depends_on=["silver"],
    connection=DeltaConnection(),
    write="delta://gold.sales_summary"
))

pipeline.run()  # ✅ Works across connections!
```

---

## Key Concepts

**Connection Abstraction:**
- Isolates storage logic from engine logic
- Same engine works with different storage systems
- Easy to add new storage types (S3, GCS, etc.)

**Path Resolution:**
- Connections resolve logical paths to physical URLs
- Handle credentials and authentication
- Validate paths before execution

---

## Hints

1. Study odibi_deep_dive/02 for connection patterns
2. Don't implement real Azure auth - use env vars or mocks
3. Delta requires `delta-spark` library
4. Use connection factory for URL → Connection mapping
5. Test with mocked credentials (don't commit secrets!)

---

## Next Phase

Once connections work, move to [Phase 5: Advanced](../phase5_advanced/) for story generation and CLI.
