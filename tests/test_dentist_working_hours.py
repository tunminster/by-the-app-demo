#!/usr/bin/env python3
"""
Test dentist API with new working_hours field
"""

import requests
import json

API_BASE = "http://localhost:8080"

def test_dentist_api():
    """Test the dentist API with new working_hours field"""
    
    print("="*70)
    print("Testing Dentist API with Working Hours")
    print("="*70)
    
    # Step 1: Login to get authentication token
    print("\n1. Logging in to get authentication token...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access_token')
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Test getting all dentists
    print("\n2. Testing GET /api/dentists (list all dentists)...")
    try:
        response = requests.get(f"{API_BASE}/api/dentists")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get all dentists working!")
            print(f"Found {len(data)} dentists")
            
            if data:
                dentist = data[0]
                print(f"\nSample dentist:")
                print(f"  ID: {dentist.get('id')}")
                print(f"  Name: {dentist.get('name')}")
                print(f"  Working Hours: {json.dumps(dentist.get('working_hours'), indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 3: Test creating a dentist with working hours
    print("\n3. Testing POST /api/dentists (create dentist with working hours)...")
    try:
        new_dentist = {
            "name": "Dr. Test Dentist",
            "specialty": "General Dentistry",
            "email": "test.dentist@example.com",
            "phone": "(555) 999-0000",
            "license": "DDS-TEST-001",
            "years_of_experience": 5,
            "working_days": "5 days/week",
            "working_hours": {
                "monday": {"start": "08:00", "end": "16:00"},
                "tuesday": {"start": "08:00", "end": "16:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "08:00", "end": "15:00"}
            }
        }
        
        response = requests.post(f"{API_BASE}/api/dentists", 
                               json=new_dentist, 
                               headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Create dentist with working hours working!")
            print(f"Dentist ID: {data.get('id')}")
            print(f"Working Hours: {json.dumps(data.get('working_hours'), indent=2)}")
            
            dentist_id = data.get('id')
        else:
            print(f"❌ Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 4: Test getting specific dentist
    print(f"\n4. Testing GET /api/dentists/{dentist_id} (get specific dentist)...")
    try:
        response = requests.get(f"{API_BASE}/api/dentists/{dentist_id}")
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get specific dentist working!")
            print(f"Name: {data.get('name')}")
            print(f"Working Hours: {json.dumps(data.get('working_hours'), indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 5: Test updating dentist with new working hours
    print(f"\n5. Testing PUT /api/dentists/{dentist_id} (update working hours)...")
    try:
        update_data = {
            "working_hours": {
                "monday": {"start": "07:00", "end": "15:00"},
                "tuesday": {"start": "07:00", "end": "15:00"},
                "wednesday": {"start": "08:00", "end": "16:00"},
                "thursday": {"start": "08:00", "end": "16:00"},
                "friday": {"start": "07:00", "end": "14:00"}
            }
        }
        
        response = requests.put(f"{API_BASE}/api/dentists/{dentist_id}", 
                              json=update_data, 
                              headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Update dentist working hours working!")
            print(f"Updated Working Hours: {json.dumps(data.get('working_hours'), indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_working_hours_design():
    """Display the working hours design"""
    print("\n" + "="*70)
    print("Working Hours Design")
    print("="*70)
    
    print("\n1. Data Structure:")
    print("   - Day names: monday, tuesday, wednesday, thursday, friday, saturday, sunday")
    print("   - Time format: HH:MM (24-hour format)")
    print("   - Storage: JSONB in PostgreSQL")
    
    print("\n2. Example Data:")
    example = {
        "monday": {"start": "09:00", "end": "17:00"},
        "tuesday": {"start": "09:00", "end": "17:00"},
        "wednesday": {"start": "09:00", "end": "17:00"},
        "thursday": {"start": "09:00", "end": "17:00"},
        "friday": {"start": "09:00", "end": "17:00"}
    }
    print(json.dumps(example, indent=2))
    
    print("\n3. Benefits:")
    print("   ✅ Flexible - Different hours for each day")
    print("   ✅ Searchable - GIN index on JSONB for fast queries")
    print("   ✅ Type-safe - Pydantic validation for time format")
    print("   ✅ Backward compatible - Optional field, existing data unaffected")
    
    print("\n4. Usage in API:")
    print("   - GET /api/dentists - Returns working hours for all dentists")
    print("   - POST /api/dentists - Accepts working_hours in request")
    print("   - PUT /api/dentists/{id} - Can update working_hours")
    print("   - GET /api/dentists/{id} - Returns working hours for specific dentist")

if __name__ == "__main__":
    test_dentist_api()
    show_working_hours_design()
    
    print("\n" + "="*70)
    print("Dentist Working Hours Test Complete")
    print("="*70)
    
    print("\nDatabase Migration Required:")
    print("Run: psql -h your_host -U your_user -d your_database -f add_dentist_working_hours.sql")
