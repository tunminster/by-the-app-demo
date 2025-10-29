# Test Files Organization

## Overview

All test files have been moved from the root directory to the `tests/` folder for better organization.

## Moved Files

The following test files were moved from root to `tests/`:

### Authentication Tests
- `test_admin_login.py` - Test admin login functionality
- `test_auth_endpoints.py` - Test authentication endpoints
- `test_refresh_token.py` - Test refresh token functionality

### API Tests
- `test_appointments_debug.py` - Debug appointments API issues
- `test_appointments_fixed.py` - Test fixed appointments API
- `test_dashboard_endpoints.py` - Test dashboard endpoints
- `test_patient_new_fields.py` - Test patient API with new fields

### Kafka Tests
- `test_ai_response_kafka.py` - Test AI response Kafka integration
- `test_kafka_simple.py` - Simple Kafka test
- `test_integration_docker.py` - Docker integration test
- `test_integration_real_response.py` - Real response integration test

### Voice/AI Tests
- `test_booking_fix.py` - Test booking fix functionality
- `test_improved_instructions.py` - Test improved AI instructions
- `test_json_extraction.py` - Test JSON extraction from AI responses
- `test_rag_injection.py` - Test RAG injection functionality
- `test_reminder_logic.py` - Test reminder logic
- `test_system_message.py` - Test system message functionality

## Running Tests

### From Root Directory
```bash
# Run individual tests
python tests/test_auth_endpoints.py
python tests/test_appointments_fixed.py
python tests/test_refresh_token.py
python tests/test_patient_new_fields.py

# Run all tests (if run_all_tests.py exists)
python tests/run_all_tests.py
```

### From Tests Directory
```bash
cd tests

# Run individual tests
python test_auth_endpoints.py
python test_appointments_fixed.py
python test_refresh_token.py
python test_patient_new_fields.py

# Run all tests
python run_all_tests.py
```

## Updated File Paths

If you have any scripts or documentation that reference the old test file paths, update them:

**Old Paths:**
```bash
python test_auth_endpoints.py
python test_appointments_fixed.py
python test_refresh_token.py
python test_patient_new_fields.py
```

**New Paths:**
```bash
python tests/test_auth_endpoints.py
python tests/test_appointments_fixed.py
python tests/test_refresh_token.py
python tests/test_patient_new_fields.py
```

## Test Categories

### Core API Tests
- Authentication (`test_auth_endpoints.py`, `test_refresh_token.py`)
- Appointments (`test_appointments_debug.py`, `test_appointments_fixed.py`)
- Patients (`test_patient_new_fields.py`)
- Dashboard (`test_dashboard_endpoints.py`)

### Integration Tests
- Kafka (`test_ai_response_kafka.py`, `test_kafka_simple.py`)
- Docker (`test_integration_docker.py`)
- Voice/AI (`test_rag_injection.py`, `test_improved_instructions.py`)

### Utility Tests
- JSON extraction (`test_json_extraction.py`)
- Booking logic (`test_booking_fix.py`)
- Reminder logic (`test_reminder_logic.py`)

## Benefits

1. **Better Organization** - All tests in one location
2. **Cleaner Root Directory** - Reduced clutter in main project folder
3. **Easier Maintenance** - Centralized test management
4. **Standard Structure** - Follows common Python project conventions
5. **Better CI/CD** - Easier to run test suites in automated pipelines

## Next Steps

1. **Update CI/CD** - If you have automated testing, update paths
2. **Update Documentation** - Update any docs referencing old test paths
3. **IDE Configuration** - Update IDE test runner configurations if needed
4. **Add Test Categories** - Consider organizing tests into subdirectories by feature
