# Availability Management API Documentation

## Overview
Complete availability management system for dental appointments with time slot booking, authentication, and role-based access control.

## Features
- ✅ JWT-based authentication
- ✅ Role-based authorization (admin, receptionist, dentist, user)
- ✅ Time slot management with JSON storage
- ✅ Advanced search and filtering
- ✅ Time slot booking and release
- ✅ Availability statistics and analytics
- ✅ Dentist-specific availability tracking

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export JWT_SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"
```

### 3. Create Database Tables
```bash
psql -d your_database -f setup_availability_table.sql
```

## API Endpoints

### Availability Management

#### GET `/api/availability`
Get all availability records with optional filtering.
- **Auth Required:** Yes (Any authenticated user)
- **Query Parameters:**
  - `dentist_id` (optional): Filter by dentist
  - `date_from` (optional): Filter from date
  - `date_to` (optional): Filter to date
  - `available_only` (optional): Show only available slots

#### GET `/api/availability/{availability_id}`
Get a specific availability record by ID.
- **Auth Required:** Yes (Any authenticated user)

#### GET `/api/availability/dentist/{dentist_id}/date/{date}`
Get availability for a specific dentist on a specific date.
- **Auth Required:** Yes (Any authenticated user)

#### GET `/api/availability/dentist/{dentist_id}/available`
Get only available time slots for a specific dentist on a specific date.
- **Auth Required:** Yes (Any authenticated user)

#### POST `/api/availability`
Create a new availability record.
- **Auth Required:** Yes (Admin or Receptionist)

**Request:**
```json
{
  "dentist_id": 1,
  "date": "2024-01-15",
  "time_slots": [
    {"start": "09:00", "end": "10:00", "available": true},
    {"start": "10:00", "end": "11:00", "available": true},
    {"start": "11:00", "end": "12:00", "available": false},
    {"start": "14:00", "end": "15:00", "available": true},
    {"start": "15:00", "end": "16:00", "available": true},
    {"start": "16:00", "end": "17:00", "available": true}
  ]
}
```

#### PUT `/api/availability/{availability_id}`
Update an existing availability record.
- **Auth Required:** Yes (Admin or Receptionist)

#### DELETE `/api/availability/{availability_id}`
Delete an availability record (admin only).
- **Auth Required:** Yes (Admin only)

### Time Slot Management

#### POST `/api/availability/{availability_id}/book-slot`
Book a specific time slot.
- **Auth Required:** Yes (Admin or Receptionist)

**Request:**
```json
{
  "start": "10:00",
  "end": "11:00",
  "available": false
}
```

#### POST `/api/availability/{availability_id}/release-slot`
Release a specific time slot.
- **Auth Required:** Yes (Admin or Receptionist)

**Request:**
```json
{
  "start": "10:00",
  "end": "11:00",
  "available": true
}
```

### Analytics

#### GET `/api/availability/stats`
Get availability statistics (admin only).
- **Auth Required:** Yes (Admin only)

**Response:**
```json
{
  "total_availability_records": 25,
  "total_available_slots": 150,
  "total_booked_slots": 45,
  "availability_by_dentist": [
    {"dentist_name": "Dr. Sarah Johnson", "availability_count": 10},
    {"dentist_name": "Dr. Michael Chen", "availability_count": 8}
  ],
  "upcoming_availability": 12
}
```

## Data Model

### Availability Entity
```json
{
  "id": 1,
  "dentist_id": 1,
  "dentist_name": "Dr. Sarah Johnson",
  "date": "2024-01-15",
  "time_slots": [
    {"start": "09:00", "end": "10:00", "available": true},
    {"start": "10:00", "end": "11:00", "available": true},
    {"start": "11:00", "end": "12:00", "available": false},
    {"start": "14:00", "end": "15:00", "available": true},
    {"start": "15:00", "end": "16:00", "available": true},
    {"start": "16:00", "end": "17:00", "available": true}
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Time Slot Structure
```json
{
  "start": "09:00",    // Start time in HH:MM format
  "end": "10:00",      // End time in HH:MM format
  "available": true    // Boolean indicating availability
}
```

## Authorization Levels

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all availability operations |
| **Receptionist** | Can create, update, view, and manage time slots |
| **Dentist** | Can view availability and their own schedules |
| **User** | Can view available time slots only |

### Endpoint Access Matrix

| Endpoint | Admin | Receptionist | Dentist | User |
|----------|-------|--------------|---------|------|
| GET `/api/availability` | ✅ | ✅ | ✅ | ✅ |
| GET `/api/availability/{id}` | ✅ | ✅ | ✅ | ✅ |
| POST `/api/availability` | ✅ | ✅ | ❌ | ❌ |
| PUT `/api/availability/{id}` | ✅ | ✅ | ❌ | ❌ |
| DELETE `/api/availability/{id}` | ✅ | ❌ | ❌ | ❌ |
| POST `/api/availability/{id}/book-slot` | ✅ | ✅ | ❌ | ❌ |
| POST `/api/availability/{id}/release-slot` | ✅ | ✅ | ❌ | ❌ |
| GET `/api/availability/stats` | ✅ | ❌ | ❌ | ❌ |

## Usage Examples

### 1. Create Availability (Receptionist/Admin)
```bash
curl -X POST "http://localhost:8000/api/availability" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dentist_id": 1,
    "date": "2024-01-20",
    "time_slots": [
      {"start": "09:00", "end": "10:00", "available": true},
      {"start": "10:00", "end": "11:00", "available": true},
      {"start": "11:00", "end": "12:00", "available": true},
      {"start": "14:00", "end": "15:00", "available": true},
      {"start": "15:00", "end": "16:00", "available": true}
    ]
  }'
```

### 2. Get Available Slots for a Dentist
```bash
# Get all availability for a dentist on a specific date
curl -X GET "http://localhost:8000/api/availability/dentist/1/date/2024-01-15" \
  -H "Authorization: Bearer <token>"

# Get only available slots
curl -X GET "http://localhost:8000/api/availability/dentist/1/available?date=2024-01-15" \
  -H "Authorization: Bearer <token>"
```

### 3. Search Availability
```bash
# Get availability for a specific dentist
curl -X GET "http://localhost:8000/api/availability?dentist_id=1" \
  -H "Authorization: Bearer <token>"

# Get availability for a date range
curl -X GET "http://localhost:8000/api/availability?date_from=2024-01-15&date_to=2024-01-20" \
  -H "Authorization: Bearer <token>"

# Get only available slots
curl -X GET "http://localhost:8000/api/availability?available_only=true" \
  -H "Authorization: Bearer <token>"
```

### 4. Book a Time Slot
```bash
curl -X POST "http://localhost:8000/api/availability/1/book-slot" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "10:00",
    "end": "11:00",
    "available": false
  }'
```

### 5. Release a Time Slot
```bash
curl -X POST "http://localhost:8000/api/availability/1/release-slot" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "10:00",
    "end": "11:00",
    "available": true
  }'
```

### 6. Update Availability
```bash
curl -X PUT "http://localhost:8000/api/availability/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "time_slots": [
      {"start": "09:00", "end": "10:00", "available": true},
      {"start": "10:00", "end": "11:00", "available": false},
      {"start": "11:00", "end": "12:00", "available": true}
    ]
  }'
```

## Database Schema

### Availability Table
```sql
CREATE TABLE availability (
    id SERIAL PRIMARY KEY,
    dentist_id INTEGER NOT NULL REFERENCES dentists(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time_slots JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dentist_id, date)
);
```

### Indexes
- `idx_availability_dentist_id` - Fast dentist lookups
- `idx_availability_date` - Date-based queries
- `idx_availability_dentist_date` - Combined dentist and date queries
- `idx_availability_time_slots` - GIN index for JSON queries

### Views
- `available_slots_view` - Easy querying of available slots
- `booked_slots_view` - Easy querying of booked slots

### Constraints
- Unique constraint on (dentist_id, date)
- Date must be >= current date
- Time slots must be valid JSON array
- Time format validation (HH:MM)
- Boolean validation for available field

## Advanced Features

### Time Slot Validation
- Automatic validation of time format (HH:MM)
- Boolean validation for availability status
- JSON structure validation
- Time slot overlap detection (planned)

### Search and Filtering
- **Dentist-specific:** Filter by dentist ID
- **Date range:** Filter by date range
- **Available only:** Show only available slots
- **Combined filters:** Multiple criteria support

### Booking Management
- **Book slots:** Mark time slots as unavailable
- **Release slots:** Mark time slots as available
- **Bulk operations:** Multiple slot management
- **Conflict detection:** Prevent double booking

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 400 Bad Request
```json
{
  "detail": "Availability already exists for this dentist on this date"
}
```

#### 404 Not Found
```json
{
  "detail": "Availability record not found"
}
```

#### 422 Validation Error
```json
{
  "detail": "Invalid start time format. Use HH:MM format"
}
```

## Performance Optimizations

### Database Indexes
- Optimized for common query patterns
- GIN index for JSON time_slots queries
- Composite indexes for dentist + date queries

### Query Optimization
- Efficient JSON queries using PostgreSQL JSONB
- Selective field retrieval
- Optimized filtering and sorting

### Caching Strategy
- Consider Redis caching for frequently accessed availability
- Cache popular dentist schedules
- Invalidate cache on availability updates

## Integration with Other Systems

### Appointment System
- Availability feeds into appointment booking
- Real-time slot availability updates
- Conflict prevention with existing appointments

### Dentist Management
- Availability linked to dentist records
- Dentist-specific schedule management
- Role-based access to dentist schedules

### Patient System
- Patients can view available slots
- Appointment booking integration
- Patient-specific availability filtering

## Security Features

### Authentication
- JWT token validation on all endpoints
- Token expiration handling
- User role verification

### Authorization
- Role-based access control
- Resource-level permissions
- Admin-only operations protection

### Data Validation
- Time format validation (HH:MM)
- JSON structure validation
- Boolean field validation
- Date constraint validation

## Monitoring and Analytics

### Availability Statistics
- Total availability records
- Available vs booked slots
- Dentist-specific statistics
- Upcoming availability tracking

### Usage Tracking
- Availability creation/modification tracking
- Booking pattern analysis
- Role-based access logging
- Performance monitoring

## Production Considerations

1. **Data Consistency:** Ensure atomic operations for booking/releasing slots
2. **Concurrency:** Handle concurrent booking attempts
3. **Performance:** Monitor JSON query performance with large datasets
4. **Backup Strategy:** Regular database backups for availability data
5. **Audit Logging:** Log all availability changes and bookings
6. **Scalability:** Consider database partitioning for large availability datasets

## Future Enhancements

1. **Recurring Availability:** Support for recurring schedules
2. **Time Zone Support:** Multi-timezone availability
3. **Advanced Booking:** Waitlist and priority booking
4. **Integration:** Calendar system integration
5. **Notifications:** Real-time availability updates
6. **Analytics:** Advanced booking analytics and reporting
7. **Mobile Support:** Mobile-optimized availability management
8. **API Rate Limiting:** Prevent abuse of availability endpoints
9. **Caching:** Redis caching for improved performance
10. **Webhooks:** Real-time availability change notifications

This availability management system provides a comprehensive, secure, and scalable solution for managing dental appointment availability with advanced time slot management capabilities.
