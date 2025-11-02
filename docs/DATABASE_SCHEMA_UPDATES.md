# Database Schema Updates

## Overview
Updated `db.py` and `booking.py` files to work with the new availability and dentist schemas that include all required columns.

## Changes Made

### 1. **db.py Updates**

#### **fetch_available_slots()**
- **Before:** Used old schema with `is_booked`, `start_time`, `end_time` columns
- **After:** Updated to use new JSONB `time_slots` structure
- **Query:** Now uses `jsonb_array_elements()` to extract available time slots

#### **mark_slot_booked()**
- **Before:** Simple `UPDATE` with `is_booked = TRUE`
- **After:** Complex JSONB update to set specific time slot `available = false`
- **Query:** Uses `jsonb_set()` to update individual time slots

#### **fetch_dentists()**
- **Before:** Only returned `id`, `name`, `specialty`
- **After:** Returns all dentist columns: `id`, `name`, `specialty`, `email`, `phone`, `license`, `years_of_experience`, `working_days`

#### **New Functions Added:**
- `fetch_dentist_by_name()` - Get dentist by name for booking
- `get_availability_by_dentist_and_date()` - Get availability for specific dentist/date
- `update_time_slot_availability()` - Update specific time slot availability

### 2. **booking.py Updates**

#### **build_context_text()**
- **Before:** Used `start_time` and `end_time` directly
- **After:** Extracts time from `time_slot` JSONB object
- **Handles:** `time_slot.start` and `time_slot.end` properties

#### **book_if_possible()**
- **Before:** Used old `mark_slot_booked()` function
- **After:** Uses new `update_time_slot_availability()` function
- **Improvements:** Better error handling and logging

#### **parse_booking_intent_ai()**
- **Before:** Used hardcoded dentist list
- **After:** Dynamically fetches dentist names from database
- **Function:** `get_dentist_names()` gets current dentist list

#### **Dynamic Dentist List**
- **Before:** Hardcoded `DENTISTS = ["Dr. Sarah Nguyen", ...]`
- **After:** `DENTISTS = get_dentist_names()` - fetched from database

## Schema Compatibility

### **Old Availability Schema (Deprecated)**
```sql
CREATE TABLE availability (
    id SERIAL PRIMARY KEY,
    dentist_id INTEGER,
    date DATE,
    start_time TIME,
    end_time TIME,
    is_booked BOOLEAN
);
```

### **New Availability Schema (Current)**
```sql
CREATE TABLE availability (
    id SERIAL PRIMARY KEY,
    dentist_id INTEGER,
    date DATE,
    time_slots JSONB  -- [{"start": "09:00", "end": "10:00", "available": true}]
);
```

### **Old Dentist Schema (Deprecated)**
```sql
CREATE TABLE dentists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    specialty VARCHAR(255)
);
```

### **New Dentist Schema (Current)**
```sql
CREATE TABLE dentists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    specialty VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    license VARCHAR(100),
    years_of_experience INTEGER,
    working_days VARCHAR(50)
);
```

## Migration Notes

### **Availability Migration**
- Old `is_booked` column → New `time_slots` JSONB array
- Old `start_time`/`end_time` → New `time_slots[].start`/`time_slots[].end`
- Each time slot now has individual availability status

### **Dentist Migration**
- Added new columns: `email`, `phone`, `license`, `years_of_experience`, `working_days`
- All existing queries updated to include new columns
- Dynamic dentist list fetching from database

## Benefits of Updates

### **1. Flexibility**
- Multiple time slots per day per dentist
- Individual slot availability tracking
- Rich dentist information

### **2. Performance**
- JSONB queries are fast with proper indexing
- Reduced table joins
- Better data organization

### **3. Maintainability**
- Dynamic dentist list (no hardcoding)
- Better error handling
- Consistent data structure

### **4. Scalability**
- Easy to add new time slots
- Flexible availability patterns
- Better appointment management

## Testing Recommendations

### **1. Database Testing**
```sql
-- Test new availability queries
SELECT * FROM availability WHERE dentist_id = 1 AND date = '2024-01-15';

-- Test time slot extraction
SELECT jsonb_array_elements(time_slots) FROM availability WHERE dentist_id = 1;
```

### **2. API Testing**
```bash
# Test dentist endpoints with new columns
curl -X GET "http://localhost:8000/api/dentists" -H "Authorization: Bearer <token>"

# Test availability endpoints
curl -X GET "http://localhost:8000/api/availability" -H "Authorization: Bearer <token>"
```

### **3. Booking Testing**
```python
# Test booking functionality
from app.utils.booking import book_if_possible

intent = {
    "dentist": "Dr. Sarah Johnson",
    "date": "2024-01-15",
    "time": "09:00",
    "patient_name": "John Doe"
}

result = book_if_possible(intent)
print(f"Booking successful: {result}")
```

## Rollback Plan

If issues arise, you can:

1. **Revert to old schema** by running the old SQL scripts
2. **Update queries** to use old column names
3. **Restore old functions** from version control

## Next Steps

1. **Test all endpoints** with new schema
2. **Update frontend** to handle new dentist fields
3. **Migrate existing data** if needed
4. **Update documentation** for API consumers
5. **Monitor performance** of JSONB queries

The updates ensure full compatibility with the new availability and dentist schemas while maintaining backward compatibility where possible.
