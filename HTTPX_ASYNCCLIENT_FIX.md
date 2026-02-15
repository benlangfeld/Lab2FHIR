# httpx AsyncClient API Fix for Integration Tests

## Problem Summary

**Date Fixed**: 2026-02-15  
**Commit**: 2f2fa78  
**Issue**: All 3 integration tests were failing with `TypeError`

### Error Message
```
TypeError: AsyncClient.__init__() got an unexpected keyword argument 'app'
```

### Affected Tests
1. `tests/integration/test_us1_happy_path.py::test_us1_happy_path`
2. `tests/integration/test_us1_happy_path.py::test_duplicate_upload_detection`
3. `tests/integration/test_us1_happy_path.py::test_patient_list_and_filter`

### Impact
- ✅ Unit tests (22): Passing
- ❌ Integration tests (3): Failing
- **CI Status**: Backend test job failing

## Root Cause

The httpx library changed its API for testing ASGI applications starting from version 0.23.0. The old method of directly passing the app to `AsyncClient` was deprecated and removed.

### Old API (Deprecated)
```python
from httpx import AsyncClient

async with AsyncClient(app=app, base_url="http://test") as client:
    response = await client.get("/endpoint")
```

### New API (Current)
```python
from httpx import ASGITransport, AsyncClient

async with AsyncClient(
    transport=ASGITransport(app=app),
    base_url="http://test"
) as client:
    response = await client.get("/endpoint")
```

## Solution

### File Changed
`backend/tests/conftest.py`

### Changes Made

#### 1. Import Update
```diff
- from httpx import AsyncClient
+ from httpx import ASGITransport, AsyncClient
```

#### 2. Client Fixture Update
```diff
  @pytest_asyncio.fixture
  async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
      """Create test client."""
  
      async def override_get_db():
          yield test_db
  
      app.dependency_overrides[get_db] = override_get_db
  
-     async with AsyncClient(app=app, base_url="http://test") as ac:
+     async with AsyncClient(
+         transport=ASGITransport(app=app), base_url="http://test"
+     ) as ac:
          yield ac
  
      app.dependency_overrides.clear()
```

## Technical Explanation

### Why the Change Was Necessary

1. **Separation of Concerns**: The new API separates the transport layer (how requests are sent) from the client configuration (what requests to send).

2. **Flexibility**: Using explicit transport objects allows for more customization and testing scenarios:
   - Mock transports for unit testing
   - Custom transports for special protocols
   - ASGI transport for testing ASGI apps
   - WSGI transport for testing WSGI apps

3. **Type Safety**: The new API provides better type hints and clearer semantics about what kind of application is being tested.

### ASGITransport

The `ASGITransport` class wraps an ASGI application (like FastAPI) and makes it testable with httpx's `AsyncClient`:

```python
transport = ASGITransport(app=app)
# This creates a transport that can:
# - Handle async requests
# - Route to ASGI app endpoints
# - Manage request/response lifecycle
# - Work with FastAPI dependency injection
```

## Testing

### Unit Tests
No changes were needed for unit tests as they don't use the `client` fixture.

**Result**: ✅ 22/22 passing

### Integration Tests
All integration tests now work correctly with the updated fixture.

**Result**: ✅ 3/3 passing

### Total Test Suite
✅ **25/25 tests passing**

## Verification Commands

```bash
# Run all tests
cd backend
uv run pytest -v

# Run only integration tests
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## CI/CD Impact

### Before Fix
```
Backend CI - Test Job
  ❌ FAILED
  - 22 passed
  - 3 errors
  - Exit code: 1
```

### After Fix
```
Backend CI - Test Job
  ✅ PASSED
  - 25 passed
  - 0 errors
  - Exit code: 0
```

## Related Issues

### Pydantic Deprecation Warnings
The test output also showed 5 Pydantic deprecation warnings about using class-based `config` instead of `ConfigDict`. These are warnings, not errors, and don't affect test execution. They can be addressed in a future commit.

**Files with warnings**:
- `src/domain/intermediate_schema.py`
- `src/api/bundles.py`
- `src/api/parsed_data.py`
- `src/api/patients.py`
- `src/api/reports.py`

## References

- [httpx Documentation - Testing ASGI Applications](https://www.python-httpx.org/advanced/#custom-transports)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [httpx Changelog - Version 0.23.0](https://github.com/encode/httpx/blob/master/CHANGELOG.md#0230-15th-march-2022)
- [httpx GitHub Issue - AsyncClient app parameter removal](https://github.com/encode/httpx/discussions/2015)

## Lessons Learned

1. **Keep Dependencies Updated**: Regular updates help catch breaking changes early
2. **Follow Migration Guides**: httpx provided clear migration paths in their changelog
3. **Test Integration Points**: Integration tests caught this issue before production
4. **Modern API Patterns**: The new API is more explicit and maintainable

## Summary

**Problem**: Integration tests failing due to httpx API change  
**Solution**: Use `ASGITransport` to wrap the FastAPI app  
**Result**: All 25 tests now passing  
**Impact**: Minimal - 1 file changed, 2 lines modified  
**Status**: ✅ Complete and verified

---

**Last Updated**: 2026-02-15  
**Author**: GitHub Copilot  
**Commit**: 2f2fa785cfee133745f4bc3fc55cbe0014053464
