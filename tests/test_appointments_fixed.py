#!/usr/bin/env python3
"""
Test appointments API after fixing field mapping
"""

import requests
import json

API_BASE = "http://localhost:8080"

def test_appointments_api():
    """Test the appointments API endpoints"""
    
    print("="*70)
    print("Testing Appointments API (Fixed Version)")
    print("="*70)
    
    # Step 1: Login to get token
    print("\n1. Logging in to get authentication token...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('access_token')
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test GET /api/appointments
    print("\n2. Testing GET /api/appointments...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/api/appointments", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Appointments endpoint working!")
            print(f"Found {len(data)} appointments")
            
            if data:
                print("\nSample appointment:")
                sample = data[0]
                print(f"  ID: {sample.get('id')}")
                print(f"  Patient: {sample.get('patient')}")
                print(f"  Date: {sample.get('appointment_date')}")
                print(f"  Time: {sample.get('appointment_time')}")
                print(f"  Treatment: {sample.get('treatment')}")
                print(f"  Status: {sample.get('status')}")
                print(f"  Dentist: {sample.get('dentist_name')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 3: Test GET /api/appointments/statuses
    print("\n3. Testing GET /api/appointments/statuses...")
    try:
        response = requests.get(f"{API_BASE}/api/appointments/statuses")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Statuses endpoint working!")
            print(f"Available statuses: {data.get('statuses', [])}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 4: Test creating a new appointment
    print("\n4. Testing POST /api/appointments (create new appointment)...")
    try:
        new_appointment = {
            "patient": "Test Patient",
            "phone": "(555) 999-8888",
            "dentist_id": 1,
            "appointment_date": "2025-12-01",
            "appointment_time": "14:00",
            "treatment": "Test Treatment",
            "status": "confirmed",
            "notes": "Test appointment"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_BASE}/api/appointments", 
                               json=new_appointment, 
                               headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Create appointment working!")
            print(f"Created appointment ID: {data.get('id')}")
            print(f"Patient: {data.get('patient')}")
            print(f"Date: {data.get('appointment_date')}")
            print(f"Time: {data.get('appointment_time')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_appointments_api()
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
