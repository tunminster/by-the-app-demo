#!/usr/bin/env python3
"""
Test refresh token functionality
"""

import requests
import json
import time

API_BASE = "http://localhost:8080"

def test_refresh_token():
    """Test the refresh token endpoint"""
    
    print("="*70)
    print("Testing Refresh Token Functionality")
    print("="*70)
    
    # Step 1: Login to get access and refresh tokens
    print("\n1. Logging in to get tokens...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            print("✅ Login successful")
            print(f"Access token: {access_token[:50]}...")
            print(f"Refresh token: {refresh_token[:50]}...")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test using access token
    print("\n2. Testing access token...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Access token working")
            print(f"User: {user_data.get('username')} ({user_data.get('role')})")
        else:
            print(f"❌ Access token failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Access token error: {e}")
    
    # Step 3: Test refresh token
    print("\n3. Testing refresh token...")
    try:
        refresh_data = {
            "refresh_token": refresh_token
        }
        refresh_response = requests.post(f"{API_BASE}/auth/refresh", json=refresh_data)
        
        if refresh_response.status_code == 200:
            new_token_data = refresh_response.json()
            new_access_token = new_token_data.get('access_token')
            new_refresh_token = new_token_data.get('refresh_token')
            print("✅ Refresh token working")
            print(f"New access token: {new_access_token[:50]}...")
            print(f"New refresh token: {new_refresh_token[:50]}...")
            
            # Verify the new access token works
            print("\n4. Testing new access token...")
            headers = {"Authorization": f"Bearer {new_access_token}"}
            response = requests.get(f"{API_BASE}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ New access token working")
                print(f"User: {user_data.get('username')} ({user_data.get('role')})")
            else:
                print(f"❌ New access token failed: {response.text}")
                
        else:
            print(f"❌ Refresh token failed: {refresh_response.text}")
            
    except Exception as e:
        print(f"❌ Refresh token error: {e}")
    
    # Step 5: Test invalid refresh token
    print("\n5. Testing invalid refresh token...")
    try:
        invalid_refresh_data = {
            "refresh_token": "invalid_token_here"
        }
        invalid_response = requests.post(f"{API_BASE}/auth/refresh", json=invalid_refresh_data)
        
        if invalid_response.status_code == 401:
            print("✅ Invalid refresh token correctly rejected")
        else:
            print(f"❌ Invalid refresh token should be rejected: {invalid_response.text}")
            
    except Exception as e:
        print(f"❌ Invalid refresh token test error: {e}")

def test_token_expiration():
    """Test token expiration behavior"""
    print("\n" + "="*70)
    print("Testing Token Expiration")
    print("="*70)
    
    # Note: In a real scenario, you'd wait for the token to expire
    # For this test, we'll just show the token structure
    print("\nToken expiration times:")
    print(f"Access token: {30} minutes")
    print(f"Refresh token: {7} days")
    print("\nNote: In production, frontend should refresh tokens before they expire")

if __name__ == "__main__":
    test_refresh_token()
    test_token_expiration()
    
    print("\n" + "="*70)
    print("Refresh Token Test Complete")
    print("="*70)
    
    print("\nFrontend Usage Example:")
    print("""
    // Login
    const loginResponse = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'admin123' })
    });
    const { access_token, refresh_token } = await loginResponse.json();
    
    // Store tokens
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    // Refresh token when access token expires
    const refreshResponse = await fetch('/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh_token })
    });
    const { access_token: new_access_token, refresh_token: new_refresh_token } = await refreshResponse.json();
    
    // Update stored tokens
    localStorage.setItem('access_token', new_access_token);
    localStorage.setItem('refresh_token', new_refresh_token);
    """)
