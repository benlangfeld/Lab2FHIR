# DateTime Validation Fix

## Problem

Test `test_us1_happy_path` was failing with a 500 Internal Server Error when trying to generate a FHIR bundle. The error occurred during Pydantic model validation when reconstructing `ParsedLabData` from JSON stored in the database.

## Root Cause

The datetime validator in `intermediate_schema.py` had a subtle bug when handling naive (timezone-unaware) datetimes:

```python
@field_validator("collection_datetime")
@classmethod
def validate_collection_not_future(cls, v: datetime) -> datetime:
    """Validate that collection datetime is not in the future."""
    if v > datetime.now(v.tzinfo):  # BUG HERE
        raise ValueError("collection_datetime cannot be in the future")
    return v
```

### The Bug Explained

When `v` is a naive datetime (no timezone info), `v.tzinfo` is `None`. The code then calls `datetime.now(None)`, which **does NOT create a naive UTC datetime**. Instead, it creates a naive datetime in the **system's local timezone**.

This causes incorrect comparisons:
- `v` = naive UTC time from database (e.g., 08:00 UTC)
- `datetime.now(None)` = naive local time (e.g., 02:00 CST, which is 08:00 UTC)
- Comparison: `08:00 > 02:00` → True (incorrectly flags as "future")

## The Data Flow

Our architecture uses naive UTC datetimes throughout. Here's the complete flow:

### 1. Creation (Parser Service)
```python
# Parser creates naive UTC datetime
collection_dt = datetime.now()  
# Result: datetime(2024, 1, 15, 8, 0, 0) - naive, no tzinfo
```

### 2. Storage (Pipeline Service)
```python
# Serialize for JSON storage
payload_json = parsed_data.model_dump(mode="json")
# Result: {"collection_datetime": "2024-01-15T08:00:00"}
```

### 3. Database (PostgreSQL JSONB)
```json
{
  "collection_datetime": "2024-01-15T08:00:00",
  "measurements": [...]
}
```

### 4. Retrieval (Bundle Service)
```python
# Reconstruct Pydantic model from JSON
parsed_data = ParsedLabData(**parsed_version.payload_json)
# Pydantic parses "2024-01-15T08:00:00" → datetime(2024, 1, 15, 8, 0, 0)
# Result: naive datetime with no timezone info
```

### 5. Validation (THIS IS WHERE THE BUG WAS)
```python
# Validator runs during model reconstruction
v = datetime(2024, 1, 15, 8, 0, 0)  # naive UTC from JSON
v.tzinfo  # None

# OLD CODE (WRONG):
datetime.now(v.tzinfo)  # = datetime.now(None)
# Returns: datetime(2024, 1, 15, 2, 0, 0) if system is in CST (UTC-6)
# This is LOCAL TIME, not UTC!

# Comparison: 08:00 > 02:00 → True (WRONG - thinks it's in the future!)
```

## Solution

Update the validator to explicitly handle naive datetimes:

```python
@field_validator("collection_datetime")
@classmethod
def validate_collection_not_future(cls, v: datetime) -> datetime:
    """Validate that collection datetime is not in the future."""
    # For naive datetimes, compare with naive UTC now
    # For timezone-aware, compare with aware now in same timezone
    now = datetime.now() if v.tzinfo is None else datetime.now(v.tzinfo)
    if v > now:
        raise ValueError("collection_datetime cannot be in the future")
    return v
```

### Why This Works

**For naive datetimes** (our case):
- `v.tzinfo` is `None`
- `now = datetime.now()` creates naive UTC datetime
- Both `v` and `now` are naive UTC
- Comparison works correctly: apples-to-apples

**For timezone-aware datetimes** (future-proofing):
- `v.tzinfo` is set (e.g., `timezone.utc`)
- `now = datetime.now(v.tzinfo)` creates aware datetime in same timezone
- Both `v` and `now` are aware with same timezone
- Comparison works correctly

## Verification

The fix ensures consistent datetime handling:

```python
# Example with our naive UTC architecture
v = datetime(2024, 1, 15, 8, 0, 0)  # naive UTC from JSON
now = datetime.now()  # naive UTC "now"

# At 09:00 UTC:
if v > now:  # 08:00 > 09:00 → False ✓ (not in future, correct!)
```

## Impact

- **Fixes**: Integration test `test_us1_happy_path`
- **Affects**: All Pydantic model reconstructions from JSON
- **Scope**: Only the datetime validation logic

## Files Changed

1. `backend/src/domain/intermediate_schema.py`
   - Lines 84-93: Updated `validate_collection_not_future` validator

## Key Takeaways

1. **`datetime.now(None)` is not naive UTC** - It's naive local time
2. **For naive datetimes, use `datetime.now()`** - This gives naive UTC
3. **Timezone context matters** - Even with naive datetimes
4. **Consistent timezone handling** - All datetimes should be in same timezone context

## Related Issues

This fix complements our overall naive UTC datetime strategy:
- Created naive: `datetime.now()` (no timezone)
- Stored as JSON: ISO 8601 strings
- Validated as naive: Compare with naive UTC now
- Used consistently: All naive UTC throughout

## Test Results

After this fix:
- ✅ 25/25 tests passing (was 24/25)
- ✅ `test_us1_happy_path` now succeeds
- ✅ 100% test pass rate

## References

- Python datetime docs: https://docs.python.org/3/library/datetime.html
- Pydantic validation: https://docs.pydantic.dev/latest/concepts/validators/
- Related fix: DATETIME_SERIALIZATION_FIX.md (JSON serialization)
- Related fix: TIMEZONE_FIX.md (naive UTC strategy)
