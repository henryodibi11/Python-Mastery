# Odibi Configuration Reference

Complete API reference for Odibi's configuration system.

**Source**: `c:/Users/hodibi/OneDrive - Ingredion/Desktop/Repos/Odibi/odibi/config.py` (313 lines)

---

## 📚 Table of Contents

1. [Enums](#enums)
2. [Connection Configs](#connection-configs)
3. [Node Operation Configs](#node-operation-configs)
4. [Pipeline Hierarchy](#pipeline-hierarchy)
5. [Project-Level Configs](#project-level-configs)
6. [Complete Examples](#complete-examples)

---

## Enums

### EngineType

Execution engine for running pipelines.

```python
class EngineType(str, Enum):
    SPARK = "spark"
    PANDAS = "pandas"
```

**Usage in YAML**:
```yaml
engine: pandas  # or "spark"
```

---

### ConnectionType

Supported data connection types.

```python
class ConnectionType(str, Enum):
    LOCAL = "local"
    AZURE_BLOB = "azure_blob"
    DELTA = "delta"
    SQL_SERVER = "sql_server"
```

**Usage in YAML**:
```yaml
connections:
  my_local:
    type: local
```

---

### WriteMode

How to handle existing data when writing.

```python
class WriteMode(str, Enum):
    OVERWRITE = "overwrite"  # Replace existing data
    APPEND = "append"        # Add to existing data
```

**Usage in YAML**:
```yaml
write:
  mode: overwrite  # or "append"
```

---

### LogLevel

Logging verbosity levels.

```python
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
```

**Usage in YAML**:
```yaml
logging:
  level: INFO
```

---

## Connection Configs

### BaseConnectionConfig

Base class for all connection types.

**Fields**:
- `type: ConnectionType` - Connection type discriminator
- `validation_mode: str = "lazy"` - When to validate connection ("lazy" or "eager")

---

### LocalConnectionConfig

Local filesystem access.

**Inherits**: `BaseConnectionConfig`

**Fields**:
- `type: ConnectionType = LOCAL` - Always "local"
- `base_path: str = "./data"` - Base directory for file operations

**YAML Example**:
```yaml
connections:
  local:
    type: local
    base_path: /data/warehouse
```

---

### AzureBlobConnectionConfig

Azure Blob Storage access.

**Inherits**: `BaseConnectionConfig`

**Fields**:
- `type: ConnectionType = AZURE_BLOB` - Always "azure_blob"
- `account_name: str` - Azure storage account name (required)
- `container: str` - Blob container name (required)
- `auth: Dict[str, str] = {}` - Authentication details (method, credentials)

**YAML Example**:
```yaml
connections:
  azure:
    type: azure_blob
    account_name: mystorageaccount
    container: data
    auth:
      method: sas_token
      token: "sv=2021-06..."
```

---

### DeltaConnectionConfig

Delta Lake / Unity Catalog access.

**Inherits**: `BaseConnectionConfig`

**Fields**:
- `type: ConnectionType = DELTA` - Always "delta"
- `catalog: str` - Catalog name (required)
- `schema_name: str` - Schema name (required, use `schema` in YAML)

**YAML Example**:
```yaml
connections:
  delta:
    type: delta
    catalog: main
    schema: bronze  # Maps to schema_name in Python
```

**Note**: Uses `alias="schema"` to avoid Python keyword conflict.

---

### SQLServerConnectionConfig

Microsoft SQL Server access.

**Inherits**: `BaseConnectionConfig`

**Fields**:
- `type: ConnectionType = SQL_SERVER` - Always "sql_server"
- `host: str` - Server hostname (required)
- `database: str` - Database name (required)
- `port: int = 1433` - Server port (default 1433)
- `auth: Dict[str, str] = {}` - Authentication (username, password, or Windows auth)

**YAML Example**:
```yaml
connections:
  sqlserver:
    type: sql_server
    host: localhost
    database: Analytics
    port: 1433
    auth:
      username: sa
      password: "..."
```

---

## Node Operation Configs

### ReadConfig

Configuration for reading data.

**Fields**:
- `connection: str` - Connection name from `connections` (required)
- `format: str` - Data format: "csv", "parquet", "delta", "json" (required)
- `table: Optional[str] = None` - Table name for SQL/Delta sources
- `path: Optional[str] = None` - File path for file-based sources
- `options: Dict[str, Any] = {}` - Format-specific options (headers, delimiter, etc.)

**Validation**:
- ✅ Must provide either `table` OR `path` (enforced by model validator)

**YAML Examples**:
```yaml
# File-based read
read:
  connection: local
  format: csv
  path: input/sales.csv
  options:
    header: true
    delimiter: ","

# Table-based read
read:
  connection: delta
  format: delta
  table: bronze.sales
```

---

### TransformStep

Single transformation operation.

**Fields**:
- `sql: Optional[str] = None` - SQL query string
- `function: Optional[str] = None` - Named function to call
- `operation: Optional[str] = None` - Named operation to apply
- `params: Dict[str, Any] = {}` - Parameters for function/operation

**Validation**:
- ✅ Exactly ONE of `sql`, `function`, or `operation` must be provided

**YAML Examples**:
```yaml
# SQL transformation
- sql: SELECT * FROM data WHERE amount > 0

# Function transformation
- function: deduplicate
  params:
    columns: [id, email]

# Operation transformation
- operation: filter_nulls
  params:
    columns: [customer_id, amount]
```

---

### TransformConfig

Configuration for data transformations.

**Fields**:
- `steps: List[Union[str, TransformStep]]` - Transformation steps (required)

**Note**: Steps can be simple SQL strings OR structured `TransformStep` objects.

**YAML Examples**:
```yaml
# Simple SQL strings
transform:
  steps:
    - SELECT * FROM data WHERE valid = true
    - SELECT customer_id, SUM(amount) as total FROM data GROUP BY customer_id

# Structured steps
transform:
  steps:
    - sql: SELECT * FROM data
    - function: clean_emails
    - operation: remove_duplicates
      params:
        key_columns: [id]
```

---

### ValidationConfig

Data quality validation rules.

**Fields**:
- `schema_validation: Optional[Dict[str, Any]] = None` - Schema rules (use `schema` in YAML)
- `not_empty: bool = False` - Ensure result has at least one row
- `no_nulls: List[str] = []` - Columns that must not contain nulls

**YAML Example**:
```yaml
validation:
  schema:
    columns:
      id: integer
      email: string
  not_empty: true
  no_nulls: [customer_id, transaction_id, amount]
```

---

### WriteConfig

Configuration for writing data.

**Fields**:
- `connection: str` - Connection name from `connections` (required)
- `format: str` - Output format: "csv", "parquet", "delta", "json" (required)
- `table: Optional[str] = None` - Table name for SQL/Delta targets
- `path: Optional[str] = None` - File path for file-based targets
- `mode: WriteMode = OVERWRITE` - Write mode (overwrite or append)
- `options: Dict[str, Any] = {}` - Format-specific write options

**Validation**:
- ✅ Must provide either `table` OR `path` (enforced by model validator)

**YAML Examples**:
```yaml
# File-based write
write:
  connection: local
  format: parquet
  path: output/results.parquet
  mode: overwrite

# Table-based write
write:
  connection: delta
  format: delta
  table: silver.clean_sales
  mode: append
```

---

## Pipeline Hierarchy

### NodeConfig

Atomic unit of pipeline execution.

**Fields**:
- `name: str` - Unique node identifier (required)
- `description: Optional[str] = None` - Human-readable description
- `depends_on: List[str] = []` - Names of nodes this depends on
- `read: Optional[ReadConfig] = None` - Read operation
- `transform: Optional[TransformConfig] = None` - Transform operations
- `write: Optional[WriteConfig] = None` - Write operation
- `cache: bool = False` - Cache result for reuse
- `validation: Optional[ValidationConfig] = None` - Data quality checks

**Validation**:
- ✅ At least one of `read`, `transform`, or `write` must be provided

**YAML Example**:
```yaml
- name: clean_sales
  description: Clean and validate sales data
  depends_on: [raw_sales]
  transform:
    steps:
      - SELECT * FROM raw_sales WHERE amount > 0
  write:
    connection: delta
    format: delta
    table: silver.sales
    mode: overwrite
  cache: true
  validation:
    not_empty: true
    no_nulls: [customer_id, amount]
```

---

### PipelineConfig

Collection of nodes forming a data pipeline.

**Fields**:
- `pipeline: str` - Pipeline identifier (required)
- `description: Optional[str] = None` - Pipeline description
- `layer: Optional[str] = None` - Logical layer: "bronze", "silver", "gold"
- `nodes: List[NodeConfig]` - List of nodes in this pipeline (required)

**Validation**:
- ✅ All node names must be unique within the pipeline

**YAML Example**:
```yaml
pipelines:
  - pipeline: sales_processing
    description: Process daily sales data
    layer: silver
    nodes:
      - name: read_raw
        read:
          connection: delta
          format: delta
          table: bronze.sales
      
      - name: clean_data
        depends_on: [read_raw]
        transform:
          steps:
            - SELECT * FROM read_raw WHERE amount > 0
      
      - name: write_clean
        depends_on: [clean_data]
        write:
          connection: delta
          format: delta
          table: silver.sales
```

---

## Project-Level Configs

### RetryConfig

Retry behavior for failed operations.

**Fields**:
- `enabled: bool = True` - Enable retries
- `max_attempts: int = 3` - Max retry attempts (1-10)
- `backoff: str = "exponential"` - Backoff strategy: "exponential", "linear", "constant"

**YAML Example**:
```yaml
retry:
  enabled: true
  max_attempts: 5
  backoff: exponential
```

---

### LoggingConfig

Logging configuration.

**Fields**:
- `level: LogLevel = INFO` - Log level
- `structured: bool = False` - Output structured JSON logs
- `metadata: Dict[str, Any] = {}` - Extra metadata in all logs

**YAML Example**:
```yaml
logging:
  level: DEBUG
  structured: true
  metadata:
    team: data-engineering
    environment: production
```

---

### StoryConfig

Odibi's execution report configuration.

**Fields**:
- `connection: str` - Connection name for story output (required)
- `path: str` - Path for story files (required)
- `max_sample_rows: int = 10` - Max rows in data samples (0-100)
- `auto_generate: bool = True` - Automatically generate stories

**Validation**:
- ✅ `connection` must exist in `connections` dict

**YAML Example**:
```yaml
story:
  connection: local
  path: stories/
  max_sample_rows: 5
  auto_generate: true
```

---

### ProjectConfig

Top-level project configuration.

**Fields**:

**Mandatory**:
- `project: str` - Project name (required)
- `engine: EngineType = PANDAS` - Execution engine
- `connections: Dict[str, Dict[str, Any]]` - Named connections (required)
- `pipelines: List[PipelineConfig]` - Pipeline definitions (required)
- `story: StoryConfig` - Story configuration (required)

**Optional**:
- `description: Optional[str] = None` - Project description
- `version: str = "1.0.0"` - Project version
- `owner: Optional[str] = None` - Project owner/contact
- `retry: RetryConfig = RetryConfig()` - Retry settings
- `logging: LoggingConfig = LoggingConfig()` - Logging settings

**Validation**:
- ✅ `story.connection` must exist in `connections`
- ❌ `environments` field blocked until Phase 3

---

## Complete Examples

### Minimal Project

Simplest valid project configuration.

```yaml
project: minimal_pipeline
engine: pandas

connections:
  local:
    type: local
    base_path: ./data

story:
  connection: local
  path: stories/

pipelines:
  - pipeline: simple
    nodes:
      - name: process
        read:
          connection: local
          format: csv
          path: input.csv
        write:
          connection: local
          format: csv
          path: output.csv
```

---

### Production Project

Full-featured production configuration.

```yaml
project: sales_analytics
description: Daily sales data processing and analytics
version: 2.1.0
owner: data-team@company.com
engine: spark

# === CONNECTIONS ===
connections:
  bronze:
    type: delta
    catalog: main
    schema: bronze
  
  silver:
    type: delta
    catalog: main
    schema: silver
  
  gold:
    type: delta
    catalog: main
    schema: gold
  
  local:
    type: local
    base_path: /mnt/data

# === STORY CONFIGURATION ===
story:
  connection: local
  path: execution_stories/
  max_sample_rows: 5
  auto_generate: true

# === RETRY & LOGGING ===
retry:
  enabled: true
  max_attempts: 3
  backoff: exponential

logging:
  level: INFO
  structured: true
  metadata:
    team: data-engineering
    environment: production
    cost_center: 12345

# === PIPELINES ===
pipelines:
  # Bronze: Raw data ingestion
  - pipeline: bronze_ingestion
    layer: bronze
    description: Ingest raw sales data
    nodes:
      - name: ingest_sales
        description: Read raw sales CSV files
        read:
          connection: local
          format: csv
          path: raw/sales/*.csv
          options:
            header: true
            inferSchema: true
            mergeSchema: true
        write:
          connection: bronze
          format: delta
          table: sales
          mode: append
        validation:
          not_empty: true
          no_nulls: [transaction_id]
  
  # Silver: Clean and validate
  - pipeline: silver_transformation
    layer: silver
    description: Clean and enrich sales data
    nodes:
      - name: clean_sales
        description: Remove invalid records
        read:
          connection: bronze
          format: delta
          table: sales
        transform:
          steps:
            - SELECT * FROM data WHERE amount > 0
            - SELECT * FROM data WHERE customer_id IS NOT NULL
            - SELECT DISTINCT * FROM data
        cache: true
        validation:
          not_empty: true
          no_nulls: [customer_id, amount, transaction_id]
      
      - name: enrich_sales
        description: Add customer and product dimensions
        depends_on: [clean_sales]
        transform:
          steps:
            - |
              SELECT 
                s.*,
                c.customer_name,
                c.segment,
                p.product_name,
                p.category
              FROM clean_sales s
              LEFT JOIN bronze.customers c ON s.customer_id = c.id
              LEFT JOIN bronze.products p ON s.product_id = p.id
        write:
          connection: silver
          format: delta
          table: sales_enriched
          mode: overwrite
  
  # Gold: Business aggregates
  - pipeline: gold_aggregation
    layer: gold
    description: Business-level aggregations
    nodes:
      - name: daily_sales_summary
        description: Aggregate sales by date and region
        read:
          connection: silver
          format: delta
          table: sales_enriched
        transform:
          steps:
            - |
              SELECT 
                DATE(transaction_date) as sale_date,
                region,
                segment,
                COUNT(DISTINCT transaction_id) as transaction_count,
                COUNT(DISTINCT customer_id) as customer_count,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_order_value
              FROM data
              GROUP BY DATE(transaction_date), region, segment
        write:
          connection: gold
          format: delta
          table: daily_sales_summary
          mode: overwrite
        validation:
          not_empty: true
```

---

## Validation Rules Summary

| Config Class | Validation Rule | Enforced By |
|--------------|----------------|-------------|
| `ReadConfig` | Must have `table` OR `path` | `@model_validator` |
| `WriteConfig` | Must have `table` OR `path` | `@model_validator` |
| `TransformStep` | Exactly one of: `sql`, `function`, `operation` | `@model_validator` |
| `NodeConfig` | At least one of: `read`, `transform`, `write` | `@model_validator` |
| `PipelineConfig` | Unique node names | `@field_validator` |
| `ProjectConfig` | `story.connection` exists in `connections` | `@model_validator` |
| `RetryConfig` | `max_attempts` between 1 and 10 | `Field(ge=1, le=10)` |
| `RetryConfig` | `backoff` matches pattern | `Field(pattern=...)` |
| `StoryConfig` | `max_sample_rows` between 0 and 100 | `Field(ge=0, le=100)` |

---

## Common Patterns

### Pattern: Multi-Source Joins

```yaml
nodes:
  - name: read_sales
    read:
      connection: delta
      format: delta
      table: sales
  
  - name: read_customers
    read:
      connection: delta
      format: delta
      table: customers
  
  - name: join_data
    depends_on: [read_sales, read_customers]
    transform:
      steps:
        - |
          SELECT s.*, c.customer_name, c.segment
          FROM read_sales s
          JOIN read_customers c ON s.customer_id = c.id
```

### Pattern: Incremental Loading

```yaml
nodes:
  - name: load_incremental
    read:
      connection: delta
      format: delta
      table: raw_events
      options:
        readChangeFeed: true
        startingVersion: 42
    write:
      connection: delta
      format: delta
      table: processed_events
      mode: append  # Key: append, not overwrite
```

### Pattern: Conditional Transforms

```yaml
transform:
  steps:
    - sql: SELECT * FROM data WHERE date >= '2024-01-01'
    - function: apply_business_rules
      params:
        rule_set: "Q1_2024"
    - operation: flag_anomalies
      params:
        threshold: 3.0
```

---

## Loading Configs in Python

```python
import yaml
from odibi.config import ProjectConfig

# Load from YAML file
with open("project.yaml") as f:
    raw_config = yaml.safe_load(f)

# Validate with Pydantic
config = ProjectConfig(**raw_config)

# Access validated config
print(f"Project: {config.project}")
print(f"Engine: {config.engine}")
print(f"Pipelines: {[p.pipeline for p in config.pipelines]}")

# Iterate nodes
for pipeline in config.pipelines:
    for node in pipeline.nodes:
        print(f"Node: {node.name}")
        if node.read:
            print(f"  Reads from: {node.read.table or node.read.path}")
```

---

## Error Handling

```python
from pydantic import ValidationError

try:
    config = ProjectConfig(**raw_config)
except ValidationError as e:
    print("Configuration errors:")
    for error in e.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        message = error['msg']
        print(f"  {field}: {message}")
```

**Example Output**:
```
Configuration errors:
  story -> connection: Story connection 'azure' not found. Available connections: local, delta
  pipelines -> 0 -> nodes -> 1 -> name: Duplicate node names found: {'process_data'}
  retry -> max_attempts: Input should be less than or equal to 10
```

---

## Version History

- **Phase 1**: Core config system (current)
- **Phase 2**: Pipeline discovery (planned)
- **Phase 3**: Environment overrides (planned)

---

**Last Updated**: Based on `config.py` as of lesson creation
**Lines of Code**: 313
**Total Config Classes**: 20
**Enums**: 4
**Connection Types**: 4
**Validation Rules**: 8+
