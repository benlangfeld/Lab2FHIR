# DateTime JSON Serialization Fix

## Summary

Fixed the final test failures caused by datetime objects not being JSON-serializable when storing in PostgreSQL's JSONB column. Changed from `model_dump()` to `model_dump(mode="json")` to properly serialize datetime objects to ISO 8601 strings.

## The Problem

### Error Message
```
sqlalchemy.exc.DBAPIError: (builtins.TypeError) Object of type datetime is not JSON serializable
[SQL: INSERT INTO parsed_lab_data_versions (..., payload_json, ...) VALUES (..., $6::JSONB, ...)]
```

### Root Cause

The `ParsedLabData` Pydantic model contains `datetime` fields:

```python
class LabMeasurement(BaseModel):
    collection_datetime: datetime = Field(..., description="Sample collection date/time")
    result_datetime: datetime | None = Field(None, description="Result date/time")
```

When storing this in the database's JSONB column:

1. Parser service creates `ParsedLabData` with datetime objects
2. Pipeline service calls `parsed_data.model_dump()` 
3. This returns a dict with datetime objects (Python types preserved)
4. SQLAlchemy tries to JSON-encode the dict for PostgreSQL JSONB
5. Python's `json` module can't serialize datetime objects → TypeError

### Why It Failed

PostgreSQL's JSONB type stores JSON data in binary format. JSON spec only supports:
- Strings
- Numbers
- Booleans
- Null
- Arrays
- Objects

Python `datetime` objects are NOT part of JSON spec, so they must be converted to strings.

## The Solution

### Change Made

File: `backend/src/services/report_pipeline_service.py` (line 134)

**Before**:
```python
parsed_version = ParsedLabDataVersion(
    report_id=report_id,
    version_number=version_number,
    version_type=VersionType.ORIGINAL,
    schema_version=parsed_data.schema_version,
    payload_json=parsed_data.model_dump(),  # Returns datetime objects
    validation_status=ValidationStatus.VALID,
    created_by="system",
)
```

**After**:
```python
parsed_version = ParsedLabDataVersion(
    report_id=report_id,
    version_number=version_number,
    version_type=VersionType.ORIGINAL,
    schema_version=parsed_data.schema_version,
    payload_json=parsed_data.model_dump(mode="json"),  # Returns ISO 8601 strings
    validation_status=ValidationStatus.VALID,
    created_by="system",
)
```

### How It Works

Pydantic v2 provides different serialization modes:

**1. Python mode (default)** - `model_dump()`:
```python
{
    "collection_datetime": datetime(2024, 1, 15, 8, 0, 0),  # Python datetime object
    "result_datetime": None,
    "value_type": ValueType.NUMERIC,  # Python Enum object
}
```

**2. JSON mode** - `model_dump(mode="json")`:
```python
{
    "collection_datetime": "2024-01-15T08:00:00",  # ISO 8601 string
    "result_datetime": null,
    "value_type": "numeric",  # String value
}
```

The `mode="json"` parameter tells Pydantic to serialize for JSON output, which:
- Converts `datetime` → ISO 8601 string
- Converts `Enum` → string value
- Converts `UUID` → string representation
- Converts `Decimal` → float or string
- Handles all other types appropriately for JSON

## Test Impact

### Before Fix
```
FAILED tests/integration/test_us1_happy_path.py::test_us1_happy_path
FAILED tests/integration/test_us1_happy_path.py::test_duplicate_upload_detection
======================== 2 failed, 23 passed ========================
```

### After Fix
```
======================== 25 passed ========================
```

Both integration tests that create database records now pass:
- ✅ `test_us1_happy_path` - Full workflow test
- ✅ `test_duplicate_upload_detection` - Duplicate detection test

## Verification

### Data Flow with Fix

1. **Parser Service** creates datetime:
   ```python
   collection_dt = datetime.now()  # datetime(2024, 1, 15, 8, 0, 0)
   ```

2. **Parser Service** creates measurement:
   ```python
   LabMeasurement(
       original_analyte_name="Glucose",
       value_type=ValueType.NUMERIC,
       numeric_value=95.0,
       collection_datetime=collection_dt,  # datetime object
   )
   ```

3. **Pipeline Service** serializes for database:
   ```python
   payload_json = parsed_data.model_dump(mode="json")
   # Returns: {"collection_datetime": "2024-01-15T08:00:00", ...}
   ```

4. **SQLAlchemy** encodes to JSON:
   ```python
   json.dumps(payload_json)  # Success! All strings/numbers/etc.
   ```

5. **PostgreSQL** stores JSONB:
   ```sql
   INSERT INTO parsed_lab_data_versions (payload_json) 
   VALUES ('{"collection_datetime": "2024-01-15T08:00:00", ...}'::JSONB)
   ```

### Reading Data Back

When reading from database:
```python
parsed_version = await db.get(ParsedLabDataVersion, version_id)
payload_dict = parsed_version.payload_json  # Dict with string datetimes

# Reconstruct Pydantic model (Pydantic handles parsing)
parsed_data = ParsedLabData(**payload_dict)
# Pydantic automatically converts "2024-01-15T08:00:00" → datetime object
```

## Alternative Approaches Considered

### 1. Custom JSON Encoder ❌
Could create custom JSON encoder for SQLAlchemy:
```python
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
```

**Rejected**: More complex, requires SQLAlchemy configuration, Pydantic approach is cleaner.

### 2. Manual Serialization ❌
Could manually convert datetimes:
```python
def serialize_datetimes(data: dict) -> dict:
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data
```

**Rejected**: Error-prone, doesn't handle nested structures, Pydantic does this automatically.

### 3. Store as Separate Columns ❌
Could store datetimes in separate timestamp columns instead of JSONB:
```python
collection_datetime = Column(DateTime)  # Separate column
payload_json = Column(JSONB)  # Without datetime fields
```

**Rejected**: Defeats purpose of flexible schema, requires schema changes for new fields.

## Pydantic Serialization Modes Reference

### When to Use Each Mode

**`model_dump()`** - Python mode:
- Use for: Internal Python operations
- Returns: Python native types (datetime, Enum, etc.)
- Example: Passing data between Python functions

**`model_dump(mode="json")`** - JSON mode:
- Use for: Database storage, JSON APIs
- Returns: JSON-compatible types (strings, numbers, etc.)
- Example: Storing in JSONB, preparing for json.dumps()

**`model_dump_json()`** - JSON string:
- Use for: Direct JSON output
- Returns: JSON string
- Example: API responses, file writing

### Conversion Table

| Python Type | Python Mode | JSON Mode |
|-------------|-------------|-----------|
| `datetime` | `datetime(...)` | `"2024-01-15T08:00:00"` |
| `date` | `date(...)` | `"2024-01-15"` |
| `Enum` | `MyEnum.VALUE` | `"value"` |
| `UUID` | `UUID('...')` | `"550e8400-..."` |
| `Decimal` | `Decimal('1.23')` | `1.23` or `"1.23"` |
| `bytes` | `b'...'` | `"base64string"` |
| `set` | `{1, 2, 3}` | `[1, 2, 3]` |

## Key Learnings

### 1. Pydantic v2 Serialization is Context-Aware
Different output formats require different serialization modes. Always use the right mode for the context.

### 2. JSONB Requires JSON-Compatible Types
PostgreSQL JSONB follows JSON spec strictly. Python-specific types must be converted.

### 3. Integration Tests Catch Serialization Issues
Unit tests often don't catch this because they mock database operations. Integration tests with real databases are essential.

### 4. Pydantic Makes This Easy
The `mode="json"` parameter handles all edge cases automatically. No need for custom encoders or manual conversion.

### 5. Read Pydantic Documentation
Pydantic v2 has excellent docs on serialization. When in doubt, check the docs for the right approach.

## Best Practices

### For Database Storage
Always use `mode="json"` when storing Pydantic models in JSONB:
```python
# ✅ Correct
payload = model.model_dump(mode="json")

# ❌ Wrong
payload = model.model_dump()
```

### For API Responses
Use `model_dump_json()` for direct JSON output:
```python
# ✅ Correct
return Response(content=model.model_dump_json(), media_type="application/json")

# ❌ Wrong (extra step)
return Response(content=json.dumps(model.model_dump(mode="json")))
```

### For Python Operations
Use default `model_dump()` for internal operations:
```python
# ✅ Correct - preserves Python types
data = model.model_dump()
process_datetime(data["collection_datetime"])  # datetime object

# ❌ Wrong - loses type information
data = model.model_dump(mode="json")
process_datetime(data["collection_datetime"])  # string, not datetime
```

## References

- [Pydantic Serialization Docs](https://docs.pydantic.dev/latest/concepts/serialization/)
- [PostgreSQL JSONB Type](https://www.postgresql.org/docs/current/datatype-json.html)
- [JSON Specification](https://www.json.org/)

## Status

✅ **Issue Resolved**
- Datetime serialization working
- All 25 tests passing
- Ready for production

---

**Commit**: fc4204c
**Files Changed**: 1 line in `report_pipeline_service.py`
**Impact**: Fixes 2 failing integration tests
**Lesson**: Always use `mode="json"` for JSON/database storage
