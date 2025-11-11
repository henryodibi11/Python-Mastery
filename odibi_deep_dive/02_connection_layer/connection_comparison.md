# Connection Type Comparison

## Quick Reference Table

| Feature | LocalConnection | AzureADLS | LocalDBFS | S3 (Exercise) | GCS (Exercise) |
|---------|----------------|-----------|-----------|---------------|----------------|
| **Use Case** | Local development | Azure production | Databricks local testing | AWS production | GCP production |
| **URI Format** | `/path/to/file` | `abfss://container@account.dfs.core.windows.net/path` | `/local/path` (mapped from `dbfs:/`) | `s3://bucket/path` | `gs://bucket/path` |
| **Authentication** | None | Key Vault or Direct Key | None | Access Key + Secret | Service Account JSON |
| **Path Prefix** | ✅ (base_path) | ✅ (path_prefix) | ❌ | ✅ (prefix) | ✅ (prefix) |
| **Spark Support** | ❌ | ✅ (configure_spark) | ❌ | ✅ | ✅ |
| **Pandas Support** | ✅ | ✅ (storage_options) | ✅ | ✅ (storage_options) | ✅ (storage_options) |
| **Validation** | Creates directory | Checks auth config | None | Checks credentials | Checks bucket |
| **Key Caching** | N/A | ✅ | N/A | ❌ | ❌ |

## Detailed Comparison

### LocalConnection

**Strengths**:
- Simple and fast
- No dependencies
- Works offline
- Auto-creates directories

**Limitations**:
- Not suitable for production
- No authentication
- Limited to single machine

**Best For**:
- Development
- Testing
- Prototyping

**Example**:
```python
conn = LocalConnection(base_path="./my_project/data")
path = conn.get_path("raw/sales.parquet")
# Returns: /full/path/to/my_project/data/raw/sales.parquet
```

---

### AzureADLS

**Strengths**:
- Production-ready authentication (Key Vault)
- Multi-account support
- Spark integration
- Timeout protection
- Key caching for performance

**Limitations**:
- Requires Azure libraries
- Complex configuration
- Network dependent

**Best For**:
- Azure Data Lake production workloads
- Enterprise pipelines
- Multi-environment deployments

**Example**:
```python
conn = AzureADLS(
    account="mystorageaccount",
    container="datalake",
    path_prefix="analytics/v2",
    auth_mode="key_vault",
    key_vault_name="my-keyvault",
    secret_name="storage-key"
)
path = conn.get_path("raw/sales.parquet")
# Returns: abfss://datalake@mystorageaccount.dfs.core.windows.net/analytics/v2/raw/sales.parquet

# Use with pandas
df = pd.read_parquet(path, storage_options=conn.pandas_storage_options())

# Configure Spark
conn.configure_spark(spark)
df = spark.read.parquet(path)
```

---

### LocalDBFS

**Strengths**:
- Enables local Databricks testing
- No dependencies
- Simple path mapping

**Limitations**:
- Mock only (not real DBFS)
- No validation
- No authentication

**Best For**:
- Testing Databricks notebooks locally
- Development without cloud access
- CI/CD pipelines

**Example**:
```python
conn = LocalDBFS(root="./mock_dbfs")
path = conn.get_path("dbfs:/FileStore/raw/sales.parquet")
# Returns: /full/path/to/mock_dbfs/FileStore/raw/sales.parquet
```

---

### S3Connection (Exercise)

**Strengths**:
- Wide AWS ecosystem support
- Familiar to many developers
- Good fsspec integration

**Limitations**:
- Requires AWS credentials
- Region-specific
- Network dependent

**Best For**:
- AWS production workloads
- S3-based data lakes
- Cross-region data access

**Example**:
```python
conn = S3Connection(
    bucket="my-data-bucket",
    prefix="analytics",
    region="us-west-2",
    access_key_id="AKIA...",
    secret_access_key="secret..."
)
path = conn.get_path("raw/sales.parquet")
# Returns: s3://my-data-bucket/analytics/raw/sales.parquet
```

---

### GCSConnection (Exercise)

**Strengths**:
- GCP native
- Good BigQuery integration
- Project-scoped access

**Limitations**:
- Requires GCP credentials
- Less common than S3/Azure

**Best For**:
- GCP production workloads
- BigQuery data pipelines
- Google Cloud ecosystem

**Example**:
```python
conn = GCSConnection(
    bucket="my-gcs-bucket",
    prefix="analytics",
    project="my-project-123",
    credentials_path="/path/to/service-account.json"
)
path = conn.get_path("raw/sales.parquet")
# Returns: gs://my-gcs-bucket/analytics/raw/sales.parquet
```

---

## Path Resolution Strategies

### Strategy 1: Simple Join (LocalConnection)
```
base_path + "/" + relative_path
./data + "/" + raw/sales.parquet = ./data/raw/sales.parquet
```

### Strategy 2: URI Construction (AzureADLS, S3, GCS)
```
protocol://container@account/prefix/relative_path

abfss://data@account.dfs.core.windows.net/team/project/raw/sales.parquet
s3://bucket/analytics/v2/raw/sales.parquet
gs://bucket/analytics/raw/sales.parquet
```

### Strategy 3: Protocol Mapping (LocalDBFS)
```
dbfs:/FileStore/raw/sales.parquet
  → strip "dbfs:/"
  → join with root
/tmp/dbfs/FileStore/raw/sales.parquet
```

---

## Authentication Patterns

### No Auth (Local, LocalDBFS)
- Simplest
- Use for development only

### Direct Key (AzureADLS direct_key, S3, GCS)
- Credentials passed directly
- Good for development
- ⚠️ Not recommended for production

### Secret Management (AzureADLS key_vault)
- Credentials fetched from vault
- Production-ready
- Requires additional setup
- Best security practice

---

## Storage Options for Pandas

### AzureADLS
```python
{
    "account_name": "mystorageaccount",
    "account_key": "key_from_vault_or_direct"
}
```

### S3Connection
```python
{
    "key": "AKIA...",
    "secret": "secret...",
    "client_kwargs": {"region_name": "us-west-2"}
}
```

### GCSConnection
```python
{
    "project": "my-project-123",
    "token": "/path/to/service-account.json"
}
```

---

## When to Use Each

| Scenario | Recommended Connection |
|----------|----------------------|
| Local development | `LocalConnection` |
| Azure Data Lake production | `AzureADLS` (key_vault mode) |
| Azure development/testing | `AzureADLS` (direct_key mode) |
| Testing Databricks locally | `LocalDBFS` |
| AWS production | `S3Connection` |
| GCP production | `GCSConnection` |
| Multi-cloud strategy | Mix of S3, GCS, AzureADLS with factory pattern |

---

## Connection Factory Pattern

To support multiple connection types from config:

```python
def create_connection(config: dict) -> BaseConnection:
    conn_type = config["type"]
    
    if conn_type == "local":
        return LocalConnection(**config)
    elif conn_type == "azure_adls":
        return AzureADLS(**config)
    elif conn_type == "local_dbfs":
        return LocalDBFS(**config)
    elif conn_type == "s3":
        return S3Connection(**config)
    elif conn_type == "gcs":
        return GCSConnection(**config)
    else:
        raise ValueError(f"Unknown connection type: {conn_type}")
```

This enables YAML-driven configuration:

```yaml
connections:
  dev:
    type: local
    base_path: ./data
  
  prod:
    type: azure_adls
    account: prodaccount
    container: datalake
    auth_mode: key_vault
    key_vault_name: prod-kv
    secret_name: storage-key
```

---

## Performance Considerations

| Connection | Speed | Network | Latency |
|-----------|-------|---------|---------|
| LocalConnection | ⚡⚡⚡ Fast | None | Minimal |
| AzureADLS | ⚡⚡ Medium | Required | Key Vault fetch (~100-500ms first call, cached after) |
| LocalDBFS | ⚡⚡⚡ Fast | None | Minimal |
| S3Connection | ⚡⚡ Medium | Required | Region-dependent |
| GCSConnection | ⚡⚡ Medium | Required | Region-dependent |

**Tip**: AzureADLS caches keys to avoid repeated vault calls. S3/GCS connections could benefit from similar caching.

---

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use secret management** (Key Vault, AWS Secrets Manager, etc.) in production
3. **Validate paths** to prevent traversal attacks
4. **Use direct keys only** for local development
5. **Set warnings** for production misconfigurations (like AzureADLS does)
6. **Rotate credentials** regularly
7. **Use minimal permissions** (read-only when possible)
