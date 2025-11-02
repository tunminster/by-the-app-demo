# Refresh Token API

## Overview

Added refresh token functionality to the authentication system. This allows the frontend to get new access tokens without requiring users to log in again.

## New Endpoint

### POST /auth/refresh

**Description:** Refresh access token using a refresh token

**Request Body:**
```json
{
  "refresh_token": "your_refresh_token_here"
}
```

**Response:**
```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token", 
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin",
    "is_active": true,
    "last_login": "2025-10-26T10:30:00Z",
    "created_at": "2025-10-25T08:00:00Z",
    "updated_at": "2025-10-26T10:30:00Z"
  }
}
```

## Updated Login Response

The `/auth/login` endpoint now returns both access and refresh tokens:

```json
{
  "access_token": "access_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "name": "Admin User",
    "role": "admin",
    "is_active": true,
    "last_login": "2025-10-26T10:30:00Z",
    "created_at": "2025-10-25T08:00:00Z",
    "updated_at": "2025-10-26T10:30:00Z"
  }
}
```

## Token Expiration

- **Access Token:** 30 minutes
- **Refresh Token:** 7 days

## Security Features

1. **Token Type Validation:** Tokens include a `type` field to distinguish between access and refresh tokens
2. **User Validation:** Refresh token validates that the user still exists and is active
3. **Token Rotation:** Each refresh generates a new refresh token (old one becomes invalid)
4. **Secure Storage:** Frontend should store refresh tokens securely

## Frontend Implementation

### JavaScript Example

```javascript
class AuthService {
  constructor() {
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  async login(username, password) {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      
      localStorage.setItem('access_token', this.accessToken);
      localStorage.setItem('refresh_token', this.refreshToken);
      
      return data.user;
    }
    throw new Error('Login failed');
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch('/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: this.refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      this.accessToken = data.access_token;
      this.refreshToken = data.refresh_token;
      
      localStorage.setItem('access_token', this.accessToken);
      localStorage.setItem('refresh_token', this.refreshToken);
      
      return this.accessToken;
    }
    throw new Error('Token refresh failed');
  }

  async makeAuthenticatedRequest(url, options = {}) {
    let response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${this.accessToken}`
      }
    });

    // If token expired, try to refresh
    if (response.status === 401) {
      try {
        await this.refreshAccessToken();
        // Retry the request with new token
        response = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${this.accessToken}`
          }
        });
      } catch (error) {
        // Refresh failed, redirect to login
        this.logout();
        throw error;
      }
    }

    return response;
  }

  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
}

// Usage
const auth = new AuthService();

// Login
await auth.login('admin', 'admin123');

// Make authenticated requests
const response = await auth.makeAuthenticatedRequest('/api/appointments');
```

### React Hook Example

```javascript
import { useState, useEffect, useCallback } from 'react';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = useCallback(async (username, password) => {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      setUser(data.user);
      return data.user;
    }
    throw new Error('Login failed');
  }, []);

  const refreshToken = useCallback(async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return null;

    const response = await fetch('/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return data.access_token;
    }
    return null;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  }, []);

  useEffect(() => {
    // Check if user is logged in on app start
    const token = localStorage.getItem('access_token');
    if (token) {
      // Verify token is still valid
      fetch('/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          // Token expired, try to refresh
          return refreshToken();
        }
      })
      .then(userData => {
        if (userData) setUser(userData);
        setLoading(false);
      })
      .catch(() => {
        logout();
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, [refreshToken, logout]);

  return { user, login, logout, refreshToken, loading };
};
```

## Testing

Run the test script to verify refresh token functionality:

```bash
python test_refresh_token.py
```

This will test:
1. ✅ Login and get tokens
2. ✅ Use access token
3. ✅ Refresh token
4. ✅ Use new access token
5. ✅ Invalid refresh token rejection

## Error Handling

### Common Errors

1. **401 Unauthorized** - Invalid or expired refresh token
2. **500 Internal Server Error** - Server-side error during token refresh

### Error Response Format

```json
{
  "detail": "Invalid refresh token"
}
```

## Security Considerations

1. **Store refresh tokens securely** - Use httpOnly cookies in production
2. **Implement token rotation** - Each refresh generates new tokens
3. **Monitor token usage** - Log refresh attempts for security monitoring
4. **Set appropriate expiration times** - Balance security vs user experience
5. **Handle token revocation** - Implement logout to invalidate tokens

## Production Recommendations

1. **Use HTTPS** - Always use secure connections
2. **Implement rate limiting** - Prevent token refresh abuse
3. **Add token blacklisting** - For immediate token revocation
4. **Monitor suspicious activity** - Track unusual refresh patterns
5. **Consider shorter expiration times** - For high-security applications
