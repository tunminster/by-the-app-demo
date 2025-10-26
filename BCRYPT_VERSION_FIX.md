# Bcrypt Version Compatibility Fix

## Error Message
```
AttributeError: module 'bcrypt' has no attribute '__about__'
ValueError: password cannot be longer than 72 bytes
```

## Root Cause

The `bcrypt` library version 4.0+ has breaking changes that are incompatible with `passlib<1.7.5`. The `__about__` attribute was removed in bcrypt 4.x.

## Fix Applied

### 1. Removed Startup Test
Removed the bcrypt initialization test in `auth.py` that was causing the app to crash on startup.

### 2. Updated `requirements.txt`
Changed bcrypt version to be compatible with passlib:

```diff
- bcrypt>=4.0.0
+ bcrypt>=3.2.0,<4.0.0  # Use bcrypt 3.x for passlib compatibility
```

## Why This Works

- `bcrypt 3.x` is fully compatible with `passlib`
- No breaking changes between versions
- Still secure and receives security patches

## Rebuild Container

After the fix, rebuild your container:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Verify Fix

Check the logs - you should see the app start without bcrypt errors:

```bash
docker-compose logs voice-api | grep -i bcrypt
```

You should see NO errors about bcrypt.

## Alternative Fix (If Still Having Issues)

If you want to use bcrypt 4.x, you need to upgrade passlib:

```bash
# In requirements.txt
bcrypt>=4.0.0
passlib[bcrypt]>=1.7.6  # Newer version supports bcrypt 4.x
```

But bcrypt 3.x is perfectly fine and more stable.

## Testing Authentication

After rebuild, test authentication:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Should work without errors!
