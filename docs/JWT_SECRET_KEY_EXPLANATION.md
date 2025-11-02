# JWT_SECRET_KEY Explained

## What is JWT_SECRET_KEY?

`JWT_SECRET_KEY` is a secret cryptographic key used to **sign and verify** JWT (JSON Web Token) tokens in your authentication system.

## What It Does

### 1. **Signing Tokens** (When User Logs In)

When a user successfully logs in (line 203 in `auth.py`):

```python
access_token = create_access_token(data={"sub": user['username']})
```

The token is **signed** using `JWT_SECRET_KEY`. This creates a digital signature that ensures:
- ✅ Token is authentic (not forged)
- ✅ Token hasn't been tampered with
- ✅ Token came from your server

### 2. **Verifying Tokens** (When User Makes Requests)

When a user makes an authenticated request, the token is **verified** using the same `JWT_SECRET_KEY`:

```python
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

This checks:
- ✅ Token signature is valid
- ✅ Token hasn't expired
- ✅ Token came from your server

## Security Importance

### Why It's Critical

**If someone steals your `JWT_SECRET_KEY`:**
- ⚠️ They can create fake tokens
- ⚠️ They can impersonate any user
- ⚠️ They can access protected endpoints

**If `JWT_SECRET_KEY` is weak:**
- ⚠️ Attackers can guess or brute-force it
- ⚠️ Your entire authentication system is compromised

### Why Different Environments Need Same Key

In your code (line 22 in `auth.py`):

```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
```

**The same `JWT_SECRET_KEY` must be used across:**
- ✅ Development environment
- ✅ Docker containers
- ✅ Kubernetes pods
- ✅ Any server that signs or verifies tokens

**Why?** Because:
- A token signed in development must be valid in Docker
- A token signed in one container must be valid in another
- Tokens need to work across your entire infrastructure

## How It's Used in Your Code

### 1. Creating Tokens

```python
def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).replace(microsecond=0) + dt.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # ← Uses SECRET_KEY
    return encoded_jwt
```

### 2. Verifying Tokens

```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # ← Uses SECRET_KEY
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    # ... rest of code
```

## Best Practices

### 1. Use Strong Secrets

**Bad:**
```bash
JWT_SECRET_KEY=secret123  # Too weak!
JWT_SECRET_KEY=admin  # Too weak!
```

**Good:**
```bash
JWT_SECRET_KEY=sk8dKj29mN3pQ7vX2zY9wR5uT8sL6fH4jK2nM9pQ3rT7vY
```

**Best (Generated):**
```python
import secrets
print(secrets.token_urlsafe(32))
# Output: 'k8dKj29mN3pQ7vX2zY9wR5uT8sL6fH4jK2nM9pQ3rT7vY12wE5rT9'
```

### 2. Keep It Secret

**Never:**
- ❌ Commit it to git
- ❌ Share it in chat/email
- ❌ Hardcode it in your application
- ❌ Expose it in logs

**Always:**
- ✅ Use environment variables
- ✅ Store in `.env` (and add to `.gitignore`)
- ✅ Use secret management (Azure Key Vault, AWS Secrets Manager)
- ✅ Use Kubernetes secrets (not in YAML files)

### 3. Use Different Keys for Different Environments

```bash
# Development
JWT_SECRET_KEY=dev_key_sk8dKj29mN3pQ7vX2zY9wR5uT8sL6fH4j

# Staging
JWT_SECRET_KEY=staging_key_X7zY9wR5uT8sL6fH4jK2nM9pQ3rT7vY12w

# Production
JWT_SECRET_KEY=prod_key_Y9wR5uT8sL6fH4jK2nM9pQ3rT7vY12wE5rT9
```

## In Your Project

### Current Setup

```yaml
# docker-compose.yml
- JWT_SECRET_KEY=${JWT_SECRET_KEY:-your-secret-key-change-this-in-production}

# manifests/deployment.yml
- name: JWT_SECRET_KEY
  value: "#{jwt-secret-key}#"
```

### Where It's Configured

1. **`.env` file** - For local development
2. **`docker-compose.yml`** - For Docker containers
3. **`manifests/deployment.yml`** - For Kubernetes
4. **Azure Pipeline variables** - For Kubernetes secret

### How to Update It

1. Generate a new secret:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. Update in all places:
   - Update `.env`
   - Update Azure Pipeline variable `jwt-secret-key`

3. **Warning:** All existing tokens become invalid after changing the key!

## Summary

| Aspect | Details |
|--------|---------|
| **Purpose** | Sign and verify JWT tokens |
| **Security** | Critical - keeps authentication secure |
| **Scope** | Must be same across all environments |
| **Best Practice** | Use 32+ character random string |
| **Storage** | Environment variables, secret managers |
| **Rotation** | Invalidates all existing tokens |

**Remember:** Treat `JWT_SECRET_KEY` like a master password - keep it secret, keep it strong!
