# Example YAML Configurations

Sample YAML files for learning and testing.

## Files

- **basic.yaml** - Basic YAML syntax and data types
- **mini_pipeline.yaml** - Simplified pipeline config for Pydantic exercises
- **anchors_demo.yaml** - Using anchors & aliases to avoid repetition
- **env_vars.yaml** - Environment variable substitution patterns
- **generated.yaml** - Auto-generated from lesson.ipynb

## Usage

```python
import yaml

# Load any example
with open('example_configs/basic.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

## Creating Your Own

Use these as templates for your own configs. Remember:

1. Always use `safe_load()` for security
2. Quote strings that might be misinterpreted (NO, YES, version numbers)
3. Use anchors to avoid duplication
4. Externalize secrets to environment variables
5. Validate with Pydantic schemas
