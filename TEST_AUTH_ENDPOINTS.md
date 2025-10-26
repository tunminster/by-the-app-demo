# Testing Authentication Endpoints

## Quick Start

### 1. Install Dependencies
```bash
pip install requests python-dotenv
```

### 2. Configure Environment (Optional)

Create a `.env` file in the project root:

```bash
# .env
API_BASE_URL=https://api-demo.bytheapp.com
```

If you don't create a `.env` file, the test will use the default URL: `https://api-demo.bytheapp.com`

### 3. Run the Test
```bash
python test_auth_endpoints.py
```

## What the Test Does

The test script performs the following checks:

### 1. Login Test
- Tests `POST /auth/login` endpoint
- Uses default credentials: `admin` / `admin123`
- Retrieves JWT access token

### 2. Get Current User Test
- Tests `GET /auth/me` endpoint
- Uses the token from the login test
- Verifies token authentication works

### 3. Register User Test
- Tests `POST /auth/register` endpoint
- Creates a new test user with unique timestamp
- Verifies registration flow

## Expected Output

```
🧪 Testing Authentication Endpoints
=============================================
🌐 API Base URL: https://api-demo.bytheapp.com
⚠️  Using default API URL (API_BASE_URL not set in .env)
💡 To use a different URL, create a .env file with:
   API_BASE_URL=https://your-api-url.com
=============================================

1️⃣ Testing /auth/login endpoint...
Status Code: 200
✅ Login successful!
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
User: System Administrator

2️⃣ Testing /auth/me endpoint...
Status Code: 200
✅ Get current user successful!
Username: admin
Email: admin@dentalcare.com
Role: admin

3️⃣ Testing /auth/register endpoint...
Status Code: 200
✅ Registration successful!
User created: test_user_20250126_143022

📊 Summary:
=============================================
✅ Auth endpoints are now available at:
   POST https://api-demo.bytheapp.com/auth/login
   POST https://api-demo.bytheapp.com/auth/register
   GET  https://api-demo.bytheapp.com/auth/me (requires authentication)
```

## Troubleshooting

### API_BASE_URL not being read from .env

**Problem:** The script is using the default URL even though you added `API_BASE_URL` to `.env`.

**Solution:**
1. Make sure the `.env` file is in the project root directory (same location as `test_auth_endpoints.py`)
2. Check that the `.env` file has the correct format:
   ```
   API_BASE_URL=https://api-demo.bytheapp.com
   ```
   or for local development:
   ```
   API_BASE_URL=http://localhost:8080
   ```
   or (without protocol, will default to http://):
   ```
   API_BASE_URL=localhost:8080
   ```
   (No spaces around the `=` sign, no quotes needed)
3. Verify that `python-dotenv` is installed:
   ```bash
   pip install python-dotenv
   ```

### Connection Adapter Error

**Problem:** Getting error `No connection adapters were found for 'localhost:8080/auth/login'`

**Solution:**
Add the protocol (`http://` or `https://`) to your API URL in `.env`:
```bash
API_BASE_URL=http://localhost:8080
```

The script will auto-add `http://` if missing, but it's better to be explicit.

### Connection Error

If you see connection errors:
- Check that the API server is running
- Verify the API URL is correct
- Check your network connection

### 401 Unauthorized

If you see authentication errors:
- Verify the default credentials (`admin` / `admin123`) exist in your database
- Check that the user account is active (`is_active: true`)
- Ensure your database connection is working

### 400 Bad Request on Registration

This is normal if you run the test multiple times - the test creates unique users but may occasionally get a duplicate username/email if run very quickly.

## Customizing the Test

### Change Default Credentials

Edit the login section in `test_auth_endpoints.py`:

```python
login_data = {
    "username": "your_username",
    "password": "your_password"
}
```

### Use Different API URL

Option 1: Create/Edit `.env` file:
```bash
API_BASE_URL=http://localhost:8080
```

Option 2: Edit the default in `test_auth_endpoints.py`:
```python
API_BASE = getenv("API_BASE_URL", "http://localhost:8080")
```

### Test Against Local Server

```bash
# In .env or directly in the script
API_BASE_URL=http://localhost:8080
```

## Files

- `test_auth_endpoints.py` - Main test script
- `.env` - Environment variables (create this file)
- `.env.example` - Example environment file (reference only)
