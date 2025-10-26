# Authentication Endpoints Setup

## Overview
This document describes the new authentication endpoints available at `/auth` prefix.

## Endpoints

### 1. Login
**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive JWT access token

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

**Error Responses:**
- `401 Unauthorized`: Incorrect username or password
- `401 Unauthorized`: Account is deactivated
- `500 Internal Server Error`: Server error

---

### 2. Register
**Endpoint:** `POST /auth/register`

**Description:** Register a new user (requires admin approval)

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "name": "John Doe",
  "role": "user"
}
```

**Response (200 OK):**
```json
{
  "id": 5,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "name": "John Doe",
  "role": "user",
  "is_active": false,
  "last_login": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Username already exists
- `400 Bad Request`: Email already exists
- `500 Internal Server Error`: Server error

**Note:** New users are created with `is_active: false` and require admin approval to login.

---

### 3. Get Current User
**Endpoint:** `GET /auth/me`

**Description:** Get current authenticated user information

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
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
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Server error

---

## Usage Examples

### JavaScript/TypeScript (Fetch API)
```javascript
// Login
const loginResponse = await fetch('https://api-demo.bytheapp.com/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});

const loginData = await loginResponse.json();
const token = loginData.access_token;

// Get current user
const userResponse = await fetch('https://api-demo.bytheapp.com/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const userData = await userResponse.json();
console.log(userData);
```

### Python (requests)
```python
import requests

# Login
login_response = requests.post(
    'https://api-demo.bytheapp.com/auth/login',
    json={
        'username': 'admin',
        'password': 'admin123'
    }
)

token = login_response.json()['access_token']

# Get current user
user_response = requests.get(
    'https://api-demo.bytheapp.com/auth/me',
    headers={'Authorization': f'Bearer {token}'}
)

user_data = user_response.json()
print(user_data)
```

### cURL
```bash
# Login
curl -X POST https://api-demo.bytheapp.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Get current user (replace TOKEN with actual token)
curl -X GET https://api-demo.bytheapp.com/auth/me \
  -H "Authorization: Bearer TOKEN"
```

---

## Testing

### Run the test script
```bash
python test_auth_endpoints.py
```

This will test all three endpoints and verify they're working correctly.

---

## Implementation Details

### Files Created/Modified
- **Created:** `app/routes/auth.py` - New authentication router
- **Modified:** `app/__init__.py` - Registered auth_router with `/auth` prefix
- **Created:** `test_auth_endpoints.py` - Test script for auth endpoints

### Security Features
- **Password Hashing:** Uses bcrypt for secure password storage
- **JWT Tokens:** Access tokens expire after 30 minutes
- **Role-Based Access:** Users have roles (admin, user, dentist, receptionist)
- **Admin Approval:** New registrations require admin activation
- **Token Validation:** Bearer token authentication for protected endpoints

### Database Requirements
The `users` table should have the following columns:
- `id` (integer, primary key)
- `username` (string, unique)
- `email` (string, unique)
- `password_hash` (string, bcrypt hashed)
- `name` (string)
- `role` (string)
- `is_active` (boolean)
- `last_login` (timestamp, nullable)
- `created_at` (timestamp)
- `updated_at` (timestamp)

---

## Troubleshooting

### Common Issues

1. **401 Unauthorized on /auth/me**
   - Check that the token is being sent in the Authorization header
   - Verify the token hasn't expired (30 minutes)
   - Ensure the token is prefixed with "Bearer "

2. **Account deactivated error**
   - New registrations require admin approval
   - Contact an administrator to activate your account

3. **Username/Email already exists**
   - Choose a different username or email
   - Check if you already have an account

---

## Related Endpoints

The existing user management endpoints are still available under `/api`:
- `POST /api/users` - Create user (admin only)
- `GET /api/users` - Get all users (admin only)
- `GET /api/users/{id}` - Get specific user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `POST /api/users/{id}/approve` - Approve user

---

## Next Steps

1. Deploy the updated code to your production environment
2. Test the endpoints using the provided test script
3. Update your frontend to use the new `/auth` endpoints
4. Configure admin users to approve new registrations
