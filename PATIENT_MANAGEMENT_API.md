# Patient Management API Documentation

## Overview
Complete patient management system with authentication, role-based access control, and comprehensive CRUD operations for a dental care application.

## Features
- ✅ JWT-based authentication
- ✅ Role-based authorization (admin, receptionist, dentist, user)
- ✅ Full CRUD operations for patients
- ✅ Advanced search and filtering
- ✅ Patient appointment tracking
- ✅ Patient statistics and analytics
- ✅ Soft delete (status-based deactivation)

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
psql -d your_database -f setup_patients_table.sql
```

## API Endpoints

### Patient Management

#### GET `/api/patients`
Get all patients with optional search and status filtering.
- **Auth Required:** Yes (Any authenticated user)
- **Query Parameters:**
  - `search` (optional): Search by name, email, or phone
  - `status` (optional): Filter by status (active, inactive, pending, suspended)

#### GET `/api/patients/{patient_id}`
Get a specific patient by ID.
- **Auth Required:** Yes (Any authenticated user)

#### POST `/api/patients`
Create a new patient.
- **Auth Required:** Yes (Admin or Receptionist)

**Request:**
```json
{
  "name": "John Smith",
  "email": "john.smith@email.com",
  "phone": "(555) 123-4567",
  "date_of_birth": "1985-03-15",
  "status": "active"
}
```

#### PUT `/api/patients/{patient_id}`
Update an existing patient.
- **Auth Required:** Yes (Admin or Receptionist)

#### DELETE `/api/patients/{patient_id}`
Deactivate a patient (admin only).
- **Auth Required:** Yes (Admin only)
- **Note:** Soft delete - sets status to 'inactive'

### Patient Appointments

#### GET `/api/patients/{patient_id}/appointments`
Get all appointments for a specific patient.
- **Auth Required:** Yes (Any authenticated user)

#### PUT `/api/patients/{patient_id}/last-visit`
Update patient's last visit date.
- **Auth Required:** Yes (Admin or Receptionist)

#### PUT `/api/patients/{patient_id}/next-appointment`
Update patient's next appointment date.
- **Auth Required:** Yes (Admin or Receptionist)

### Patient Analytics

#### GET `/api/patients/stats`
Get patient statistics (admin only).
- **Auth Required:** Yes (Admin only)

**Response:**
```json
{
  "total_patients": 150,
  "active_patients": 120,
  "inactive_patients": 30,
  "patients_by_status": [
    {"status": "active", "count": 120},
    {"status": "inactive", "count": 25},
    {"status": "pending", "count": 5}
  ],
  "recent_patients": 15,
  "upcoming_appointments": 45
}
```

#### GET `/api/patients/statuses`
Get all available patient statuses.
- **Auth Required:** Yes (Any authenticated user)

## Data Model

### Patient Entity
```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john.smith@email.com",
  "phone": "(555) 123-4567",
  "date_of_birth": "1985-03-15",
  "last_visit": "2024-01-10",
  "next_appointment": "2024-01-15",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Patient Statuses
- **`active`** - Patient is active and can book appointments
- **`inactive`** - Patient is inactive
- **`pending`** - Patient registration pending
- **`suspended`** - Patient account suspended

## Authorization Levels

### Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all patient operations |
| **Receptionist** | Can create, update, and view patients |
| **Dentist** | Can view patient information and appointments |
| **User** | Can view patient information only |

### Endpoint Access Matrix

| Endpoint | Admin | Receptionist | Dentist | User |
|----------|-------|--------------|---------|------|
| GET `/api/patients` | ✅ | ✅ | ✅ | ✅ |
| GET `/api/patients/{id}` | ✅ | ✅ | ✅ | ✅ |
| POST `/api/patients` | ✅ | ✅ | ❌ | ❌ |
| PUT `/api/patients/{id}` | ✅ | ✅ | ❌ | ❌ |
| DELETE `/api/patients/{id}` | ✅ | ❌ | ❌ | ❌ |
| GET `/api/patients/{id}/appointments` | ✅ | ✅ | ✅ | ✅ |
| PUT `/api/patients/{id}/last-visit` | ✅ | ✅ | ❌ | ❌ |
| PUT `/api/patients/{id}/next-appointment` | ✅ | ✅ | ❌ | ❌ |
| GET `/api/patients/stats` | ✅ | ❌ | ❌ | ❌ |

## Usage Examples

### 1. Create a New Patient (Receptionist/Admin)
```bash
curl -X POST "http://localhost:8000/api/patients" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane.doe@email.com",
    "phone": "(555) 987-6543",
    "date_of_birth": "1990-05-20",
    "status": "active"
  }'
```

### 2. Search Patients
```bash
# Search by name
curl -X GET "http://localhost:8000/api/patients?search=John" \
  -H "Authorization: Bearer <token>"

# Filter by status
curl -X GET "http://localhost:8000/api/patients?status=active" \
  -H "Authorization: Bearer <token>"
```

### 3. Update Patient Information
```bash
curl -X PUT "http://localhost:8000/api/patients/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "(555) 123-9999",
    "status": "active"
  }'
```

### 4. Update Patient Visit Information
```bash
# Update last visit
curl -X PUT "http://localhost:8000/api/patients/1/last-visit" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '"2024-01-20"'

# Update next appointment
curl -X PUT "http://localhost:8000/api/patients/1/next-appointment" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '"2024-02-15"'
```

### 5. Get Patient Appointments
```bash
curl -X GET "http://localhost:8000/api/patients/1/appointments" \
  -H "Authorization: Bearer <token>"
```

### 6. Get Patient Statistics (Admin Only)
```bash
curl -X GET "http://localhost:8000/api/patients/stats" \
  -H "Authorization: Bearer <admin-token>"
```

## Database Schema

### Patients Table
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    last_visit DATE,
    next_appointment DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
- `idx_patients_email` - Fast email lookups
- `idx_patients_name` - Fast name searches
- `idx_patients_status` - Status filtering
- `idx_patients_phone` - Phone number searches
- `idx_patients_date_of_birth` - Date of birth filtering
- `idx_patients_last_visit` - Last visit tracking
- `idx_patients_next_appointment` - Upcoming appointments

### Constraints
- Email must be unique
- Status must be one of: active, inactive, pending, suspended
- Date of birth cannot be in the future
- Last visit cannot be in the future
- Next appointment cannot be in the past

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
  "detail": "Patient with this email already exists"
}
```

#### 404 Not Found
```json
{
  "detail": "Patient not found"
}
```

## Search and Filtering

### Advanced Search Parameters
- **Name Search:** `GET /api/patients?search=John`
- **Email Search:** `GET /api/patients?search=john@email.com`
- **Phone Search:** `GET /api/patients?search=555`
- **Status Filter:** `GET /api/patients?status=active`
- **Combined:** `GET /api/patients?search=John&status=active`

### Search Features
- Case-insensitive search
- Partial matching for name, email, and phone
- Multiple search criteria support
- Status-based filtering
- Date range filtering (planned for future)

## Integration with Other Systems

### Appointment System
- Patients are linked to appointments via name matching
- Last visit and next appointment tracking
- Appointment history retrieval

### User Management
- Role-based access control
- Authentication required for all operations
- Admin-only statistics and management

### Dentist System
- Dentists can view patient information
- Appointment coordination between patients and dentists

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
- Email format validation
- Date validation (no future birth dates)
- Status constraint validation
- Unique email enforcement

## Performance Optimizations

### Database Indexes
- Optimized for common search patterns
- Fast lookups by email, name, status
- Efficient date-based queries

### Query Optimization
- Selective field retrieval
- Efficient filtering and sorting
- Pagination support (planned)

## Monitoring and Analytics

### Patient Statistics
- Total patient count
- Active vs inactive patients
- Recent patient registrations
- Upcoming appointments count
- Status distribution

### Usage Tracking
- Patient creation/modification tracking
- Role-based access logging
- Error monitoring and reporting

## Production Considerations

1. **Data Privacy:** Ensure HIPAA compliance for patient data
2. **Backup Strategy:** Regular database backups for patient data
3. **Audit Logging:** Log all patient data access and modifications
4. **Performance:** Monitor query performance with large patient datasets
5. **Security:** Regular security audits and penetration testing
6. **Scalability:** Consider database partitioning for large patient databases

## Future Enhancements

1. **Advanced Search:** Full-text search capabilities
2. **Patient Photos:** Profile picture support
3. **Medical History:** Comprehensive medical record tracking
4. **Insurance Information:** Insurance provider and policy tracking
5. **Emergency Contacts:** Emergency contact information
6. **Patient Portal:** Self-service patient portal
7. **Appointment Scheduling:** Direct appointment booking
8. **Communication:** Email/SMS notifications
9. **Document Management:** Patient document storage
10. **Analytics Dashboard:** Advanced reporting and analytics

This patient management system provides a comprehensive, secure, and scalable solution for managing patient information in a dental care application.
