# Appointment Management API Documentation

## Overview
Complete appointment management system for dental care with scheduling, conflict prevention, authentication, and role-based access control.

## Features
- ✅ JWT-based authentication
- ✅ Role-based authorization (admin, receptionist, dentist, user)
- ✅ Full CRUD operations for appointments
- ✅ Advanced search and filtering
- ✅ Conflict prevention for double booking
- ✅ Appointment status management
- ✅ Comprehensive statistics and analytics
- ✅ Integration with dentist and patient systems

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
psql -d your_database -f setup_appointments_table.sql
```

## API Endpoints

### Appointment Management

#### GET `/api/appointments`
Get all appointments with optional filtering.
- **Auth Required:** Yes (Any authenticated user)
- **Query Parameters:**
  - `patient` (optional): Filter by patient name
  - `dentist_id` (optional): Filter by dentist ID
  - `date_from` (optional): Filter from date
  - `date_to` (optional): Filter to date
  - `status` (optional): Filter by status
  - `treatment` (optional): Filter by treatment type

#### GET `/api/appointments/{appointment_id}`
Get a specific appointment by ID.
- **Auth Required:** Yes (Any authenticated user)

#### GET `/api/appointments/dentist/{dentist_id}`
Get appointments for a specific dentist.
- **Auth Required:** Yes (Any authenticated user)
- **Query Parameters:**
  - `date` (optional): Filter by specific date

#### GET `/api/appointments/patient/{patient_name}`
Get appointments for a specific patient.
- **Auth Required:** Yes (Any authenticated user)

#### POST `/api/appointments`
Create a new appointment.
- **Auth Required:** Yes (Admin or Receptionist)

**Request:**
```json
{
  "patient": "John Smith",
  "phone": "(555) 123-4567",
  "dentist_id": 1,
  "date": "2024-01-15",
  "time": "09:00",
  "treatment": "Regular Cleaning",
  "status": "confirmed",
  "notes": "Regular checkup and cleaning"
}
```

#### PUT `/api/appointments/{appointment_id}`
Update an existing appointment.
- **Auth Required:** Yes (Admin or Receptionist)

#### DELETE `/api/appointments/{appointment_id}`
Delete an appointment (admin only).
- **Auth Required:** Yes (Admin only)

### Appointment Status Management

#### PUT `/api/appointments/{appointment_id}/status`
Update appointment status.
- **Auth Required:** Yes (Admin or Receptionist)

**Request:**
```json
{
  "status": "completed"
}
```

### Analytics

#### GET `/api/appointments/stats`
Get appointment statistics (admin only).
- **Auth Required:** Yes (Admin only)

**Response:**
```json
{
  "total_appointments": 150,
  "appointments_by_status": [
    {"status": "confirmed", "count": 80},
    {"status": "completed", "count": 60},
    {"status": "cancelled", "count": 10}
  ],
  "appointments_by_dentist": [
    {"dentist_name": "Dr. Sarah Johnson", "appointment_count": 50},
    {"dentist_name": "Dr. Michael Chen", "appointment_count": 40}
  ],
  "today_appointments": 8,
  "upcoming_appointments": 25,
  "common_treatments": [
    {"treatment": "Regular Cleaning", "count": 45},
    {"treatment": "Dental Checkup", "count": 30}
  ]
}
```

#### GET `/api/appointments/statuses`
Get all available appointment statuses.
- **Auth Required:** Yes (Any authenticated user)

## Data Model

### Appointment Entity
```json
{
  "id": 1,
  "patient": "John Smith",
  "phone": "(555) 123-4567",
  "dentist_id": 1,
  "dentist_name": "Dr. Sarah Johnson",
  "date": "2024-01-15",
  "time": "09:00",
  "treatment": "Regular Cleaning",
  "status": "confirmed",
  "notes": "Regular checkup and cleaning",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Appointment Statuses
- **`confirmed`** - Appointment is confirmed
- **`cancelled`** - Appointment is cancelled
- **`completed`** - Appointment is completed
- **`no_show`** - Patient did not show up
- **`rescheduled`** - Appointment is rescheduled

## Authorization Levels

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all appointment operations |
| **Receptionist** | Create, update, view, and manage appointments |
| **Dentist** | View appointments and their own schedule |
| **User** | View appointment information only |

### Endpoint Access Matrix

| Endpoint | Admin | Receptionist | Dentist | User |
|----------|-------|--------------|---------|------|
| GET `/api/appointments` | ✅ | ✅ | ✅ | ✅ |
| GET `/api/appointments/{id}` | ✅ | ✅ | ✅ | ✅ |
| POST `/api/appointments` | ✅ | ✅ | ❌ | ❌ |
| PUT `/api/appointments/{id}` | ✅ | ✅ | ❌ | ❌ |
| DELETE `/api/appointments/{id}` | ✅ | ❌ | ❌ | ❌ |
| PUT `/api/appointments/{id}/status` | ✅ | ✅ | ❌ | ❌ |
| GET `/api/appointments/stats` | ✅ | ❌ | ❌ | ❌ |

## Usage Examples

### 1. Create an Appointment (Receptionist/Admin)
```bash
curl -X POST "http://localhost:8000/api/appointments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient": "Jane Doe",
    "phone": "(555) 987-6543",
    "dentist_id": 1,
    "date": "2024-01-20",
    "time": "14:00",
    "treatment": "Dental Checkup",
    "status": "confirmed",
    "notes": "Annual examination"
  }'
```

### 2. Search Appointments
```bash
# Search by patient
curl -X GET "http://localhost:8000/api/appointments?patient=John" \
  -H "Authorization: Bearer <token>"

# Search by dentist
curl -X GET "http://localhost:8000/api/appointments?dentist_id=1" \
  -H "Authorization: Bearer <token>"

# Search by date range
curl -X GET "http://localhost:8000/api/appointments?date_from=2024-01-15&date_to=2024-01-20" \
  -H "Authorization: Bearer <token>"

# Search by status
curl -X GET "http://localhost:8000/api/appointments?status=confirmed" \
  -H "Authorization: Bearer <token>"
```

### 3. Get Dentist Appointments
```bash
# Get all appointments for a dentist
curl -X GET "http://localhost:8000/api/appointments/dentist/1" \
  -H "Authorization: Bearer <token>"

# Get appointments for a specific date
curl -X GET "http://localhost:8000/api/appointments/dentist/1?date=2024-01-15" \
  -H "Authorization: Bearer <token>"
```

### 4. Update Appointment
```bash
curl -X PUT "http://localhost:8000/api/appointments/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "treatment": "Root Canal",
    "notes": "Updated treatment plan"
  }'
```

### 5. Update Appointment Status
```bash
curl -X PUT "http://localhost:8000/api/appointments/1/status" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '"completed"'
```

### 6. Get Appointment Statistics (Admin)
```bash
curl -X GET "http://localhost:8000/api/appointments/stats" \
  -H "Authorization: Bearer <admin-token>"
```

## Database Schema

### Appointments Table
```sql
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    dentist_id INTEGER NOT NULL REFERENCES dentists(id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    treatment VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'confirmed',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
- `idx_appointments_patient` - Fast patient lookups
- `idx_appointments_dentist_id` - Dentist-based queries
- `idx_appointments_date` - Date-based queries
- `idx_appointments_status` - Status filtering
- `idx_appointments_dentist_date` - Combined dentist and date queries
- `idx_appointments_dentist_time` - Unique constraint for conflict prevention

### Constraints
- Unique constraint on (dentist_id, appointment_date, appointment_time)
- Status must be one of: confirmed, cancelled, completed, no_show, rescheduled
- Appointment date must be >= current date
- Appointment time must be between 08:00 and 18:00

### Views
- `appointments_with_dentist` - Appointments with dentist information
- `today_appointments` - Today's appointments
- `upcoming_appointments` - Future appointments
- `appointments_by_status` - Status distribution

## Advanced Features

### Conflict Prevention
- **Double Booking Prevention:** Unique constraint prevents same dentist/time conflicts
- **Database Triggers:** Automatic conflict checking on insert/update
- **API Validation:** Additional conflict checking in application layer

### Search and Filtering
- **Patient Search:** Search by patient name (case-insensitive)
- **Dentist Filtering:** Filter by specific dentist
- **Date Range:** Filter by date range
- **Status Filtering:** Filter by appointment status
- **Treatment Search:** Search by treatment type

### Status Management
- **Status Updates:** Easy status change operations
- **Status Validation:** Valid status values enforced
- **Status History:** Track status changes (planned)

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
  "detail": "Time slot is already booked for this dentist"
}
```

#### 404 Not Found
```json
{
  "detail": "Appointment not found"
}
```

#### 422 Validation Error
```json
{
  "detail": "Invalid appointment time format"
}
```

## Performance Optimizations

### Database Indexes
- Optimized for common query patterns
- Composite indexes for dentist + date queries
- Unique indexes for conflict prevention

### Query Optimization
- Efficient filtering and sorting
- Selective field retrieval
- Optimized joins with dentist table

### Caching Strategy
- Consider Redis caching for frequently accessed appointments
- Cache today's appointments
- Invalidate cache on appointment updates

## Integration with Other Systems

### Dentist System
- Appointments linked to dentist records
- Dentist-specific appointment queries
- Dentist schedule management

### Patient System
- Patient appointment history
- Patient-specific appointment filtering
- Patient contact information integration

### Availability System
- Real-time availability updates
- Conflict prevention with availability
- Slot booking integration

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
- Date constraint validation
- Status value validation
- Conflict prevention

## Monitoring and Analytics

### Appointment Statistics
- Total appointment count
- Status distribution
- Dentist workload analysis
- Treatment popularity
- Daily/weekly trends

### Usage Tracking
- Appointment creation/modification tracking
- Role-based access logging
- Performance monitoring
- Error tracking

## Production Considerations

1. **Data Consistency:** Ensure atomic operations for appointment management
2. **Concurrency:** Handle concurrent booking attempts
3. **Performance:** Monitor query performance with large appointment datasets
4. **Backup Strategy:** Regular database backups for appointment data
5. **Audit Logging:** Log all appointment changes and status updates
6. **Scalability:** Consider database partitioning for large appointment datasets

## Future Enhancements

1. **Recurring Appointments:** Support for recurring appointment schedules
2. **Appointment Reminders:** Email/SMS notification system
3. **Waitlist Management:** Patient waitlist for popular time slots
4. **Calendar Integration:** Google Calendar/Outlook integration
5. **Mobile App:** Mobile appointment management
6. **Advanced Analytics:** Detailed reporting and analytics
7. **Appointment Templates:** Predefined appointment types
8. **Payment Integration:** Payment processing for appointments
9. **Document Management:** Attach documents to appointments
10. **Communication:** In-app messaging between patients and staff

This appointment management system provides a comprehensive, secure, and scalable solution for managing dental appointments with advanced conflict prevention and role-based access control.
