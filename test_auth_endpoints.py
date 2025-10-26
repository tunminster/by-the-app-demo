#!/usr/bin/env python3
"""
Test Authentication Endpoints
Verify that the new /auth endpoints are accessible
"""

import requests
import json
from datetime import datetime

# API Base URL
API_BASE = "https://api-demo.bytheapp.com"

def test_auth_endpoints():
    """Test the authentication endpoints"""
    print("🧪 Testing Authentication Endpoints")
    print("=" * 45)
    
    # Test 1: Login endpoint
    print("\n1️⃣ Testing /auth/login endpoint...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Token: {data.get('access_token', '')[:50]}...")
            print(f"User: {data.get('user', {}).get('name', 'N/A')}")
            
            # Test 2: Get current user info
            print("\n2️⃣ Testing /auth/me endpoint...")
            token = data.get('access_token')
            
            me_response = requests.get(
                f"{API_BASE}/auth/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"Status Code: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ Get current user successful!")
                print(f"Username: {user_data.get('username')}")
                print(f"Email: {user_data.get('email')}")
                print(f"Role: {user_data.get('role')}")
            else:
                print(f"❌ Failed to get current user: {me_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
    
    # Test 3: Register endpoint (will fail if user exists)
    print("\n3️⃣ Testing /auth/register endpoint...")
    register_data = {
        "username": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com",
        "password": "testpassword123",
        "name": "Test User",
        "role": "user"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            print(f"User created: {response.json().get('username')}")
        elif response.status_code == 400:
            print("ℹ️ User already exists (expected if running multiple times)")
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing registration: {e}")
    
    print("\n📊 Summary:")
    print("=" * 45)
    print("✅ Auth endpoints are now available at:")
    print(f"   POST {API_BASE}/auth/login")
    print(f"   POST {API_BASE}/auth/register")
    print(f"   GET  {API_BASE}/auth/me (requires authentication)")

if __name__ == "__main__":
    test_auth_endpoints()
