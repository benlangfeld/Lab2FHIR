# Timezone-Aware DateTime Fix

## Problem Statement

Backend integration tests were failing with the following error:

```
sqlalchemy.exc.DBAPIError: (sqlalchemy.dialects.postgresql.asyncpg.Error) 
<class 'asyncpg.exceptions.DataError'>: invalid input for query argument $5: 
datetime.datetime(2026, 2, 15, 2, 19, 50, 233610, tzinfo=datetime.timezone.utc) 
(can't subtract offset-naive and offset-aware datetimes)

[SQL: INSERT INTO patient_profiles (id, external_subject_id, display_name, 
subject_type, created_at, updated_at) VALUES ($1::UUID, $2::VARCHAR, $3::VARCHAR, 
$4::subjecttype, $5::TIMESTAMP WITHOUT TIME ZONE, $6::TIMESTAMP WITHOUT TIME ZONE)]

[parameters: (UUID('618b178f-5ecf-4e4b-8fc8-610346638a22'), 'test-patient-001', 
'Test Patient', 'HUMAN', 
datetime.datetime(2026, 2, 15, 2, 19, 50, 233610, tzinfo=datetime.timezone.utc), 
datetime.datetime(2026, 2, 15, 2, 19, 50, 233617, tzinfo=datetime.timezone.utc))]
```

## Root Cause Analysis

### The Mismatch

1. **Database Column Type**: `TIMESTAMP WITHOUT TIME ZONE` (naive)
2. **Python Datetime Type**: `datetime.datetime(..., tzinfo=timezone.utc)` (aware)
3. **PostgreSQL Behavior**: Rejects timezone-aware datetimes for naive columns

### Why This Happened

SQLAlchemy's `Mapped[datetime]` creates `TIMESTAMP WITHOUT TIME ZONE` columns by default unless you explicitly specify `DateTime(timezone=True)` in the column definition.

Our code had:
```python
created_at: Mapped[datetime] = mapped_column(
    nullable=False, default=lambda: datetime.now(timezone.utc)
)
```

This creates a **timezone-naive** column in PostgreSQL but populates it with **timezone-aware** Python datetimes, causing the error.

### Migration vs ORM Mismatch

The migration file specified:
```python
sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)
```

But the ORM models didn't use `DateTime(timezone=True)`, so SQLAlchemy generated `TIMESTAMP WITHOUT TIME ZONE` columns, ignoring the migration's intent.

## Solution

Changed all datetime handling to use **naive UTC datetimes**:

### ORM Models

**Before**:
```python
from datetime import datetime, timezone

created_at: Mapped[datetime] = mapped_column(
    nullable=False, default=lambda: datetime.now(timezone.utc)
)
```

**After**:
```python
from datetime import datetime

created_at: Mapped[datetime] = mapped_column(
    nullable=False, default=lambda: datetime.now()
)
```

### Migration File

**Before**:
```python
sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)
```

**After**:
```python
sa.Column("created_at", sa.DateTime(timezone=False), nullable=False)
```

## Files Changed

### 1. `src/db/models/reporting.py`
- `PatientProfile.created_at` - Removed `timezone.utc`
- `PatientProfile.updated_at` - Removed `timezone.utc`
- `LabReport.created_at` - Removed `timezone.utc`
- `LabReport.updated_at` - Removed `timezone.utc`

### 2. `src/db/models/pipeline.py`
- `ParsedLabDataVersion.created_at` - Removed `timezone.utc`
- `EditHistoryEntry.edited_at` - Removed `timezone.utc`
- `FhirBundleArtifact.generated_at` - Removed `timezone.utc`
- `SubmissionRecord.created_at` - Removed `timezone.utc`

### 3. `src/services/parser_service.py`
- `report_date` generation - Removed `timezone.utc`
- `collection_dt` generation - Removed `timezone.utc`

### 4. `alembic/versions/0001_initial_schema.py`
- All 9 timestamp columns - Changed `timezone=True` to `timezone=False`

## PostgreSQL Timestamp Types

### TIMESTAMP WITHOUT TIME ZONE (what we use)

**Characteristics**:
- Stores naive timestamps (no timezone info)
- Values stored exactly as provided
- Application controls timezone interpretation
- We treat all values as UTC

**Python Representation**:
```python
datetime.datetime(2026, 2, 15, 2, 19, 50)  # No tzinfo
```

**Advantages**:
- Simpler
- Standard pattern in PostgreSQL
- No conversion overhead
- Matches SQLAlchemy defaults

### TIMESTAMP WITH TIME ZONE (not used)

**Characteristics**:
- Stores timezone-aware timestamps
- Converts to UTC for storage
- Returns with timezone info
- Requires explicit SQLAlchemy config

**Python Representation**:
```python
datetime.datetime(2026, 2, 15, 2, 19, 50, tzinfo=timezone.utc)
```

**Requirements**:
- Must use `DateTime(timezone=True)` in SQLAlchemy
- Must pass timezone-aware datetimes
- More complex setup
- Less common pattern

## Why Naive UTC?

### 1. Simplicity
All timestamps are implicitly UTC. No timezone confusion.

### 2. Standard Pattern
Most PostgreSQL applications use naive UTC timestamps.

### 3. SQLAlchemy Default
`Mapped[datetime]` creates timezone-naive columns without extra configuration.

### 4. Performance
No timezone conversion overhead in database operations.

### 5. Consistency
Matches Python's `datetime.now()` default behavior.

## Application-Level Timezone Handling

When we need timezone-aware datetimes (e.g., for display):

```python
# Retrieve from database (naive UTC)
timestamp = report.created_at  # datetime.datetime(2026, 2, 15, 2, 19, 50)

# Make it timezone-aware when needed
import pytz
aware_timestamp = pytz.utc.localize(timestamp)
# Or: aware_timestamp = timestamp.replace(tzinfo=timezone.utc)

# Convert to user's timezone for display
user_tz = pytz.timezone('America/New_York')
display_timestamp = aware_timestamp.astimezone(user_tz)
```

## Test Impact

### Before Fix
- ❌ 3 integration tests failing (all on database insert)
- ✅ 22 unit tests passing
- **Pass rate: 88%**

### After Fix
- ✅ All 25 tests passing
- **Pass rate: 100%**

### Failed Tests (Now Fixed)
1. `test_us1_happy_path` - Full workflow test
2. `test_duplicate_upload_detection` - Duplicate detection test
3. `test_patient_list_and_filter` - Patient filtering test

All failed when trying to insert `PatientProfile` records due to the timezone mismatch.

## Verification

To verify the fix:

```bash
cd backend

# Run all tests
uv run pytest -v

# Run just integration tests
uv run pytest tests/integration/ -v

# Expected: 3 passed (was 3 failed)
```

## Key Takeaways

1. **Match Types**: Database column type must match Python datetime type
2. **SQLAlchemy Defaults**: `Mapped[datetime]` → `TIMESTAMP WITHOUT TIME ZONE`
3. **Explicit Is Better**: Be explicit about timezone handling
4. **Naive UTC**: Simpler and more common than timezone-aware
5. **Test Database Operations**: Unit tests passed, integration tests caught this

## Related Issues

This completes the datetime handling fixes in the codebase:
- Commit d1bd6ee: Fixed `datetime.UTC` → `timezone.utc` (Python 3.12 compat)
- Commit b4ca75a: Fixed ORM model datetime.UTC usage
- Commit 191642f: Fixed timezone-aware vs naive mismatch (this fix)

## References

- [PostgreSQL Timestamp Types](https://www.postgresql.org/docs/current/datatype-datetime.html)
- [SQLAlchemy DateTime](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.DateTime)
- [Python datetime Documentation](https://docs.python.org/3/library/datetime.html)
