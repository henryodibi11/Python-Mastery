# Odibi YAML Configuration Patterns

**Deep dive into Odibi's production-grade YAML architecture**

---

## 📋 Overview

Odibi uses YAML as its primary configuration language for defining data pipelines. This document analyzes the patterns, conventions, and best practices found in actual Odibi configs.

**Source Configs Analyzed:**
- `Odibi/examples/example_delta_pipeline.yaml`
- `Odibi/examples/example_local.yaml`
- `Odibi/examples/template_full.yaml`

---

## 🏗️ Top-Level Structure

Every Odibi config follows this structure:

```yaml
# 1. Project metadata
project: <string>
description: <string> (optional)
version: <string> (optional)
engine: pandas | spark

# 2. Connections (where data lives)
connections:
  <conn_name>:
    type: local | azure_adls | azure_sql
    # ... type-specific fields

# 3. Story generation (observability)
story:
  connection: <conn_name>
  path: <string>
  max_sample_rows: <int>

# 4. Global settings
retry:
  max_attempts: <int>
  backoff_seconds: <float>

logging:
  level: DEBUG | INFO | WARNING | ERROR

# 5. Pipelines (the actual work)
pipelines:
  - pipeline: <string>
    nodes:
      - name: <string>
        # ... operations
```

---

## 🔌 Connection Patterns

### Pattern 1: Local Development

**Use case:** Local testing, notebooks, CI/CD

```yaml
connections:
  data:
    type: local
    base_path: ./data
```

**Key insight:** Simple file-based storage with relative paths.

### Pattern 2: Azure ADLS (Cloud Storage)

**Use case:** Production data lakes (Bronze, Silver, Gold)

```yaml
connections:
  bronze:
    type: azure_adls
    account: YOUR_STORAGE_ACCOUNT
    container: bronze
    path_prefix: raw
    auth_mode: key_vault
    key_vault_name: YOUR_KEY_VAULT
    secret_name: bronze-storage-key
```

**Key insights:**
- **Separation of concerns:** Each layer (bronze/silver/gold) gets its own connection
- **Security first:** Uses Azure Key Vault, never hardcodes credentials
- **Path organization:** `path_prefix` for namespace isolation

### Pattern 3: Azure SQL (Relational)

**Use case:** Dimension tables, master data, metadata

```yaml
connections:
  azure_db:
    type: azure_sql
    host: myserver.database.windows.net
    database: analytics
    port: 1433
    auth_mode: key_vault
    key_vault_name: company-keyvault
    secret_name: sql-connection-string
```

**Key insight:** Same security pattern (Key Vault) across all connection types.

---

## 📊 Pipeline Patterns

### Pattern 1: Simple ETL (Bronze → Silver)

```yaml
pipelines:
  - pipeline: bronze_to_silver
    layer: transformation
    nodes:
      # Read raw data
      - name: load_raw_sales
        read:
          connection: data
          path: bronze/sales.csv
          format: csv
        cache: true  # ← Important for reuse!

      # Transform with SQL
      - name: clean_sales
        depends_on: [load_raw_sales]
        transform:
          steps:
            - |
              SELECT * FROM load_raw_sales
              WHERE amount > 0

      # Write to parquet
      - name: save_silver
        depends_on: [clean_sales]
        write:
          connection: data
          path: silver/sales.parquet
          format: parquet
          mode: overwrite
```

**Key patterns:**
- **Caching:** `cache: true` avoids re-reading data
- **SQL transforms:** Reference nodes by name (like CTEs!)
- **Explicit dependencies:** `depends_on` creates DAG

### Pattern 2: Delta Lake with Time Travel

```yaml
pipelines:
  - pipeline: delta_time_travel
    nodes:
      # Read latest version
      - name: read_latest
        read:
          connection: local
          path: output/sales.delta
          format: delta

      # Read specific version (time travel!)
      - name: read_v0
        read:
          connection: local
          path: output/sales.delta
          format: delta
          options:
            versionAsOf: 0  # ← Time travel to version 0
```

**Key insight:** Delta Lake options enable version control for data.

### Pattern 3: Partitioned Delta (Production)

```yaml
pipelines:
  - pipeline: production_delta_etl
    nodes:
      - name: write_silver
        write:
          connection: silver
          path: events/clean_events.delta
          format: delta
          mode: append
          options:
            partition_by:
              - event_type  # ← Partition by low-cardinality column
```

**Best practices from Odibi:**
- Only partition by **low-cardinality** columns
- Use `append` mode for Delta (ACID guarantees)
- Partition on ADLS for query performance

---

## 🎯 Node Operation Patterns

### Pattern 1: Read-Only Nodes (Data Loading)

**Purpose:** Load data and cache for downstream use

```yaml
- name: load_raw_sales
  read:
    connection: data
    path: bronze/sales.csv
    format: csv
    options:
      header: 0
      dtype:
        transaction_id: str
        amount: float
  cache: true  # Critical for multi-use
```

**When to use:**
- Loading source data
- Shared data across multiple transforms
- Dimension tables used in joins

### Pattern 2: Transform-Only Nodes (SQL)

**Purpose:** Transform previously loaded/cached data

```yaml
- name: clean_sales
  depends_on: [load_raw_sales]
  transform:
    steps:
      - |
        SELECT
          transaction_id,
          customer_id,
          amount
        FROM load_raw_sales
        WHERE amount > 0
      
      # Chain multiple transforms
      - |
        SELECT *,
          amount * 1.1 as amount_with_tax
        FROM __result__  # ← Previous step result
```

**Key patterns:**
- Multi-step SQL: Each step operates on `__result__` of previous
- Reference cached nodes by name
- Standard SQL syntax (DuckDB/Pandas-compatible)

### Pattern 3: Write-Only Nodes (Sinks)

**Purpose:** Persist results to storage

```yaml
- name: save_silver
  depends_on: [clean_sales]
  write:
    connection: data
    path: silver/sales.parquet
    format: parquet
    mode: overwrite
    options:
      compression: snappy
```

**Format-specific options:**
- **Parquet:** `compression` (snappy, gzip, brotli)
- **Delta:** `mergeSchema`, `partition_by`, `versionAsOf`
- **CSV:** `header`, `sep`, `encoding`

---

## 🔐 Security Patterns

### ✅ Best Practice: Externalize Secrets

```yaml
connections:
  prod_db:
    type: azure_sql
    host: ${DB_HOST}  # From environment variable
    auth_mode: key_vault
    key_vault_name: ${KEY_VAULT_NAME}
    secret_name: db-connection-string  # Secret stored in KV
```

**Never do this:**
```yaml
# ❌ NEVER COMMIT THIS
password: my_actual_password_123
api_key: sk_live_abc123xyz
```

**Security layers in Odibi:**
1. **Environment variables:** Config references like `${DB_HOST}`
2. **Azure Key Vault:** Secrets stored in Azure, fetched at runtime
3. **Managed Identity:** No credentials needed (Azure AD auth)

---

## 🔄 Retry & Error Handling

### Global Retry Config

```yaml
retry:
  max_attempts: 3
  backoff_seconds: 2.0
```

**When retries trigger:**
- Network failures (ADLS timeout)
- Transient database errors
- API rate limits

**Exponential backoff:**
- Attempt 1: Wait 2.0s
- Attempt 2: Wait 4.0s
- Attempt 3: Wait 8.0s

---

## 📖 Story Generation (Observability)

### Pattern: Centralized Story Output

```yaml
story:
  connection: outputs
  path: stories/
  max_sample_rows: 10
  auto_generate: true
```

**What stories contain:**
- Execution timeline and duration
- Data samples (first N rows)
- Lineage graph (DAG visualization)
- Errors and warnings

**Best practice:** Store stories separate from data (different connection).

---

## 🎨 Naming Conventions

### Observed in Odibi Configs

| Element | Convention | Example |
|---------|------------|---------|
| Connections | `snake_case` | `bronze`, `azure_lake`, `outputs` |
| Pipelines | `snake_case` | `bronze_to_silver`, `delta_time_travel` |
| Nodes | `verb_noun` | `load_raw_sales`, `clean_sales`, `save_silver` |
| Layers | `noun` | `transformation`, `aggregation`, `analytics` |

**Node naming pattern:**
- **Read nodes:** `load_*`, `read_*`
- **Transform nodes:** `clean_*`, `enrich_*`, `aggregate_*`
- **Write nodes:** `save_*`, `write_*`

---

## 📐 Multi-Layer Architecture

Odibi configs naturally map to medallion architecture:

```yaml
connections:
  bronze:  # Raw data
    type: azure_adls
    container: bronze
  
  silver:  # Cleaned data
    type: azure_adls
    container: silver
  
  gold:    # Analytics-ready
    type: azure_adls
    container: gold

pipelines:
  - pipeline: bronze_to_silver
    # Clean, validate, standardize
  
  - pipeline: silver_to_gold
    # Aggregate, join, business logic
```

**Separation benefits:**
- Clear data flow
- Independent scaling
- Role-based access (analysts only see gold)

---

## 🚀 Advanced Patterns

### Pattern 1: Node Dependencies (DAG)

```yaml
nodes:
  - name: read_sales
    read: {...}
  
  - name: read_customers
    read: {...}
  
  - name: join_sales_customers
    depends_on: [read_sales, read_customers]  # ← Wait for both
    transform: {...}
  
  - name: aggregate
    depends_on: [join_sales_customers]
    transform: {...}
```

**Execution order:**
1. `read_sales` and `read_customers` run in parallel
2. `join_sales_customers` waits for both
3. `aggregate` runs last

### Pattern 2: Format-Specific Options

```yaml
# Parquet with compression
write:
  format: parquet
  options:
    compression: snappy
    row_group_size: 128000000

# Delta with partitioning
write:
  format: delta
  mode: append
  options:
    partition_by: [year, month]
    mergeSchema: true

# CSV with custom delimiter
write:
  format: csv
  options:
    sep: '|'
    header: true
    encoding: utf-8
```

---

## 📚 Complete Example: Production Pipeline

```yaml
# Production-grade Odibi config
project: Sales Analytics Pipeline
version: "2.1.0"
owner: "data-engineering@company.com"
engine: pandas

connections:
  bronze:
    type: azure_adls
    account: ${STORAGE_ACCOUNT}
    container: bronze
    auth_mode: managed_identity
  
  silver:
    type: azure_adls
    account: ${STORAGE_ACCOUNT}
    container: silver
    auth_mode: managed_identity
  
  analytics_db:
    type: azure_sql
    host: ${DB_HOST}
    database: analytics
    auth_mode: key_vault
    key_vault_name: ${KEY_VAULT_NAME}
    secret_name: sql-connection-string

story:
  connection: silver
  path: observability/stories/
  max_sample_rows: 5

retry:
  max_attempts: 3
  backoff_seconds: 2.0

logging:
  level: INFO
  structured: true

pipelines:
  - pipeline: bronze_to_silver
    description: "Clean and validate raw sales data"
    layer: transformation
    
    nodes:
      # Load from Bronze
      - name: load_raw_sales
        read:
          connection: bronze
          path: sales/raw_sales.csv
          format: csv
        cache: true
      
      # Load dimension from SQL
      - name: load_customers
        read:
          connection: analytics_db
          format: sql
          table: dim_customer
        cache: true
      
      # Clean sales data
      - name: clean_sales
        depends_on: [load_raw_sales]
        transform:
          steps:
            - |
              SELECT * FROM load_raw_sales
              WHERE amount > 0
                AND transaction_date IS NOT NULL
      
      # Enrich with customer data
      - name: enrich_sales
        depends_on: [clean_sales, load_customers]
        transform:
          steps:
            - |
              SELECT
                s.*,
                c.customer_name,
                c.customer_segment
              FROM clean_sales s
              LEFT JOIN load_customers c
                ON s.customer_id = c.customer_id
      
      # Write to Silver as Delta
      - name: save_silver
        depends_on: [enrich_sales]
        write:
          connection: silver
          path: sales/enriched_sales.delta
          format: delta
          mode: append
          options:
            partition_by: [year, month]
            mergeSchema: true
```

---

## ✅ Best Practices Summary

1. **Security**
   - ✅ Use Key Vault or Managed Identity
   - ✅ Environment variables for config values
   - ❌ Never hardcode secrets

2. **Structure**
   - ✅ Separate connections by layer (bronze/silver/gold)
   - ✅ Use `cache: true` for reused data
   - ✅ Explicit `depends_on` for clarity

3. **Naming**
   - ✅ Consistent snake_case
   - ✅ Descriptive node names (`load_*`, `clean_*`, `save_*`)
   - ✅ Logical pipeline names

4. **Formats**
   - ✅ Parquet for large datasets
   - ✅ Delta for production (ACID + time travel)
   - ✅ CSV for compatibility/debugging

5. **Observability**
   - ✅ Enable story generation
   - ✅ Structured logging in production
   - ✅ Separate story storage

---

## 🔗 References

- [Odibi Configuration Docs](../../Odibi/docs/CONFIGURATION_EXPLAINED.md)
- [Delta Lake Best Practices](https://docs.delta.io/latest/best-practices.html)
- [Azure Key Vault Integration](https://learn.microsoft.com/en-us/azure/key-vault/)
