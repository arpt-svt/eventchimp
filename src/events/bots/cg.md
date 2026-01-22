# Python Coding Guidelines and Best Practices

## Code Style

### Follow PEP 8
- Use 4 spaces for indentation (never tabs)
- Limit lines to 79 characters (or 99 for modern projects)
- Use blank lines to separate functions, classes, and logical sections
- Use lowercase with underscores for function and variable names (`snake_case`)
- Use CamelCase for class names (`PascalCase`)
- Use UPPERCASE for constants (`SCREAMING_SNAKE_CASE`)

### Imports
- Place imports at the top of the file
- Group imports in order: standard library, third-party, local application
- Use absolute imports over relative imports when possible
- Avoid wildcard imports (`from module import *`)

```python
# Good
import os
import sys

import requests
from django.db import models

from myapp.utils import helper
```

## Naming Conventions

### Variables and Functions
```python
# Good
user_name = "Alice"
total_count = 42

def calculate_total_price(items):
    pass

# Bad
userName = "Alice"  # camelCase
TotalCount = 42     # PascalCase for variable
def CalculateTotalPrice(items):  # PascalCase for function
    pass
```

### Classes
```python
# Good
class UserAccount:
    pass

class HTTPRequestHandler:
    pass

# Bad
class user_account:  # snake_case for class
    pass
```

### Constants
```python
# Good
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"
```

## Documentation

### Docstrings
Use docstrings for all public modules, functions, classes, and methods.

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculate the discounted price.

    Args:
        price: The original price of the item.
        discount_percent: The discount percentage (0-100).

    Returns:
        The price after applying the discount.

    Raises:
        ValueError: If discount_percent is not between 0 and 100.
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
```

### Comments
- Write comments that explain "why", not "what"
- Keep comments up to date with code changes
- Avoid obvious comments

```python
# Bad
x = x + 1  # Increment x

# Good
x = x + 1  # Compensate for border width
```

## Type Hints

Use type hints for function signatures and complex variables.

```python
from typing import List, Dict, Optional, Union

def get_user_by_id(user_id: int) -> Optional[User]:
    pass

def process_items(items: List[str]) -> Dict[str, int]:
    pass

def fetch_data(url: str, timeout: Optional[int] = None) -> Union[dict, None]:
    pass
```

## Error Handling

### Be Specific with Exceptions
```python
# Bad
try:
    result = do_something()
except Exception:
    pass

# Good
try:
    result = do_something()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except ConnectionError as e:
    logger.warning(f"Connection failed: {e}")
    return None
```

### Use Context Managers
```python
# Good
with open("file.txt", "r") as f:
    content = f.read()

# Bad
f = open("file.txt", "r")
content = f.read()
f.close()
```

## Functions

### Keep Functions Small and Focused
- Each function should do one thing well
- Aim for functions under 20-30 lines
- If a function needs many comments, consider splitting it

### Use Default Arguments Carefully
```python
# Bad - mutable default argument
def append_to_list(item, lst=[]):
    lst.append(item)
    return lst

# Good
def append_to_list(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### Return Early
```python
# Good
def get_user_status(user):
    if user is None:
        return "unknown"
    if not user.is_active:
        return "inactive"
    if user.is_admin:
        return "admin"
    return "regular"

# Bad - deeply nested
def get_user_status(user):
    if user is not None:
        if user.is_active:
            if user.is_admin:
                return "admin"
            else:
                return "regular"
        else:
            return "inactive"
    else:
        return "unknown"
```

## Classes

### Use Properties Instead of Getters/Setters
```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self) -> float:
        return 3.14159 * self._radius ** 2
```

### Use `__slots__` for Memory Optimization
```python
class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

## Data Structures

### Use List Comprehensions
```python
# Good
squares = [x ** 2 for x in range(10)]
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]

# Less readable for complex operations - use regular loops
```

### Use Dictionary Comprehensions
```python
# Good
word_lengths = {word: len(word) for word in words}
```

### Use `enumerate()` Instead of Range
```python
# Good
for index, item in enumerate(items):
    print(f"{index}: {item}")

# Bad
for i in range(len(items)):
    print(f"{i}: {items[i]}")
```

### Use `zip()` for Parallel Iteration
```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

## Performance Tips

### Use Generators for Large Datasets
```python
# Good - memory efficient
def read_large_file(file_path):
    with open(file_path, "r") as f:
        for line in f:
            yield line.strip()

# Bad - loads everything into memory
def read_large_file(file_path):
    with open(file_path, "r") as f:
        return f.readlines()
```

### Use `set` for Membership Testing
```python
# Good - O(1) lookup
valid_ids = {1, 2, 3, 4, 5}
if user_id in valid_ids:
    pass

# Bad - O(n) lookup
valid_ids = [1, 2, 3, 4, 5]
if user_id in valid_ids:
    pass
```

### Use `join()` for String Concatenation
```python
# Good
result = "".join(strings)
result = ", ".join(items)

# Bad - creates many intermediate strings
result = ""
for s in strings:
    result += s
```

## Testing

### Write Unit Tests
```python
import pytest

def test_calculate_discount():
    assert calculate_discount(100, 20) == 80
    assert calculate_discount(50, 0) == 50

def test_calculate_discount_invalid():
    with pytest.raises(ValueError):
        calculate_discount(100, 150)
```

### Use Fixtures for Test Setup
```python
@pytest.fixture
def sample_user():
    return User(name="Test", email="test@example.com")

def test_user_display_name(sample_user):
    assert sample_user.display_name == "Test"
```

## Logging

### Use the `logging` Module
```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Starting data processing")
    try:
        result = transform(data)
        logger.debug(f"Transformed data: {result}")
        return result
    except Exception as e:
        logger.exception(f"Error processing data: {e}")
        raise
```

## Security Best Practices

- Never hardcode secrets or credentials
- Use environment variables or secret management tools
- Sanitize user inputs
- Use parameterized queries for database operations
- Keep dependencies updated

```python
import os

# Good
API_KEY = os.environ.get("API_KEY")

# Bad
API_KEY = "sk-1234567890abcdef"
```

## Project Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── requirements.txt
├── setup.py
└── README.md
```

## Tools and Linters

- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Style guide enforcement
- **mypy**: Static type checker
- **pylint**: Code analysis
- **pytest**: Testing framework

### Example pyproject.toml
```toml
[tool.black]
line-length = 99
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 99

[tool.mypy]
python_version = "3.11"
strict = true
```
