# Availability API Test

## Quick Start

### Run Full Test Suite
```bash
python3 tests/test_availability_api.py
```

### Clean Up Test Data Only
```bash
python3 tests/cleanup_availability.py
```

## What Was Fixed

### Problems
1. **JSONB adapter issue**: `psycopg2` couldn't adapt Python dicts/lists directly to PostgreSQL JSONB
2. **Function naming conflicts**: Helper functions had the same names as endpoints, causing recursive calls

### Solutions

#### 1. JSONB Data Handling
Updated `app/routes/availability.py` to use `psycopg2.extras.Json` adapter:
1. **Import Json adapter**: `from psycopg2.extras import RealDictCursor, Json`
2. **Wrap data**: `Json([slot.dict() for slot in availability_data.time_slots])` (for Pydantic models)
3. **Direct wrap**: `Json(value)` (when value is already a dict/list from `.dict()`)
4. **Add casting**: `INSERT INTO availability (... time_slots) VALUES (%s::jsonb)`

#### 2. Naming Conflicts
Renamed internal helper functions to avoid conflicts:
- `get_availability_by_id()` → `_get_availability_by_id()`
- `get_availability_by_dentist_and_date()` → `_get_availability_by_dentist_and_date()`

#### 3. Logging
Added proper logging configuration to `app/__init__.py` and debug logs to availability operations.

## Test Coverage

The test suite covers:
- ✅ Authentication (login)
- ✅ Create availability
- ✅ Get availability by ID
- ✅ Get all availability
- ✅ Search availability by dentist/date
- ✅ Update availability (book slots)
- ✅ Delete availability
- ✅ Automatic cleanup of test data

## Test Payload

```json
{
    "dentist_id": 11,
    "date": "2025-11-03",
    "time_slots": [
        {"start": "09:00", "end": "10:00", "available": true},
        {"start": "10:00", "end": "11:00", "available": true},
        {"start": "11:00", "end": "12:00", "available": true},
        {"start": "12:00", "end": "13:00", "available": true},
        {"start": "13:00", "end": "14:00", "available": true},
        {"start": "14:00", "end": "15:00", "available": true},
        {"start": "15:00", "end": "16:00", "available": true},
        {"start": "16:00", "end": "17:00", "available": true}
    ]
}
```

## Files Modified
- `app/routes/availability.py` - Fixed JSONB handling, renamed helper functions, added logging
- `app/__init__.py` - Added logging configuration

## Files Created
- `tests/test_availability_api.py` - Full test suite
- `tests/cleanup_availability.py` - Quick cleanup script
- `AVAILABILITY_API_TEST.md` - This documentation

## Next Steps
The Availability API is now fully functional and tested. You can use it to:
- Create dentist availability schedules
- Book/release time slots
- Search for available appointments
- Manage availability records

