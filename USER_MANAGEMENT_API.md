# User Management API Documentation

## Overview
Complete user management system with authentication, authorization, and CRUD operations for a dental care application.

## Features
- ✅ JWT-based authentication
- ✅ Role-based authorization (admin, user, dentist, receptionist)
- ✅ Password hashing with bcrypt
- ✅ User CRUD operations
- ✅ Search and filtering
- ✅ User statistics
- ✅ Password change functionality
- ✅ Soft delete (deactivation)

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
psql -d your_database -f setup_users_table.sql
```

## API Endpoints

### Authentication

#### POST `/api/login`
Login and get access token.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@dentalcare.com",
    "name": "System Administrator",
    "role": "admin",
    "is_active": true,
    "last_login": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### User Management

#### GET `/api/me`
Get current user information.
- **Auth Required:** Yes
- **Headers:** `Authorization: Bearer <token>`

#### GET `/api/users`
Get all users (admin only).
- **Auth Required:** Yes (Admin)
- **Query Parameters:**
  - `search` (optional): Search by username, email, or name
  - `role` (optional): Filter by role
  - `is_active` (optional): Filter by active status

#### GET `/api/users/{user_id}`
Get specific user by ID.
- **Auth Required:** Yes (Admin or own data)

#### POST `/api/users`
Create new user (admin only).
- **Auth Required:** Yes (Admin)

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "New User",
  "role": "user",
  "is_active": true
}
```

#### PUT `/api/users/{user_id}`
Update user information.
- **Auth Required:** Yes (Admin or own data)

**Request:**
```json
{
  "name": "Updated Name",
  "role": "dentist",
  "is_active": true
}
```

#### DELETE `/api/users/{user_id}`
Deactivate user (admin only).
- **Auth Required:** Yes (Admin)
- **Note:** Soft delete - sets `is_active` to false

#### POST `/api/users/{user_id}/change-password`
Change user password.
- **Auth Required:** Yes (Admin or own data)

**Request:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### Utility Endpoints

#### GET `/api/users/roles`
Get available user roles.
- **Auth Required:** Yes (Admin)

#### GET `/api/users/stats`
Get user statistics.
- **Auth Required:** Yes (Admin)

**Response:**
```json
{
  "total_users": 10,
  "active_users": 8,
  "inactive_users": 2,
  "users_by_role": [
    {"role": "admin", "count": 1},
    {"role": "user", "count": 5},
    {"role": "dentist", "count": 3}
  ],
  "recent_logins": 5
}
```

## User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `admin` | System administrator | Full access to all endpoints |
| `user` | Basic user | Access to own data only |
| `dentist` | Dentist user | Dentist-specific access |
| `receptionist` | Reception staff | Reception-specific access |

## Security Features

### Password Security
- Passwords are hashed using bcrypt
- Minimum security requirements enforced
- Password change requires current password verification

### JWT Authentication
- Access tokens expire in 30 minutes (configurable)
- Tokens include user role for authorization
- Automatic token validation on protected endpoints

### Authorization Levels
1. **Public:** Login endpoint only
2. **Authenticated:** User's own data
3. **Admin:** All user management operations

## Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid credentials)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## Usage Examples

### 1. Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Get Current User Info
```bash
curl -X GET "http://localhost:8000/api/me" \
  -H "Authorization: Bearer <your-token>"
```

### 3. Create New User (Admin)
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123",
    "name": "New User",
    "role": "user"
  }'
```

### 4. Search Users
```bash
curl -X GET "http://localhost:8000/api/users?search=admin&role=admin" \
  -H "Authorization: Bearer <admin-token>"
```

## Default Admin User

After running the SQL setup script, you'll have a default admin user:

- **Username:** `admin`
- **Email:** `admin@dentalcare.com`
- **Password:** `admin123`
- **Role:** `admin`

**⚠️ Important:** Change the default password in production!

## Production Considerations

1. **Change JWT Secret:** Set a strong `JWT_SECRET_KEY` environment variable
2. **HTTPS Only:** Use HTTPS in production for secure token transmission
3. **Password Policy:** Implement stronger password requirements
4. **Rate Limiting:** Add rate limiting to prevent brute force attacks
5. **Audit Logging:** Log all user management activities
6. **Backup:** Regular database backups for user data

## Integration with Other Systems

The user management system integrates with:
- **Dentist Management:** Users with `dentist` role can access dentist-specific features
- **Appointment System:** User authentication for appointment booking
- **Voice System:** User context for AI voice interactions
