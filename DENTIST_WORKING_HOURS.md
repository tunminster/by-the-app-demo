# Dentist Working Hours Feature

## Overview

Added working hours functionality to the Dentist entity, allowing flexible scheduling with different hours for each day of the week.

## Design

### Data Structure

Working hours are stored as a JSONB object where:
- **Keys:** Day names (monday, tuesday, wednesday, thursday, friday, saturday, sunday)
- **Values:** Object with `start` and `end` times in "HH:MM" format

### Example

```json
{
  "monday": {"start": "09:00", "end": "17:00"},
  "tuesday": {"start": "09:00", "end": "17:00"},
  "wednesday": {"start": "09:00", "end": "17:00"},
  "thursday": {"start": "09:00", "end": "17:00"},
  "friday": {"start": "09:00", "end": "15:00"}
}
```

## New Pydantic Models

### WorkingHours
```python
class WorkingHours(BaseModel):
    """Working hours for a single day"""
    start: str  # Format: "HH:MM"
    end: str    # Format: "HH:MM"
```

### Updated DentistBase
```python
class DentistBase(BaseModel):
    name: str
    specialty: str
    email: EmailStr
    phone: str
    license: str
    years_of_experience: int
    working_days: str  # e.g., "5 days/week"
    working_hours: Dict[str, WorkingHours]  # NEW: Day -> Working Hours
```

## Database Schema

### Migration
```sql
ALTER TABLE dentists ADD COLUMN working_hours JSONB;

-- Create GIN index for better query performance
CREATE INDEX idx_dentists_working_hours ON dentists USING GIN (working_hours);
```

### Sample Data
```sql
UPDATE dentists 
SET working_hours = '{
  "monday": {"start": "09:00", "end": "17:00"},
  "tuesday": {"start": "09:00", "end": "17:00"},
  "wednesday": {"start": "09:00", "end": "17:00"},
  "thursday": {"start": "09:00", "end": "17:00"},
  "friday": {"start": "09:00", "end": "17:00"}
}'::jsonb;
```

## API Endpoints

All existing dentist endpoints now support the new `working_hours` field:

### 1. Create Dentist

**POST** `/api/dentists`

```json
{
  "name": "Dr. Sarah Nguyen",
  "specialty": "General Dentistry",
  "email": "sarah.nguyen@example.com",
  "phone": "(555) 123-4567",
  "license": "DDS-001",
  "years_of_experience": 8,
  "working_days": "5 days/week",
  "working_hours": {
    "monday": {"start": "09:00", "end": "17:00"},
    "tuesday": {"start": "09:00", "end": "17:00"},
    "wednesday": {"start": "09:00", "end": "17:00"},
    "thursday": {"start": "09:00", "end": "17:00"},
    "friday": {"start": "09:00", "end": "15:00"}
  }
}
```

### 2. Get All Dentists

**GET** `/api/dentists`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Dr. Sarah Nguyen",
    "specialty": "General Dentistry",
    "email": "sarah.nguyen@example.com",
    "phone": "(555) 123-4567",
    "license": "DDS-001",
    "years_of_experience": 8,
    "working_days": "5 days/week",
    "working_hours": {
      "monday": {"start": "09:00", "end": "17:00"},
      "tuesday": {"start": "09:00", "end": "17:00"},
      "wednesday": {"start": "09:00", "end": "17:00"},
      "thursday": {"start": "09:00", "end": "17:00"},
      "friday": {"start": "09:00", "end": "15:00"}
    }
  }
]
```

### 3. Get Specific Dentist

**GET** `/api/dentists/{id}`

Returns the dentist with all working hours.

### 4. Update Dentist

**PUT** `/api/dentists/{id}`

```json
{
  "working_hours": {
    "monday": {"start": "08:00", "end": "16:00"},
    "tuesday": {"start": "08:00", "end": "16:00"},
    "wednesday": {"start": "09:00", "end": "17:00"},
    "thursday": {"start": "09:00", "end": "17:00"},
    "friday": {"start": "08:00", "end": "14:00"}
  }
}
```

### 5. Search Dentists

**GET** `/api/dentists/search?specialty=General`

Returns dentists with working hours included in search results.

## Frontend Usage

### JavaScript Example

```javascript
// Create dentist with working hours
const newDentist = {
  name: "Dr. Sarah Nguyen",
  specialty: "General Dentistry",
  email: "sarah.nguyen@example.com",
  phone: "(555) 123-4567",
  license: "DDS-001",
  years_of_experience: 8,
  working_days: "5 days/week",
  working_hours: {
    monday: { start: "09:00", end: "17:00" },
    tuesday: { start: "09:00", end: "17:00" },
    wednesday: { start: "09:00", end: "17:00" },
    thursday: { start: "09:00", end: "17:00" },
    friday: { start: "09:00", end: "15:00" }
  }
};

const response = await fetch('/api/dentists', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(newDentist)
});

const dentist = await response.json();
console.log('Dentist created:', dentist);
```

### React Form Example

```jsx
import React, { useState } from 'react';

const DentistWorkingHoursForm = () => {
  const [workingHours, setWorkingHours] = useState({
    monday: { start: "09:00", end: "17:00" },
    tuesday: { start: "09:00", end: "17:00" },
    wednesday: { start: "09:00", end: "17:00" },
    thursday: { start: "09:00", end: "17:00" },
    friday: { start: "09:00", end: "17:00" }
  });

  const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

  const handleDayChange = (day, field, value) => {
    setWorkingHours({
      ...workingHours,
      [day]: {
        ...workingHours[day],
        [field]: value
      }
    });
  };

  return (
    <div>
      <h3>Working Hours</h3>
      {days.map(day => (
        <div key={day}>
          <label>
            {day.charAt(0).toUpperCase() + day.slice(1)}:
            <input
              type="time"
              value={workingHours[day]?.start || ''}
              onChange={(e) => handleDayChange(day, 'start', e.target.value)}
              disabled={!workingHours[day]}
            />
            <span> to </span>
            <input
              type="time"
              value={workingHours[day]?.end || ''}
              onChange={(e) => handleDayChange(day, 'end', e.target.value)}
              disabled={!workingHours[day]}
            />
          </label>
        </div>
      ))}
    </div>
  );
};
```

## Querying Working Hours

### PostgreSQL Examples

```sql
-- Get dentists working on Mondays
SELECT name, working_hours->'monday' as monday_hours
FROM dentists
WHERE working_hours ? 'monday';

-- Get dentists working after 10:00 AM on Fridays
SELECT name, working_hours->'friday' as friday_hours
FROM dentists
WHERE (working_hours->'friday'->>'start')::time <= '10:00'::time;

-- Count dentists working on weekends
SELECT COUNT(*)
FROM dentists
WHERE working_hours ? 'saturday' OR working_hours ? 'sunday';
```

## Benefits

1. **Flexible Scheduling** - Different hours for each day
2. **Easy Updates** - Change hours for specific days
3. **Fast Queries** - GIN index on JSONB for performance
4. **Type Safety** - Pydantic validation ensures correct format
5. **Backward Compatible** - Optional field, existing data unaffected

## Implementation Details

### Database Functions

All database functions were updated to handle JSONB conversion:

- `get_all_dentists()` - Parses JSONB to dict
- `get_dentist_by_id()` - Parses JSONB to dict  
- `create_dentist()` - Converts dict to JSONB
- `update_dentist()` - Converts dict to JSONB for updates

### Pydantic Models

- `WorkingHours` - Validates time format (HH:MM)
- `DentistBase` - Includes working_hours as Dict[str, WorkingHours]
- `DentistCreate` - Inherits working_hours from DentistBase
- `DentistUpdate` - Supports optional working_hours updates

## Testing

Run the test script to verify the implementation:

```bash
python tests/test_dentist_working_hours.py
```

This will test:
1. ✅ Getting all dentists with working hours
2. ✅ Creating dentist with working hours
3. ✅ Getting specific dentist
4. ✅ Updating working hours
5. ✅ Data structure validation

## Migration

Run the database migration to add the new column:

```bash
psql -h your_host -U your_user -d your_database -f add_dentist_working_hours.sql
```

Or manually:

```sql
ALTER TABLE dentists ADD COLUMN working_hours JSONB;
CREATE INDEX idx_dentists_working_hours ON dentists USING GIN (working_hours);
```
