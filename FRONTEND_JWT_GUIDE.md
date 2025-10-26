# Frontend JWT Token Guide

## TL;DR - What Frontend Needs to Know

**Frontend NEVER needs `JWT_SECRET_KEY`** ❌

The frontend only needs to:
1. ✅ Send login request with username/password
2. ✅ Receive and store the JWT token from the API
3. ✅ Send the token with authenticated requests

## How It Works

### 1. User Logs In (Frontend → Backend)

**Frontend sends:**
```javascript
POST /auth/login
{
  "username": "admin",
  "password": "admin123"
}
```

**Backend signs the token with `JWT_SECRET_KEY`** (frontend never sees this!)
```python
# Backend code (auth.py)
access_token = jwt.encode(
    data={"sub": user['username']}, 
    SECRET_KEY,  # ← Secret key used here
    algorithm="HS256"
)
```

**Backend returns:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

### 2. Frontend Stores the Token

```javascript
// After successful login
const response = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const data = await response.json();

// Store the token
localStorage.setItem('token', data.access_token);  // ✅ Store token
localStorage.setItem('user', JSON.stringify(data.user));
```

### 3. Frontend Sends Token with Requests

```javascript
// Making authenticated request
const token = localStorage.getItem('token');

fetch('/api/dentists', {
  headers: {
    'Authorization': `Bearer ${token}`  // ✅ Send token (NOT the secret key!)
  }
});
```

**Backend verifies the token:**
```python
# Backend code
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # ← Uses secret key
```

## Frontend Example Code

### Complete Login Flow

```javascript
// Login function
async function login(username, password) {
  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    
    // Store token (NOT the secret key!)
    localStorage.setItem('authToken', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// Make authenticated request
async function getDentists() {
  const token = localStorage.getItem('authToken');
  
  const response = await fetch('/api/dentists', {
    headers: {
      'Authorization': `Bearer ${token}`  // Send token in header
    }
  });

  if (response.status === 401) {
    // Token expired or invalid
    localStorage.removeItem('authToken');
    // Redirect to login
    window.location.href = '/login';
    return;
  }

  return response.json();
}

// Logout
function logout() {
  localStorage.removeItem('authToken');
  localStorage.removeItem('user');
  window.location.href = '/login';
}
```

## Security Rules for Frontend

### ✅ DO

- ✅ Store JWT tokens in localStorage or sessionStorage
- ✅ Send tokens in `Authorization: Bearer <token>` header
- ✅ Validate token expiration on the frontend
- ✅ Handle 401 responses (token expired/invalid)
- ✅ Clear tokens on logout

### ❌ DON'T

- ❌ **NEVER send or store `JWT_SECRET_KEY`** (only backend has this!)
- ❌ Don't hardcode tokens in your code
- ❌ Don't share tokens in URLs or query parameters
- ❌ Don't log tokens to the console in production
- ❌ Don't send tokens to third-party services

## Token Lifecycle

```
┌─────────────┐
│   Frontend  │
│             │
│ 1. User     │  username/password
│    logs in  │ ──────────────────┐
│             │                    │
│ 2. Receive  │                    ▼
│    token    │ ◄─────────────────┐
│             │                    │
│ 3. Store    │                    │
│    token    │                    │
│             │                    │
│ 4. Send     │                    │
│    requests │  Authorization: Bearer <token>
│    with     │ ──────────────────┐
│    token    │                    ▼
│             │             ┌──────────────┐
└─────────────┘             │   Backend    │
                            │              │
                            │ 1. Validates │
                            │    password  │
                            │              │
                            │ 2. Signs     │
                            │    token with│
                            │    SECRET_KEY│
                            │              │
                            │ 3. Returns   │
                            │    token     │
                            │              │
                            │ 4. Verifies  │
                            │    token     │
                            │    with      │
                            │    SECRET_KEY│
                            └──────────────┘

Note: JWT_SECRET_KEY never leaves the backend!
```

## Common Frontend Token Storage

### Option 1: localStorage (Survives browser close)
```javascript
localStorage.setItem('token', token);
```

### Option 2: sessionStorage (Cleared when tab closes)
```javascript
sessionStorage.setItem('token', token);
```

### Option 3: Memory (Cleared on refresh)
```javascript
let token = data.access_token;  // In-memory variable
```

### Option 4: httpOnly Cookie (Most secure, but requires backend setup)
Backend sets cookie, frontend can't access via JavaScript.

## Handling Token Expiration

```javascript
// Check if token exists
function isAuthenticated() {
  return !!localStorage.getItem('authToken');
}

// Check if token is expired (frontend check)
function isTokenExpired() {
  const token = localStorage.getItem('authToken');
  if (!token) return true;
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    return Date.now() >= exp;
  } catch (e) {
    return true;
  }
}

// Protected route guard
function requireAuth() {
  if (!isAuthenticated() || isTokenExpired()) {
    window.location.href = '/login';
  }
}
```

## Summary

| Component | What It Does |
|-----------|-------------|
| **Frontend** | Requests login → Receives token → Stores token → Sends token with requests |
| **Backend** | Validates credentials → Signs token with SECRET_KEY → Verifies tokens with SECRET_KEY |
| **JWT_SECRET_KEY** | **Never exposed to frontend** - only used by backend |

## Key Takeaway

**The frontend NEVER sees or uses `JWT_SECRET_KEY`**. It only:
- Receives tokens from the backend
- Stores tokens (in localStorage/sessionStorage)
- Sends tokens with authenticated requests

The `JWT_SECRET_KEY` is a **backend secret** that signs and verifies tokens. The frontend only deals with the tokens themselves.
