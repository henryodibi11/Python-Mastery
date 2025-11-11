"""
Type System Exercises

Complete the TODO sections to practice type hints and Pydantic models.
Run test_exercises.py to validate your solutions.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# ==============================================================================
# Exercise 1: Basic Pydantic Model
# ==============================================================================

# TODO: Create a DatabaseConfig model with:
# - host: str (required)
# - port: int (default 5432, must be between 1 and 65535)
# - database: str (required)
# - username: str (required)
# - password: Optional[str] (default None)
# - pool_size: int (default 10, must be >= 1)

class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    pass  # TODO: Implement


# ==============================================================================
# Exercise 2: Field Validators
# ==============================================================================

# TODO: Create a DatasetConfig model with:
# - name: str (required, must be alphanumeric + underscores, lowercase)
# - columns: List[str] (required, must be non-empty, no duplicates)
# - partition_cols: List[str] (default empty list)
# 
# Add validators:
# - name: strip whitespace, convert to lowercase, validate format
# - columns: ensure non-empty, ensure no duplicates
# - partition_cols: ensure all partition columns exist in columns

class DatasetConfig(BaseModel):
    """Dataset configuration with validation."""
    pass  # TODO: Implement


# ==============================================================================
# Exercise 3: Model Validators (Cross-field validation)
# ==============================================================================

# TODO: Create an enum for FileFormat with: CSV, PARQUET, JSON, DELTA

class FileFormat(str, Enum):
    """Supported file formats."""
    pass  # TODO: Implement


# TODO: Create a FileConfig model with:
# - path: Optional[str] = None
# - table: Optional[str] = None
# - format: FileFormat (required)
# - options: Dict[str, Any] (default empty dict)
#
# Add model validator:
# - Ensure exactly one of path or table is provided (not both, not neither)
# - If format is DELTA, table must be provided (not path)

class FileConfig(BaseModel):
    """File or table configuration."""
    pass  # TODO: Implement


# ==============================================================================
# Exercise 4: Nested Models
# ==============================================================================

# TODO: Create a ScheduleConfig model with:
# - cron: Optional[str] = None (cron expression)
# - interval_seconds: Optional[int] = None (must be >= 60 if provided)
#
# Add model validator:
# - Ensure exactly one of cron or interval_seconds is provided

class ScheduleConfig(BaseModel):
    """Schedule configuration."""
    pass  # TODO: Implement


# TODO: Create a JobConfig model with:
# - name: str (required, alphanumeric + underscores)
# - description: Optional[str] = None
# - source: FileConfig (required)
# - target: FileConfig (required)
# - schedule: Optional[ScheduleConfig] = None
# - enabled: bool (default True)
#
# Add validators:
# - name: validate format
# - Ensure source and target are different (different path or table)

class JobConfig(BaseModel):
    """Complete job configuration."""
    pass  # TODO: Implement


# ==============================================================================
# Exercise 5: Union Types
# ==============================================================================

# TODO: Create connection config models:
# - LocalStorageConfig: type="local", base_path: str
# - S3Config: type="s3", bucket: str, region: str, prefix: Optional[str] = ""
# - AzureBlobConfig: type="azure", account: str, container: str
#
# Create StorageConfig as Union of the three types

class LocalStorageConfig(BaseModel):
    """Local filesystem storage."""
    pass  # TODO: Implement


class S3Config(BaseModel):
    """AWS S3 storage."""
    pass  # TODO: Implement


class AzureBlobConfig(BaseModel):
    """Azure Blob storage."""
    pass  # TODO: Implement


# TODO: Create a type alias for the union
StorageConfig = None  # TODO: Implement Union type


# ==============================================================================
# Exercise 6: Advanced - Complete Pipeline Config
# ==============================================================================

# TODO: Create a complete PipelineConfig model with:
# - pipeline: str (required, alphanumeric + underscores)
# - description: Optional[str] = None
# - storage: StorageConfig (required)
# - jobs: List[JobConfig] (required, non-empty)
# - max_parallel: int (default 5, must be >= 1)
# - retry_attempts: int (default 3, must be >= 0, <= 10)
#
# Add validators:
# - pipeline: validate format
# - jobs: ensure non-empty, ensure unique job names
# - jobs: ensure no circular dependencies (job A depends on B, B depends on A)

class PipelineConfig(BaseModel):
    """Complete pipeline configuration."""
    pass  # TODO: Implement


# ==============================================================================
# BONUS: Complex Validation
# ==============================================================================

# TODO (BONUS): Add a method to PipelineConfig:
# - build_dependency_graph() -> Dict[str, List[str]]
#   Returns mapping of job name -> list of jobs that depend on it
#
# TODO (BONUS): Add a validator to detect circular dependencies
# Hint: Use depth-first search or topological sort
