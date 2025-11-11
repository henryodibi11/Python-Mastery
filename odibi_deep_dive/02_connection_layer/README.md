# 02: Connection Layer Deep Dive

🎯 **Problem**: How do you write code that works with local files, Azure Data Lake, S3, GCS, and Databricks without changing your logic?

## 🦉 First Principles

**Storage abstraction**: Separate the "what" (read a table) from the "where" (local disk vs cloud storage).

**Key insights**:
- All storage systems provide: paths, reading, writing
- Differences: authentication, URI format, path resolution
- Solution: Common interface (`BaseConnection`) with storage-specific implementations

## What You'll Learn

1. **BaseConnection ABC** - The interface contract all connections must fulfill
2. **LocalConnection** - Simple filesystem with base path resolution
3. **AzureADLS** - Azure Data Lake with Key Vault authentication and Spark configuration
4. **LocalDBFS** - Mock Databricks filesystem for local development
5. **Path resolution strategies** - How relative paths become full URIs
6. **Storage options** - Passing credentials to pandas/fsspec
7. **Connection validation** - Fail fast with clear error messages

## Files

- `lesson.ipynb` - Interactive walkthrough of all connection types
- `exercises.ipynb` - Build S3Connection and GCSConnection
- `solutions.ipynb` - Reference implementations
- `connection_comparison.md` - Side-by-side comparison table

## 🔍 Real Code

This lesson uses actual implementations from:
- [odibi/connections/base.py](file:///c:/Users/hodibi/OneDrive%20-%20Ingredion/Desktop/Repos/Odibi/odibi/connections/base.py)
- [odibi/connections/local.py](file:///c:/Users/hodibi/OneDrive%20-%20Ingredion/Desktop/Repos/Odibi/odibi/connections/local.py)
- [odibi/connections/azure_adls.py](file:///c:/Users/hodibi/OneDrive%20-%20Ingredion/Desktop/Repos/Odibi/odibi/connections/azure_adls.py)
- [odibi/connections/local_dbfs.py](file:///c:/Users/hodibi/OneDrive%20-%20Ingredion/Desktop/Repos/Odibi/odibi/connections/local_dbfs.py)

## Prerequisites

- Understanding of Python ABCs (abstract base classes)
- Basic knowledge of cloud storage concepts
- Familiarity with authentication methods

## Next Steps

After mastering connections, proceed to:
- **03: YAML Configuration** - Define connections in config files
- **04: Layer System** - Read/write data through layers using connections
