# Reset Admin Password Guide

## Problem

You're getting this error:
```
Login failed: The password hash in the database was created with a password longer than 72 bytes
```

This means the admin password in your database was created with a password that exceeded bcrypt's 72-byte limit.

## Solution

### Step 1: Reset the Admin Password

Run the reset script:

```bash
python reset_admin_password.py
```

This will set the admin password to `AdminPass123!` (15 bytes, well within the limit).

Or specify your own password:

```bash
python reset_admin_password.py "YourSecurePassword123!"
```

**Important:** The password must be:
- At least 8 characters
- At most 72 bytes

### Step 2: Update Your Test Script

Edit `test_auth_endpoints.py` and update the password:

```python
login_data = {
    "username": "admin",
    "password": "AdminPass123!"  # Updated password
}
```

### Step 3: Run the Test

```bash
python test_auth_endpoints.py
```

## Why Did This Happen?

1. bcrypt has a 72-byte limit for passwords
2. The admin password in your database was created with a password > 72 bytes
3. You're now trying to login with `admin123` (8 bytes)
4. bcrypt can't verify it because the hash was created with a longer password

## Verification

After running the reset script, you should see:

```
✅ Admin password reset successfully!
Username: admin
Email: admin@dentalcare.com
Name: System Administrator
```

And in the test output:

```
✅ Login successful!
```

## Alternative: Create a New Admin Account

If you prefer to create a new admin account instead:

```python
# In Python console or script
from app.routes.auth import register_user, UserRegister

new_admin = UserRegister(
    username="newadmin",
    email="newadmin@example.com",
    password="SecurePass123!",
    name="New Administrator",
    role="admin"
)

# This will create an inactive user
# Then manually activate it in the database or use the user management API
```

## Troubleshooting

### Error: "Admin user not found"

Make sure you have an admin user in the database. Check:

```sql
SELECT username, email, role FROM users WHERE username = 'admin';
```

### Error: "Password is too long"

Use a shorter password:

```bash
python reset_admin_password.py "ShortPass123"
```

### Still can't login

Check the server logs for the debug messages:
```
⚠️  Password verification failed: Hash was created with password > 72 bytes
⚠️  Attempted password length: 8 characters, 8 bytes
```

If you see this, the password has been reset successfully in the database, and you just need to use the new password in your test.
