"""
Type System Lesson: From Type Hints to Pydantic

Learn the type system patterns that power Odibi's fail-fast validation.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from dataclasses import dataclass
from enum import Enum


# ==============================================================================
# 🎯 THE PROBLEM
# ==============================================================================

def process_pipeline_bad(config):
    """Runtime disaster waiting to happen."""
    # What type is config? Dictionary? Object? None?
    # What fields exist? What are their types?
    # When does this fail? After 3 hours of processing.
    
    name = config["name"]  # KeyError if missing
    timeout = config["timeout"] + 10  # TypeError if string
    nodes = config["nodes"][0]  # IndexError if empty
    
    return f"Processing {name} with {len(nodes)} nodes"


def process_pipeline_better(config: Dict[str, Any]) -> str:
    """Type hints help, but don't prevent errors."""
    # We know it's a dict, but:
    # - What keys are required?
    # - What are the value types?
    # - Still fails at runtime
    
    name = config["name"]
    timeout = config.get("timeout", 30)  # Better, but manual
    nodes = config.get("nodes", [])
    
    return f"Processing {name} with {len(nodes)} nodes"


# ==============================================================================
# 🦉 FIRST PRINCIPLES
# ==============================================================================

"""
Type System Hierarchy (Simple → Powerful):

1. Type Hints (PEP 484)
   - Documentation that static analyzers can check
   - No runtime enforcement
   - Free documentation
   
2. Dataclasses (PEP 557)
   - Auto-generate __init__, __repr__, __eq__
   - Type hints required
   - No validation
   
3. Pydantic (Runtime Validation)
   - Parse/validate/serialize data
   - Type coercion (e.g., "123" → 123)
   - Custom validators
   - Fail-fast at instantiation

Odibi Choice: Pydantic
Why? Config loaded once, validated immediately, used safely everywhere.
"""


# ==============================================================================
# ⚡ MINIMAL EXAMPLE: Type Hints
# ==============================================================================

def calculate_discount(price: float, discount: float = 0.1) -> float:
    """Type hints: document inputs and outputs."""
    return price * (1 - discount)


def process_items(items: List[str]) -> Dict[str, int]:
    """Generic types: collections with element types."""
    return {item: len(item) for item in items}


def find_user(user_id: int) -> Optional[Dict[str, str]]:
    """Optional[T]: value or None."""
    if user_id == 1:
        return {"name": "Alice", "role": "admin"}
    return None


def handle_config(config: Union[str, Dict[str, Any]]) -> str:
    """Union: one of several types."""
    if isinstance(config, str):
        return f"Loading from {config}"
    return f"Using provided config with {len(config)} keys"


# ==============================================================================
# ⚡ MINIMAL EXAMPLE: Dataclasses
# ==============================================================================

@dataclass
class User:
    """Dataclass: auto-generates __init__, __repr__, __eq__."""
    name: str
    age: int
    email: Optional[str] = None
    active: bool = True


def demo_dataclass():
    user = User(name="Bob", age=30)
    print(user)  # User(name='Bob', age=30, email=None, active=True)
    
    # But no validation!
    bad_user = User(name=123, age="thirty")  # Type checker warns, runtime allows
    print(bad_user)  # Works but wrong


# ==============================================================================
# ⚡ MINIMAL EXAMPLE: Pydantic Basics
# ==============================================================================

class UserModel(BaseModel):
    """Pydantic: validation + parsing + serialization."""
    name: str
    age: int
    email: Optional[str] = None
    active: bool = True


def demo_pydantic_basic():
    # Valid creation
    user = UserModel(name="Alice", age=25)
    print(user.model_dump())  # {'name': 'Alice', 'age': 25, 'email': None, 'active': True}
    
    # Type coercion
    user2 = UserModel(name="Bob", age="30")  # String → int coercion
    print(user2.age, type(user2.age))  # 30 <class 'int'>
    
    # Validation failure
    try:
        bad_user = UserModel(name="Charlie", age="thirty")  # Can't coerce
    except Exception as e:
        print(f"Validation error: {type(e).__name__}")


# ==============================================================================
# 🔍 ODIBI ANALYSIS: Field Constraints
# ==============================================================================

class ConnectionConfig(BaseModel):
    """Field constraints: defaults, descriptions, validation."""
    
    name: str = Field(description="Connection name")
    timeout: int = Field(default=30, ge=1, le=300)  # 1-300 seconds
    max_retries: int = Field(default=3, ge=0, le=10)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def demo_field_constraints():
    # Valid
    conn = ConnectionConfig(name="db_prod")
    print(f"Connection: {conn.name}, timeout: {conn.timeout}")
    
    # Invalid: timeout out of range
    try:
        bad_conn = ConnectionConfig(name="db_dev", timeout=500)
    except Exception as e:
        print(f"Validation failed: timeout must be <= 300")


# ==============================================================================
# 🔍 ODIBI ANALYSIS: Custom Validators
# ==============================================================================

class NodeConfig(BaseModel):
    """Custom validators: business logic validation."""
    
    name: str
    depends_on: List[str] = Field(default_factory=list)
    timeout: Optional[int] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is valid Python identifier."""
        v = v.strip()
        if not v:
            raise ValueError("Node name cannot be empty")
        if not v.replace("_", "").isalnum():
            raise ValueError(f"Node name '{v}' must be alphanumeric with underscores")
        return v.lower()
    
    @field_validator("depends_on")
    @classmethod
    def validate_dependencies(cls, v: List[str]) -> List[str]:
        """Ensure no duplicate dependencies."""
        if len(v) != len(set(v)):
            raise ValueError("Duplicate dependencies not allowed")
        return v


def demo_validators():
    # Valid node
    node = NodeConfig(name="  Extract_Data  ", depends_on=["source1", "source2"])
    print(f"Node: {node.name}, depends on: {node.depends_on}")
    
    # Invalid: bad name
    try:
        bad_node = NodeConfig(name="extract-data")  # Hyphens not allowed
    except Exception as e:
        print("Validation failed: name must be alphanumeric")
    
    # Invalid: duplicate dependencies
    try:
        bad_node2 = NodeConfig(name="transform", depends_on=["src", "src"])
    except Exception as e:
        print("Validation failed: duplicate dependencies")


# ==============================================================================
# 🔍 ODIBI ANALYSIS: Model Validators (Cross-Field)
# ==============================================================================

class WriteMode(str, Enum):
    """Enum: restricted set of values."""
    OVERWRITE = "overwrite"
    APPEND = "append"


class WriteConfig(BaseModel):
    """Model validators: validate across multiple fields."""
    
    connection: str
    path: Optional[str] = None
    table: Optional[str] = None
    mode: WriteMode = WriteMode.OVERWRITE
    
    @model_validator(mode="after")
    def check_path_or_table(self):
        """Ensure either path or table is provided (not both, not neither)."""
        if not self.path and not self.table:
            raise ValueError("Either 'path' or 'table' must be provided")
        if self.path and self.table:
            raise ValueError("Cannot specify both 'path' and 'table'")
        return self


def demo_model_validator():
    # Valid: path provided
    write1 = WriteConfig(connection="local", path="/data/output.csv")
    print(f"Writing to path: {write1.path}")
    
    # Valid: table provided
    write2 = WriteConfig(connection="delta", table="bronze.users")
    print(f"Writing to table: {write2.table}")
    
    # Invalid: neither provided
    try:
        bad_write = WriteConfig(connection="local")
    except Exception as e:
        print("Validation failed: must provide path or table")
    
    # Invalid: both provided
    try:
        bad_write2 = WriteConfig(connection="local", path="/data/out.csv", table="users")
    except Exception as e:
        print("Validation failed: cannot provide both")


# ==============================================================================
# 🔍 ODIBI ANALYSIS: Nested Models
# ==============================================================================

class ReadConfig(BaseModel):
    """Nested model: configs within configs."""
    connection: str
    format: str
    path: str
    options: Dict[str, Any] = Field(default_factory=dict)


class PipelineNode(BaseModel):
    """Odibi pattern: nested validated configs."""
    name: str
    read: Optional[ReadConfig] = None
    write: Optional[WriteConfig] = None
    
    @model_validator(mode="after")
    def check_has_operation(self):
        """Node must have at least one operation."""
        if not self.read and not self.write:
            raise ValueError(f"Node '{self.name}' must have at least one operation")
        return self


def demo_nested_models():
    # Valid: read + write node
    node = PipelineNode(
        name="etl_users",
        read=ReadConfig(
            connection="source_db",
            format="csv",
            path="/data/users.csv"
        ),
        write=WriteConfig(
            connection="target_db",
            table="bronze.users"
        )
    )
    print(f"Node {node.name}: read from {node.read.path}, write to {node.write.table}")
    
    # Invalid: no operations
    try:
        bad_node = PipelineNode(name="empty_node")
    except Exception as e:
        print("Validation failed: must have operation")


# ==============================================================================
# 🔍 ODIBI ANALYSIS: Union Types (Discriminated Unions)
# ==============================================================================

class LocalConnection(BaseModel):
    type: str = "local"
    base_path: str


class AzureConnection(BaseModel):
    type: str = "azure"
    account: str
    container: str


ConnectionType = Union[LocalConnection, AzureConnection]


class ProjectConfig(BaseModel):
    """Union types: flexible config structures."""
    name: str
    connections: Dict[str, Union[LocalConnection, AzureConnection]]


def demo_union_types():
    config = ProjectConfig(
        name="my_project",
        connections={
            "local_dev": LocalConnection(base_path="./data"),
            "prod_storage": AzureConnection(account="prodacct", container="raw")
        }
    )
    
    for name, conn in config.connections.items():
        print(f"{name}: {conn.type} connection")


# ==============================================================================
# 🏗️ BUILD IT: Complete Example
# ==============================================================================

class TransformStep(BaseModel):
    """Single transformation step."""
    sql: Optional[str] = None
    function: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode="after")
    def check_exactly_one(self):
        """Exactly one of sql or function must be provided."""
        if not self.sql and not self.function:
            raise ValueError("Must provide either 'sql' or 'function'")
        if self.sql and self.function:
            raise ValueError("Cannot provide both 'sql' and 'function'")
        return self


class TransformConfig(BaseModel):
    """Transformation configuration."""
    steps: List[TransformStep]
    
    @field_validator("steps")
    @classmethod
    def validate_non_empty(cls, v: List[TransformStep]) -> List[TransformStep]:
        if not v:
            raise ValueError("Transform must have at least one step")
        return v


class CompleteNodeConfig(BaseModel):
    """Complete node config: Odibi pattern."""
    name: str
    description: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)
    
    read: Optional[ReadConfig] = None
    transform: Optional[TransformConfig] = None
    write: Optional[WriteConfig] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip().lower()
        if not v.replace("_", "").isalnum():
            raise ValueError("Name must be alphanumeric with underscores")
        return v
    
    @model_validator(mode="after")
    def check_has_operation(self):
        """Node must have at least one operation."""
        if not any([self.read, self.transform, self.write]):
            raise ValueError(f"Node '{self.name}' must have at least one operation")
        return self


def demo_complete_example():
    """Complete Odibi-style ETL node."""
    
    node = CompleteNodeConfig(
        name="bronze_to_silver_users",
        description="Clean and deduplicate user data",
        depends_on=["extract_users"],
        read=ReadConfig(
            connection="bronze",
            format="parquet",
            path="/bronze/users"
        ),
        transform=TransformConfig(
            steps=[
                TransformStep(sql="SELECT * FROM input WHERE active = true"),
                TransformStep(function="deduplicate", params={"key": "user_id"}),
                TransformStep(sql="SELECT user_id, name, email, created_at FROM input")
            ]
        ),
        write=WriteConfig(
            connection="silver",
            table="silver.users",
            mode=WriteMode.OVERWRITE
        )
    )
    
    print(f"\nNode: {node.name}")
    print(f"Description: {node.description}")
    print(f"Dependencies: {node.depends_on}")
    print(f"Read from: {node.read.path}")
    print(f"Transform steps: {len(node.transform.steps)}")
    print(f"Write to: {node.write.table} ({node.write.mode.value})")


# ==============================================================================
# ✅ TEST IT
# ==============================================================================

def test_fail_fast_validation():
    """Demonstrate fail-fast: errors at creation, not usage."""
    
    print("\n=== Fail-Fast Validation ===")
    
    # Bad config caught immediately
    try:
        bad_node = CompleteNodeConfig(name="")
    except Exception as e:
        print(f"✓ Empty name caught at creation: {e}")
    
    # Missing operation caught immediately
    try:
        bad_node = CompleteNodeConfig(name="no_ops")
    except Exception as e:
        print(f"✓ Missing operation caught at creation")
    
    # Invalid nested config caught immediately
    try:
        bad_node = CompleteNodeConfig(
            name="bad_write",
            write=WriteConfig(connection="local")  # Missing path/table
        )
    except Exception as e:
        print(f"✓ Invalid nested config caught at creation")
    
    print("\nContrast with dict: errors only at access time")
    bad_dict = {"name": "", "write": {}}  # No validation
    print(f"Bad dict created: {bad_dict}")
    print("Error happens later when you try to use it")


# ==============================================================================
# 🎯 MAIN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TYPE SYSTEM LESSON: From Type Hints to Pydantic")
    print("=" * 70)
    
    print("\n--- Type Hints ---")
    result = calculate_discount(100.0, 0.2)
    print(f"Discount: ${result}")
    
    print("\n--- Dataclasses ---")
    demo_dataclass()
    
    print("\n--- Pydantic Basics ---")
    demo_pydantic_basic()
    
    print("\n--- Field Constraints ---")
    demo_field_constraints()
    
    print("\n--- Custom Validators ---")
    demo_validators()
    
    print("\n--- Model Validators ---")
    demo_model_validator()
    
    print("\n--- Nested Models ---")
    demo_nested_models()
    
    print("\n--- Union Types ---")
    demo_union_types()
    
    print("\n--- Complete Example ---")
    demo_complete_example()
    
    print("\n--- Fail-Fast Testing ---")
    test_fail_fast_validation()
    
    print("\n" + "=" * 70)
    print("Lesson complete! Next: exercises.py")
    print("=" * 70)
