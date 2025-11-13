# YAML Configuration Deep Dive

## Common Confusions Explained

### 1. When to Quote Strings

YAML is smart about detecting types, but this can bite you:

```yaml
# These are all DIFFERENT types:
name: John        # string (no quotes needed)
age: 30           # integer
price: 19.99      # float
enabled: true     # boolean
nothing: null     # null/None

# When you MUST quote:
zip_code: "00123"     # Without quotes: 123 (loses leading zeros!)
version: "1.0"        # Without quotes: 1.0 (float, not string)
email: "user@example" # Contains @ (could be misinterpreted)
country: "NO"         # Famous bug: NO = False in YAML!

# Special characters require quotes:
message: "Hello: World"  # Contains colon
path: "C:\\Users\\Name"   # Backslashes
command: "echo 'test'"   # Contains quotes
```

**Rule of Thumb:**
- Simple strings (letters, numbers, spaces): No quotes needed
- Numbers that must stay strings: Quote them
- Contains special chars (`:`, `@`, `-`, `!`): Quote them

---

### 2. Indentation Rules

YAML uses **spaces only** (never tabs). Indentation shows structure:

```yaml
# ✅ CORRECT: Consistent 2-space indentation
database:
  host: localhost
  credentials:
    username: admin
    password: secret

# ✅ ALSO CORRECT: Consistent 4-space indentation
database:
    host: localhost
    credentials:
        username: admin
        password: secret

# ❌ WRONG: Mixed indentation
database:
  host: localhost
    credentials:  # Inconsistent indent
      username: admin

# ❌ WRONG: Using tabs
database:
→host: localhost  # Tab character - will error!
```

**Best Practice:** Use 2 spaces (most common in data engineering)

---

### 3. Multiline Strings: `|` vs `>`

This confuses everyone at first:

#### Literal Block `|` - Preserves newlines
```yaml
sql: |
  SELECT *
  FROM users
  WHERE age > 18
```
Becomes in Python:
```python
"SELECT *\nFROM users\nWHERE age > 18\n"
```

**Use for:** SQL queries, shell scripts, code blocks

#### Folded Block `>` - Combines into one line
```yaml
description: >
  This is a long
  description that will
  become one line.
```
Becomes:
```python
"This is a long description that will become one line.\n"
```

**Use for:** Long descriptions, paragraphs, documentation

#### Quick Reference
```yaml
# | = Literal = Keep newlines
# > = Folded = Join into one line

script: |
  #!/bin/bash
  echo "Line 1"
  echo "Line 2"

paragraph: >
  This is a very long paragraph
  that we want to write across
  multiple lines for readability
  but it will be one line in Python.
```

---

### 4. Lists: Two Syntaxes

#### Block Style (Preferred)
```yaml
fruits:
  - apple
  - banana
  - orange
```

#### Flow Style (Inline)
```yaml
fruits: [apple, banana, orange]
```

Both are identical in Python:
```python
{"fruits": ["apple", "banana", "orange"]}
```

**When to use each:**
- Block: Default choice, more readable
- Flow: Short lists, space-constrained

#### Nested Lists
```yaml
# List of lists
matrix:
  - [1, 2, 3]
  - [4, 5, 6]

# List of dicts
users:
  - name: Alice
    age: 30
  - name: Bob
    age: 25
```

---

### 5. Anchors & Aliases (DRY Config)

**Problem:** Repeating the same configuration

```yaml
# ❌ Without anchors: Duplication
pipeline_1:
  retry:
    max_attempts: 3
    backoff: exponential

pipeline_2:
  retry:
    max_attempts: 3
    backoff: exponential
```

**Solution:** Anchors (`&name`) and Aliases (`*name`)

```yaml
# ✅ With anchors: Define once, reuse
default_retry: &retry_config
  max_attempts: 3
  backoff: exponential

pipeline_1:
  retry: *retry_config

pipeline_2:
  retry: *retry_config
```

**How it works:**
1. `&retry_config` - Creates an anchor (like a variable)
2. `*retry_config` - References the anchor (like using the variable)

**Advanced: Merging with overrides**
```yaml
defaults: &defaults
  timeout: 30
  retries: 3

production:
  <<: *defaults      # Merge all defaults
  timeout: 60        # Override timeout only
  
# Result:
# production:
#   timeout: 60
#   retries: 3
```

---

### 6. Environment Variable Substitution

**Problem:** YAML doesn't support env vars natively!

```yaml
# ❌ This does NOT work by default:
database:
  host: ${DB_HOST}
  password: ${DB_PASSWORD}
```

**Solutions:**

#### Option 1: Python code
```python
import os
import yaml

with open('config.yaml') as f:
    content = f.read()
    # Replace ${VAR} with environment values
    for key, value in os.environ.items():
        content = content.replace(f'${{{key}}}', value)
    config = yaml.safe_load(content)
```

#### Option 2: Use envyaml library
```bash
pip install envyaml
```

```python
from envyaml import EnvYAML

config = EnvYAML('config.yaml')
# Automatically replaces ${VAR} with os.environ['VAR']
```

#### Option 3: Odibi pattern (Pydantic)
```yaml
# config.yaml
database:
  host: placeholder
  password: placeholder
```

```python
# Load and override from env
config = yaml.safe_load(open('config.yaml'))
config['database']['host'] = os.getenv('DB_HOST', 'localhost')
config['database']['password'] = os.getenv('DB_PASSWORD')
```

---

### 7. Type Coercion Gotchas

YAML automatically converts strings to other types. This can surprise you:

```yaml
# What you wrote → What Python sees

country: NO        # False (boolean!)
country: "NO"      # "NO" (string) ✅

version: 1.0       # 1.0 (float)
version: "1.0"     # "1.0" (string) ✅

zip: 00501         # 501 (integer, loses leading zero!)
zip: "00501"       # "00501" (string) ✅

yes_value: yes     # True (boolean!)
yes_value: "yes"   # "yes" (string) ✅

# Booleans (case-insensitive):
true, True, TRUE, yes, Yes, YES, on, On, ON → True
false, False, FALSE, no, No, NO, off, Off, OFF → False

# Null values:
null, Null, NULL, ~, (empty) → None
```

**Best Practice:** When in doubt, use quotes for strings!

---

### 8. Comments

```yaml
# This is a full-line comment

key: value  # This is an inline comment

# Multi-line "comments" using literal blocks:
_comment: |
  This is technically a key, but using '_' prefix
  signals it's documentation/comments
  
  Useful for explaining complex configs

actual_key: actual_value
```

---

### 9. File Organization Patterns

### Small Project
```
config.yaml         # All config in one file
```

### Medium Project
```
config/
  base.yaml         # Common settings
  dev.yaml          # Development overrides
  prod.yaml         # Production overrides
```

### Large Project (Odibi style)
```
configs/
  connections/
    databases.yaml
    storage.yaml
  pipelines/
    bronze.yaml
    silver.yaml
    gold.yaml
  settings.yaml     # App settings
```

---

### 10. Common Errors & Fixes

#### Error: `could not determine a constructor for the tag`
```yaml
# ❌ YAML tries to evaluate as Python object
value: !!python/object:...

# ✅ Use safe_load to prevent this
```

#### Error: `mapping values are not allowed here`
```yaml
# ❌ Missing space after colon
key:value

# ✅ Space required
key: value
```

#### Error: `found character that cannot start any token`
```yaml
# ❌ Special character not quoted
message: @everyone hello

# ✅ Quote strings with special chars
message: "@everyone hello"
```

#### Error: `expected <block end>, but found`
```yaml
# ❌ Indentation mismatch
database:
  host: localhost
 port: 5432  # Wrong indent

# ✅ Consistent indentation
database:
  host: localhost
  port: 5432
```

---

## Real-World Examples

### Database Configuration
```yaml
databases:
  # Development
  dev: &dev_db
    host: localhost
    port: 5432
    name: dev_db
    pool_size: 5
    ssl: false

  # Production (inherits from dev, overrides specific values)
  prod:
    <<: *dev_db
    host: prod-db.example.com
    name: prod_db
    pool_size: 20
    ssl: true
    connection_timeout: 30
```

### Pipeline Configuration
```yaml
pipeline:
  name: daily_sales_etl
  
  source:
    type: csv
    path: /data/raw/sales.csv
    options:
      delimiter: ","
      header: true
  
  transformations:
    - type: filter
      condition: "amount > 0"
    
    - type: add_column
      name: processed_at
      value: current_timestamp
  
  destination:
    type: database
    table: cleaned_sales
    mode: overwrite
```

### Multi-Environment Setup
```yaml
# base.yaml
defaults: &defaults
  retry:
    max_attempts: 3
    backoff: exponential
  logging:
    level: INFO
    format: json

# dev.yaml
environment: development
settings:
  <<: *defaults
  logging:
    level: DEBUG
  debug: true

# prod.yaml  
environment: production
settings:
  <<: *defaults
  retry:
    max_attempts: 5
  alerts:
    enabled: true
    slack_webhook: ${SLACK_WEBHOOK}
```

---

## Best Practices Summary

1. **Always** use `yaml.safe_load()`, never `yaml.load()`
2. **Quote** strings with numbers, special chars, or country codes
3. **Use 2-space indentation** (spaces only, no tabs)
4. **Use anchors** for repeated config (`&` and `*`)
5. **Comment** complex sections
6. **Validate** with Pydantic after loading
7. **Separate** environment-specific configs
8. **Keep secrets** out of YAML (use env vars or secret managers)
9. **Version control** your configs (except secrets)
10. **Test** your configs (parse them in tests)

---

## Debugging YAML

### Online Validators
- https://www.yamllint.com/
- https://yaml-online-parser.appspot.com/

### Python Debugging
```python
import yaml

try:
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"YAML Error: {e}")
    # Shows line number and problem
```

### Pretty Print Loaded Config
```python
import yaml
from pprint import pprint

with open('config.yaml') as f:
    config = yaml.safe_load(f)
    pprint(config, sort_dicts=False)  # Preserves order
```

---

## When NOT to Use YAML

YAML is great for config, but use alternatives when:

1. **Configuration is code** → Use Python
   ```python
   # config.py
   SETTINGS = {
       "database": create_database_config(),
       "pipelines": [build_pipeline(x) for x in sources]
   }
   ```

2. **Strict typing required** → Use TOML or Python with Pydantic
   ```toml
   # config.toml
   [database]
   host = "localhost"
   port = 5432  # TOML has strict types
   ```

3. **Very large configs** → Use Python modules or JSON
4. **Need comments in output** → YAML comments lost on round-trip
5. **Team unfamiliar with YAML** → JSON (more familiar) or Python

---

## YAML vs JSON vs TOML

| Feature | YAML | JSON | TOML |
|---------|------|------|------|
| **Readability** | ★★★★★ | ★★★ | ★★★★ |
| **Comments** | ✅ | ❌ | ✅ |
| **Type safety** | ⚠️ (coercion) | ✅ | ✅ |
| **Complexity** | High | Low | Medium |
| **Multi-line strings** | Easy | Hard | Medium |
| **Tool support** | ★★★★★ | ★★★★★ | ★★★★ |
| **Best for** | Data pipelines, K8s | APIs, web | App config |

**Choose YAML when:** Config is for humans, needs comments, lots of nested structure
**Choose JSON when:** Config is for machines, APIs, strict types
**Choose TOML when:** App settings, strict types, less nesting
