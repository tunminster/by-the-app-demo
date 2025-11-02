# Authentication & Authorization Workflow

## Overview
Complete authentication and authorization system with user registration, admin approval, and role-based access control for both user and dentist management.

## 🔐 Authentication Flow

### 1. User Registration (Public)
Users can register but require admin approval to become active.

```bash
POST /api/register
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "name": "New User",
  "role": "user"
}
```

**Response:**
```json
{
  "id": 5,
  "username": "newuser",
  "email": "user@example.com",
  "name": "New User",
  "role": "user",
  "is_active": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 2. Admin Approval (Admin Only)
Admins can view pending users and approve them.

```bash
# Get pending users
GET /api/users/pending
Authorization: Bearer <admin-token>

# Approve a user
POST /api/users/{user_id}/approve
Authorization: Bearer <admin-token>
```

### 3. User Login (Active Users Only)
Only active users can login and receive JWT tokens.

```bash
POST /api/login
{
  "username": "newuser",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "username": "newuser",
    "email": "user@example.com",
    "name": "New User",
    "role": "user",
    "is_active": true,
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

## 🛡️ Authorization Levels

### User Management Endpoints

| Endpoint | Method | Auth Required | Role Required | Description |
|----------|--------|---------------|---------------|-------------|
| `/api/register` | POST | ❌ | - | Register new user (pending approval) |
| `/api/login` | POST | ❌ | - | Login and get JWT token |
| `/api/me` | GET | ✅ | Any | Get current user info |
| `/api/users` | GET | ✅ | Admin | List all users |
| `/api/users/pending` | GET | ✅ | Admin | Get pending users |
| `/api/users/{id}/approve` | POST | ✅ | Admin | Approve user registration |
| `/api/users/{id}` | GET | ✅ | Admin/Self | Get specific user |
| `/api/users/{id}` | PUT | ✅ | Admin/Self | Update user |
| `/api/users/{id}` | DELETE | ✅ | Admin | Deactivate user |
| `/api/users/{id}/change-password` | POST | ✅ | Admin/Self | Change password |

### Dentist Management Endpoints

| Endpoint | Method | Auth Required | Role Required | Description |
|----------|--------|---------------|---------------|-------------|
| `/api/dentists` | GET | ✅ | Any | List dentists |
| `/api/dentists/{id}` | GET | ✅ | Any | Get specific dentist |
| `/api/dentists` | POST | ✅ | Admin | Create dentist |
| `/api/dentists/{id}` | PUT | ✅ | Admin | Update dentist |
| `/api/dentists/{id}` | DELETE | ✅ | Admin | Delete dentist |
| `/api/dentists/{id}/appointments` | GET | ✅ | Admin/Dentist | Get dentist appointments |
| `/api/dentists/specialties` | GET | ✅ | Any | Get specialties |

## 🔑 Role-Based Access Control

### Role Hierarchy

1. **Admin** - Full system access
   - Can approve user registrations
   - Can manage all users
   - Can manage all dentists
   - Can view all appointments

2. **Dentist** - Dentist-specific access
   - Can view dentist information
   - Can view their own appointments
   - Cannot create/delete dentists

3. **Receptionist** - Reception access
   - Can view dentist information
   - Cannot manage dentists
   - Cannot approve users

4. **User** - Basic access
   - Can view dentist information
   - Cannot access user management
   - Cannot access dentist management

## 🚀 Usage Examples

### Complete Registration to Login Flow

#### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "name": "John Doe",
    "role": "user"
  }'
```

#### 2. Admin Login
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

#### 3. Admin Views Pending Users
```bash
curl -X GET "http://localhost:8000/api/users/pending" \
  -H "Authorization: Bearer <admin-token>"
```

#### 4. Admin Approves User
```bash
curl -X POST "http://localhost:8000/api/users/5/approve" \
  -H "Authorization: Bearer <admin-token>"
```

#### 5. User Login (Now Active)
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

#### 6. User Accesses Dentist Information
```bash
curl -X GET "http://localhost:8000/api/dentists" \
  -H "Authorization: Bearer <user-token>"
```

### Dentist Management (Admin Only)

#### Create Dentist
```bash
curl -X POST "http://localhost:8000/api/dentists" \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Sarah Smith",
    "specialty": "Orthodontics",
    "email": "sarah.smith@clinic.com",
    "phone": "+1-555-0123",
    "license": "DDS-123",
    "years_of_experience": 10,
    "working_days": "5 days/week"
  }'
```

#### Update Dentist
```bash
curl -X PUT "http://localhost:8000/api/dentists/1" \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "specialty": "General Dentistry",
    "years_of_experience": 12
  }'
```

## 🔒 Security Features

### JWT Token Security
- **Expiration:** 30 minutes (configurable)
- **Algorithm:** HS256
- **Secret Key:** Environment variable `JWT_SECRET_KEY`
- **Token Validation:** Automatic on all protected endpoints

### Password Security
- **Hashing:** bcrypt with salt
- **Validation:** Strong password requirements
- **Change Password:** Requires current password verification

### Authorization Checks
- **Role-based:** Different access levels per role
- **Resource-based:** Users can only access their own data (except admins)
- **Active Status:** Only active users can login and access protected resources

## 📊 Database Schema Updates

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT false,  -- Changed default to false
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Dentists Table
```sql
CREATE TABLE dentists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    license VARCHAR(100) UNIQUE NOT NULL,
    years_of_experience INTEGER NOT NULL CHECK (years_of_experience >= 0),
    working_days VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚨 Error Handling

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
  "detail": "Username already exists"
}
```

#### 404 Not Found
```json
{
  "detail": "User not found"
}
```

## 🔧 Environment Variables

```bash
# Required for JWT token generation
export JWT_SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"

# Database connection (existing)
export POSTGRES_DB="your_database"
export POSTGRES_USER="your_user"
export POSTGRES_PASSWORD="your_password"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
```

## 🎯 Production Considerations

1. **Strong JWT Secret:** Use a cryptographically secure random key
2. **HTTPS Only:** Always use HTTPS in production
3. **Token Expiration:** Consider shorter expiration times for sensitive operations
4. **Rate Limiting:** Implement rate limiting on login/registration endpoints
5. **Audit Logging:** Log all authentication and authorization events
6. **Password Policy:** Implement stronger password requirements
7. **Account Lockout:** Implement account lockout after failed login attempts

## 🔄 Workflow Summary

1. **User Registration** → Account created but inactive
2. **Admin Approval** → User becomes active
3. **User Login** → JWT token issued
4. **API Access** → Role-based access to endpoints
5. **Dentist Management** → Admin-only operations
6. **User Management** → Admin or self-access only

This system provides a secure, role-based authentication and authorization system that ensures only approved users can access the system and that different user types have appropriate access levels.
