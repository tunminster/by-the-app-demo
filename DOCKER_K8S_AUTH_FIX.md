# Docker/Kubernetes Authentication Fix

## Problem
401 errors when logging in via Docker containers or Kubernetes, even though login works locally.

## Root Cause
The `JWT_SECRET_KEY` environment variable was missing in Docker and Kubernetes configurations. This caused JWT token validation to fail between local (which used the default secret) and containerized environments.

## Solution

### 1. `.env` File
Added `JWT_SECRET_KEY` to your `.env` file:

```bash
JWT_SECRET_KEY=your-secret-key-change-this-in-production
```

### 2. Docker Compose
Updated `docker-compose.yml` to pass `JWT_SECRET_KEY` to containers:

```yaml
environment:
  - JWT_SECRET_KEY=${JWT_SECRET_KEY:-your-secret-key-change-this-in-production}
```

### 3. Kubernetes Deployment
Updated `manifests/deployment.yml` to include `JWT_SECRET_KEY`:

```yaml
- name: JWT_SECRET_KEY
  value: "#{jwt-secret-key}#"
```

## Deployment Steps

### Docker Compose
```bash
# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Kubernetes
Update your Azure Pipeline variables to include:
- Variable name: `jwt-secret-key`
- Value: (use the same value as in your `.env` file, or generate a secure random string)

Then redeploy:
```bash
# Your Azure Pipeline will handle the deployment
# with the updated #{jwt-secret-key}# variable
```

## Security Recommendation

⚠️ **Important**: For production, generate a secure random secret:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Update both `.env` and your Kubernetes secrets with this value.

## Verification

After deployment, test authentication:

```bash
# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

You should receive a valid JWT token instead of a 401 error.
