# Python Coding Guidelines

This document outlines the coding standards and best practices for the Eventchimp project. All code should follow these guidelines to ensure consistency, maintainability, and readability.

## Table of Contents
1. [General Principles](#general-principles)
2. [Code Style](#code-style)
3. [Naming Conventions](#naming-conventions)
4. [Import Organization](#import-organization)
5. [Function and Class Design](#function-and-class-design)
6. [Django-Specific Guidelines](#django-specific-guidelines)
7. [Documentation](#documentation)
8. [Error Handling](#error-handling)
9. [Testing](#testing)
10. [Code Organization](#code-organization)

---

## General Principles

1. **Readability First**: Code should be easy to read and understand. Prefer clarity over cleverness.
2. **DRY (Don't Repeat Yourself)**: Avoid code duplication. Extract common logic into reusable functions or utilities.
3. **Single Responsibility**: Each function, class, or module should have one clear purpose.
4. **Explicit over Implicit**: Make code intentions clear. Avoid magic numbers and ambiguous variable names.
5. **Fail Fast**: Validate inputs early and raise clear error messages.

---

## Code Style

### PEP 8 Compliance
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black formatter default) or 100 characters
- Use blank lines to separate logical sections

### Formatting
```python
# Good
def calculate_availability(start_datetime, end_datetime):
    if end_datetime <= start_datetime:
        return []
    # ... rest of function

# Bad
def calc(start,end):
    if end<=start:return[]
```

### Quotes
- Use double quotes (`"`) for strings, unless the string contains double quotes
- Be consistent within a file

```python
# Good
message = "User created successfully"
error = 'User said "Hello"'

# Bad
message = 'User created successfully'
```

---

## Naming Conventions

### Variables and Functions
- Use `snake_case` for variables, functions, and methods
- Use descriptive names that indicate purpose
- Avoid single-letter variables except in loops or mathematical contexts

```python
# Good
def get_available_slots(event_id, start_datetime, end_datetime):
    reservation_list = []
    current_time = timezone.now()

# Bad
def getSlots(eid, sdt, edt):
    rl = []
    ct = timezone.now()
```

### Constants
- Use `UPPER_SNAKE_CASE` for module-level constants
- Define constants in a dedicated `constants.py` file when shared across modules

```python
# Good
MINUTES_MULTIPLE_OF = 5
MAX_DURATION_IN_MINUTES = 720

# Bad
minutes_multiple_of = 5
```

### Classes
- Use `PascalCase` for class names
- Use descriptive names that indicate what the class represents

```python
# Good
class EventSerializer(serializers.ModelSerializer):
    pass

class ReservationManager(models.Manager):
    pass

# Bad
class ES(serializers.ModelSerializer):
    pass
```

### Private Methods/Attributes
- Prefix with single underscore `_` for internal use (convention, not enforced)
- Use double underscore `__` only for name mangling (rarely needed)

```python
# Good
class Event(models.Model):
    def _validate_dates(self):
        pass  # Internal helper method

# Bad
class Event(models.Model):
    def __validate_dates__(self):  # Unnecessary name mangling
        pass
```

---

## Import Organization

### Import Order
1. Standard library imports
2. Third-party imports (Django, DRF, etc.)
3. Local application imports
4. Blank line between each group

```python
# Good
import json
from datetime import time

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from events.models import Event
from reservations.models import Reservation
from commons.utils import merge_datetime_intervals

# Bad
from events.models import Event
import json
from django.utils import timezone
from reservations.models import Reservation
```

### Import Style
- Use absolute imports
- Import specific functions/classes when possible
- Avoid `from module import *` (except for well-known cases like Django admin)

```python
# Good
from django.utils import timezone
from commons.utils import merge_datetime_intervals, get_start_of_day

# Acceptable for Django admin
from django.contrib import admin
from .models import Event

# Bad
from django.utils import *
from commons import utils  # Then use utils.merge_datetime_intervals
```

---

## Function and Class Design

### Function Guidelines
- Keep functions focused and small (ideally < 50 lines)
- Use type hints when it adds clarity (optional but recommended)
- Document complex logic with comments
- Return early for edge cases

```python
# Good
def get_available_slots(event_id, start_datetime, end_datetime):
    """Get available time slots for an event within a date range.
    
    Args:
        event_id: The ID of the event
        start_datetime: Start of the query range
        end_datetime: End of the query range
    
    Returns:
        List of available slot dictionaries with start_datetime and end_datetime
    """
    if end_datetime <= start_datetime:
        return []
    
    event = get_object_or_404(Event, pk=event_id)
    # ... rest of function

# Bad
def get_available_slots(event_id, start_datetime, end_datetime):
    # No docstring, no early return, does too many things
    event = get_object_or_404(Event, pk=event_id)
    if end_datetime > start_datetime:
        # ... 100 lines of code
    return []
```

### Function Parameters
- Use keyword arguments for clarity when calling functions with many parameters
- Group related parameters into objects/dictionaries when appropriate

```python
# Good
reservations = add_buffer_to_reservations(
    reservations=reservations,
    before_buffer_time_in_minutes=before_buffer,
    after_buffer_time_in_minutes=after_buffer
)

# Also acceptable for simple cases
result = max(a, b)
```

### List Comprehensions vs Loops
- Use list comprehensions for simple transformations
- Use loops for complex logic or when side effects are needed

```python
# Good - Simple transformation
squares = [x**2 for x in range(10)]

# Good - Complex logic
available_slots = []
for availability in availabilities:
    slots = split_into_slots(
        start_datetime=availability["start_datetime"],
        end_datetime=availability["end_datetime"],
        step_in_minutes=event.step_in_minutes
    )
    available_slots.extend(slots)

# Bad - Overly complex comprehension
available_slots = [
    slot for availability in availabilities
    for slot in split_into_slots(
        start_datetime=availability["start_datetime"],
        end_datetime=availability["end_datetime"],
        step_in_minutes=event.step_in_minutes
    )
]
```

---

## Django-Specific Guidelines

### Models
- Use descriptive field names
- Set appropriate `verbose_name` and `help_text` for admin
- Use `related_name` for ForeignKey relationships
- Implement `soft_delete()` methods instead of hard deletes when needed
- Use `get_owner_id()` method for permission checks

```python
# Good
class Event(models.Model):
    organiser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events"
    )
    title = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    
    def soft_delete(self):
        self.is_active = False
        self.save(force_update=True, update_fields=["is_active", "updated_at"])
    
    def get_owner_id(self):
        return self.organiser_id

# Bad
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # No related_name
    t = models.CharField(max_length=120)  # Abbreviated name
```

### QuerySets
- Use QuerySet methods efficiently
- Chain filters when appropriate
- Use `select_related()` and `prefetch_related()` to avoid N+1 queries
- Create custom QuerySet managers for reusable queries

```python
# Good
@classmethod
def get_active_reservations(cls, event_id, start_datetime, end_datetime):
    return cls.objects.exclude(
        status=ReservationStatus.CANCELLED
    ).filter(
        event_id=event_id,
        start_datetime__lte=end_datetime,
        end_datetime__gte=start_datetime,
        is_active=True,
    )

# Bad
def get_active_reservations(cls, event_id, start_datetime, end_datetime):
    all_reservations = cls.objects.all()
    result = []
    for r in all_reservations:
        if r.event_id == event_id and r.is_active:
            # ... manual filtering
    return result
```

### Views
- Use ViewSets for CRUD operations
- Keep view logic minimal; move business logic to models or helper functions
- Use appropriate permission classes
- Return appropriate HTTP status codes

```python
# Good
class EventViewset(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsOwner]
    
    def get_queryset(self):
        return Event.objects.filter(
            organiser=self.request.user,
            is_active=True
        )
    
    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        event.soft_delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)

# Bad
class EventViewset(viewsets.ModelViewSet):
    # No permission classes
    # Complex business logic in view
    def create(self, request):
        # 50 lines of validation and business logic
        pass
```

### Serializers
- Use `ModelSerializer` when possible
- Validate data in `validate()` method
- Use custom fields from `commons.serializerfields` when needed
- Set appropriate `read_only_fields`

```python
# Good
class EventSerializer(serializers.ModelSerializer):
    start_datetime = AutoTzDateTimeField(validators=[MinutesMultipleOfValidator()])
    
    class Meta:
        model = Event
        fields = ('id', 'title', 'start_datetime', ...)
        read_only_fields = ('id', 'organiser', 'slug', ...)
    
    def validate(self, data):
        start_datetime = data.get('start_datetime')
        end_datetime = data.get('end_datetime')
        if start_datetime >= end_datetime:
            raise serializers.ValidationError(
                "End datetime must be after start datetime."
            )
        return data
```

### Settings
- Use environment variables for sensitive data
- Access settings via `django.conf.settings`
- Use `settings.DEBUG` for debug-only code

```python
# Good
from django.conf import settings

if settings.DEBUG:
    debug_data = {...}
    print(json.dumps(debug_data, default=datetime_serializer, indent=2))

# Bad
if DEBUG:  # Not imported
    pass
```

---

## Documentation

### Docstrings
- Use docstrings for all public functions, classes, and methods
- Follow Google or NumPy style (be consistent within project)
- Document parameters, return values, and exceptions

```python
# Good
def get_negation_interval(intervals, min_datetime, max_datetime):
    """Calculate negation intervals from a list of intervals.
    
    Given a list of intervals and a range [min_datetime, max_datetime],
    returns the intervals that represent the gaps (negation) between
    the provided intervals.
    
    Args:
        intervals: List of dicts with 'start_datetime' and 'end_datetime'
        min_datetime: Minimum datetime for the range
        max_datetime: Maximum datetime for the range
    
    Returns:
        List of dicts representing negation intervals, each with
        'start_datetime' and 'end_datetime' keys.
    """
    pass

# Bad
def get_negation_interval(intervals, min_datetime, max_datetime):
    # Calculates negation
    pass
```

### Comments
- Use comments to explain "why", not "what"
- Keep comments up-to-date with code changes
- Remove commented-out code before committing

```python
# Good
# Apply buffer time to prevent back-to-back reservations
if before_buffer > 0 or after_buffer > 0:
    reservations = add_buffer_to_reservations(...)

# Bad
# Loop through reservations
for reservation in reservations:
    # Add buffer
    reservation["start_datetime"] += ...
```

---

## Error Handling

### Exception Handling
- Use specific exception types
- Provide meaningful error messages
- Don't catch exceptions unless you can handle them meaningfully
- Use `get_object_or_404()` for Django model lookups

```python
# Good
def get_available_slots(event_id, start_datetime, end_datetime):
    if end_datetime <= start_datetime:
        return []
    event = get_object_or_404(Event, pk=event_id)
    # ...

def datetime_serializer(obj):
    if isinstance(obj, timezone.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

# Bad
def get_available_slots(event_id, start_datetime, end_datetime):
    try:
        event = Event.objects.get(pk=event_id)
    except:
        return None  # Swallows all exceptions
```

### Validation
- Validate inputs early in functions
- Use Django validators for model/serializer validation
- Return clear error messages

```python
# Good
def validate(self, data):
    start_datetime = data.get('start_datetime')
    end_datetime = data.get('end_datetime')
    
    if start_datetime >= end_datetime:
        raise serializers.ValidationError(
            "End datetime must be after start datetime."
        )
    return data
```

---

## Testing

### Test Structure
- Write tests for all business logic
- Use descriptive test method names: `test_<functionality>_<scenario>`
- Follow Arrange-Act-Assert pattern
- Use Django's `TestCase` for database tests

```python
# Good
class AvailabilityHelperTestCase(TestCase):
    def test_get_available_slots_returns_empty_when_end_before_start(self):
        # Arrange
        start = timezone.now()
        end = start - timezone.timedelta(hours=1)
        
        # Act
        result = get_available_slots(event_id=1, start_datetime=start, end_datetime=end)
        
        # Assert
        self.assertEqual(result, [])
    
    def test_get_available_slots_filters_by_notice_period(self):
        # Test implementation
        pass

# Bad
class TestAvailability(TestCase):
    def test1(self):
        # Unclear what is being tested
        pass
```

### Test Data
- Use factories or fixtures for test data
- Keep tests independent (no shared state)
- Use meaningful test data that reflects real scenarios

---

## Code Organization

### File Structure
- Keep files focused on a single purpose
- Group related functionality in modules
- Use helper modules (e.g., `availability_helper.py`) for complex business logic

### Module Organization
```
app_name/
    __init__.py
    models.py          # Django models
    views.py           # ViewSets and views
    serializers.py     # DRF serializers
    urls.py            # URL routing
    admin.py           # Django admin
    tests.py           # Unit tests
    utils.py           # Utility functions (if needed)
    helpers.py         # Business logic helpers (if needed)
```

### Function Organization Within Files
1. Imports
2. Constants
3. Helper/utility functions
4. Main functions/classes
5. Tests (if in same file, though prefer separate test files)

### Common Utilities
- Place shared utilities in `commons/` directory
- Use descriptive module names: `utils.py`, `validators.py`, `constants.py`
- Keep utilities pure (no side effects) when possible

```python
# Good - Pure function in commons/utils.py
def merge_datetime_intervals(intervals):
    """Merge overlapping datetime intervals."""
    if len(intervals) <= 1:
        return intervals
    # ... implementation
    return merged

# Bad - Function with side effects in utils
def merge_datetime_intervals(intervals):
    global some_global_variable  # Side effect
    # ...
```

---

## Additional Best Practices

### Performance
- Avoid N+1 queries (use `select_related`, `prefetch_related`)
- Use database indexes for frequently queried fields
- Consider caching for expensive operations
- Use QuerySet methods efficiently (avoid loading all objects into memory)

### Security
- Never commit secrets or API keys
- Use Django's built-in security features
- Validate and sanitize user inputs
- Use parameterized queries (Django ORM handles this)

### Code Review Checklist
- [ ] Code follows PEP 8 style guide
- [ ] Functions have docstrings
- [ ] No hardcoded values (use constants)
- [ ] Error handling is appropriate
- [ ] Tests are included for new functionality
- [ ] No commented-out code
- [ ] Imports are organized correctly
- [ ] No unnecessary complexity

---

## Tools and Linting

### Recommended Tools
- **Black**: Code formatter (optional but recommended)
- **flake8**: Linter for PEP 8 compliance
- **pylint**: Additional linting (optional)
- **mypy**: Type checking (optional)

### Pre-commit Hooks
Consider setting up pre-commit hooks to automatically check code style before commits.

---

## Examples

### Complete Example: Well-Structured Function

```python
from django.utils import timezone
from django.shortcuts import get_object_or_404

from events.models import Event
from reservations.models import Reservation


def get_available_slots(event_id, start_datetime, end_datetime):
    """Get available time slots for an event within a date range.
    
    This function calculates available booking slots by:
    1. Getting the event and its schedule
    2. Finding existing reservations
    3. Calculating available time windows
    4. Splitting windows into bookable slots
    
    Args:
        event_id: The ID of the event
        start_datetime: Start of the query range
        end_datetime: End of the query range
    
    Returns:
        List of available slot dictionaries, each containing:
        - start_datetime: Start time of the slot
        - end_datetime: End time of the slot
    
    Raises:
        Http404: If event with given ID does not exist
    """
    # Early return for invalid input
    if end_datetime <= start_datetime:
        return []
    
    # Get event
    event = get_object_or_404(Event, pk=event_id)
    
    # Calculate minimum slot start time based on notice period
    slots_start_datetime = timezone.now() + timezone.timedelta(
        minutes=event.notice_in_minutes
    )
    
    # Adjust query range to event boundaries
    start_datetime = max(start_datetime, event.start_datetime)
    end_datetime = min(end_datetime, event.end_datetime)
    
    # Apply rolling days limit if set
    if event.rolling_days:
        tomorrow = get_start_of_day(timezone.now() + timezone.timedelta(days=1))
        max_end = tomorrow + timezone.timedelta(days=event.rolling_days)
        end_datetime = min(end_datetime, max_end)
    
    # Get reservations and apply buffers
    reservations = Reservation.get_active_reservations(
        event_id=event_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime
    ).values("start_datetime", "end_datetime")
    
    if event.before_buffer_time_in_minutes > 0 or event.after_buffer_time_in_minutes > 0:
        reservations = add_buffer_to_reservations(
            reservations=reservations,
            before_buffer_time_in_minutes=event.before_buffer_time_in_minutes,
            after_buffer_time_in_minutes=event.after_buffer_time_in_minutes
        )
    
    # Calculate available intervals
    reservation_neg = get_negation_interval(
        reservations,
        start_datetime,
        end_datetime
    )
    
    schedules = event.schedule.get_schedule(start_datetime, end_datetime)
    availabilities = find_common_interval(schedules, reservation_neg)
    
    # Split intervals into slots
    available_slots = []
    for availability in availabilities:
        slots = split_into_slots(
            start_datetime=availability["start_datetime"],
            end_datetime=availability["end_datetime"],
            step_in_minutes=event.step_in_minutes
        )
        available_slots.extend(slots)
    
    # Filter out slots that are too soon (notice period)
    return [
        slot for slot in available_slots
        if slot["start_datetime"] > slots_start_datetime
    ]
```

---

## Summary

- Follow PEP 8 and use consistent formatting
- Write clear, descriptive names
- Keep functions focused and small
- Document complex logic
- Handle errors appropriately
- Write tests for business logic
- Organize code logically
- Use Django best practices
- Review code before committing

Remember: **Code is read more often than it's written. Write for your future self and your teammates.**
