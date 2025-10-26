#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify and Fix Admin Password
This script checks the current password hash and updates it if needed
"""

from passlib.context import CryptContext
from app.utils.db import conn
from psycopg2.extras import RealDictCursor

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_and_fix_admin_password():
    """Check current password hash and fix if needed"""
    
    # Get current admin user
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT username, password_hash FROM users WHERE username = 'admin'")
        user = cur.fetchone()
        
        if not user:
            print("❌ Admin user not found in database")
            return False
        
        current_hash = user['password_hash']
        print(f"Current password hash: {current_hash}")
        
        # Test if current hash works with "admin123"
        try:
            is_valid = pwd_context.verify("admin123", current_hash)
            print(f"✅ Current password hash is valid for 'admin123': {is_valid}")
            
            if is_valid:
                print("✅ Password is correct! No need to update.")
                return True
            else:
                print("❌ Current password hash does not work with 'admin123'")
                print("   Updating to new hash...")
                
        except Exception as e:
            print(f"❌ Error verifying current hash: {e}")
            print("   Updating to new hash...")
        
        # Generate new hash
        new_hash = pwd_context.hash("admin123")
        print(f"New password hash: {new_hash}")
        
        # Update in database
        cur.execute("""
            UPDATE users 
            SET password_hash = %s, updated_at = NOW()
            WHERE username = 'admin'
            RETURNING username, email, name
        """, (new_hash,))
        
        result = cur.fetchone()
        if result:
            print("✅ Password hash updated successfully!")
            print(f"Username: {result['username']}")
            print(f"Email: {result['email']}")
            print(f"Name: {result['name']}")
            
            # Verify the new hash works
            print("\n🔍 Verifying new hash...")
            is_valid = pwd_context.verify("admin123", new_hash)
            print(f"✅ New hash works: {is_valid}")
            return True
        else:
            print("❌ Failed to update password")
            return False

if __name__ == "__main__":
    print("🔐 Verify and Fix Admin Password")
    print("=" * 50)
    check_and_fix_admin_password()
    print("=" * 50)
