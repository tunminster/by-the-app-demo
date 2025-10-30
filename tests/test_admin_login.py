#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Admin Login
Debug why admin login is failing
"""

import requests
from passlib.context import CryptContext
from app.utils.db import conn
from psycopg2.extras import RealDictCursor

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_admin_login():
    """Test admin login and debug"""
    print("🔍 Testing Admin Login")
    print("=" * 50)
    
    # Step 1: Check what's in the database
    print("\n1️⃣ Checking database...")
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT username, email, password_hash, is_active, role FROM users WHERE username = 'admin'")
        user = cur.fetchone()
        
        if not user:
            print("❌ Admin user not found!")
            return False
        
        print("✓ Admin user found:")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   Is Active: {user['is_active']}")
        print(f"   Password Hash: {user['password_hash'][:30]}...")
        
        # Step 2: Test password verification locally
        print("\n2️⃣ Testing password verification...")
        try:
            is_valid = pwd_context.verify("admin123", user['password_hash'])
            print(f"   Password 'admin123' verified: {is_valid}")
            
            if not is_valid:
                print("   ❌ Password verification failed!")
                print("   🔄 Let's generate a new hash...")
                
                new_hash = pwd_context.hash("admin123")
                print(f"   New hash: {new_hash}")
                
                # Update in database
                cur.execute("""
                    UPDATE users 
                    SET password_hash = %s, updated_at = NOW()
                    WHERE username = 'admin'
                """, (new_hash,))
                
                print("   ✅ Password hash updated!")
                
                # Verify it works
                new_is_valid = pwd_context.verify("admin123", new_hash)
                print(f"   New hash verified: {new_is_valid}")
        
        except Exception as e:
            print(f"   ❌ Error verifying password: {e}")
            return False
        
        # Step 3: Test the login endpoint
        print("\n3️⃣ Testing login endpoint...")
        try:
            response = requests.post(
                'http://localhost:8080/auth/login',
                json={'username': 'admin', 'password': 'admin123'},
                timeout=5
            )
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                print("   ✅ Login successful!")
                print(f"   Token: {data.get('access_token', 'N/A')[:50]}...")
                return True
            else:
                print("   ❌ Login failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Error calling login endpoint: {e}")
            return False

if __name__ == "__main__":
    test_admin_login()
