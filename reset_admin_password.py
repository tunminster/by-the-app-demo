#!/usr/bin/env python3
"""
Reset Admin Password
This script resets the admin password to a new valid password
"""

import sys
from passlib.context import CryptContext
from app.utils.db import conn

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_admin_password(new_password: str):
    """Reset the admin user's password"""
    # Validate new password
    password_bytes = len(new_password.encode('utf-8'))
    if password_bytes > 72:
        print(f"❌ Error: Password is {password_bytes} bytes. Must be <= 72 bytes")
        return False
    
    if len(new_password) < 8:
        print("❌ Error: Password must be at least 8 characters")
        return False
    
    # Hash the new password
    hashed_password = pwd_context.hash(new_password)
    
    # Update in database
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE users 
                SET password_hash = %s, updated_at = NOW()
                WHERE username = 'admin'
                RETURNING username, email, name
            """, (hashed_password,))
            
            result = cur.fetchone()
            if result:
                print("✅ Admin password reset successfully!")
                print(f"Username: {result[0]}")
                print(f"Email: {result[1]}")
                print(f"Name: {result[2]}")
                return True
            else:
                print("❌ Admin user not found")
                return False
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False

if __name__ == "__main__":
    # Default new password
    new_password = "AdminPass123!"
    
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
    
    print("🔐 Reset Admin Password")
    print("=" * 40)
    print(f"New password: {new_password}")
    print(f"Length: {len(new_password)} characters")
    print(f"Bytes: {len(new_password.encode('utf-8'))} bytes")
    print("=" * 40)
    
    if reset_admin_password(new_password):
        print("\n✅ Success! You can now login with:")
        print(f"   Username: admin")
        print(f"   Password: {new_password}")
    else:
        print("\n❌ Failed to reset password")
        sys.exit(1)
