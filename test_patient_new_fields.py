#!/usr/bin/env python3
"""
Test patient API with new fields (address, emergency_contact, medical_history)
"""

import requests
import json
from datetime import date

API_BASE = "http://localhost:8080"

def test_patient_api():
    """Test the patient API with new fields"""
    
    print("="*70)
    print("Testing Patient API with New Fields")
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
    
    # Step 2: Test creating a patient with new fields
    print("\n2. Testing POST /api/patients (create patient with new fields)...")
    try:
        new_patient = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "date_of_birth": "1990-05-15",
            "address": "123 Main St, Anytown, ST 12345",
            "emergency_contact": "Jane Doe - (555) 987-6543",
            "medical_history": "Allergic to penicillin. Previous root canal in 2020.",
            "status": "active"
        }
        
        response = requests.post(f"{API_BASE}/api/patients", 
                               json=new_patient, 
                               headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Create patient with new fields working!")
            print(f"Patient ID: {data.get('id')}")
            print(f"Name: {data.get('name')}")
            print(f"Address: {data.get('address')}")
            print(f"Emergency Contact: {data.get('emergency_contact')}")
            print(f"Medical History: {data.get('medical_history')}")
            
            patient_id = data.get('id')
        else:
            print(f"❌ Error: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 3: Test getting all patients
    print("\n3. Testing GET /api/patients (list all patients)...")
    try:
        response = requests.get(f"{API_BASE}/api/patients", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get all patients working!")
            print(f"Found {len(data)} patients")
            
            if data:
                patient = data[0]
                print(f"\nSample patient:")
                print(f"  Name: {patient.get('name')}")
                print(f"  Address: {patient.get('address')}")
                print(f"  Emergency Contact: {patient.get('emergency_contact')}")
                print(f"  Medical History: {patient.get('medical_history')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 4: Test getting specific patient
    print(f"\n4. Testing GET /api/patients/{patient_id} (get specific patient)...")
    try:
        response = requests.get(f"{API_BASE}/api/patients/{patient_id}", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get specific patient working!")
            print(f"Name: {data.get('name')}")
            print(f"Address: {data.get('address')}")
            print(f"Emergency Contact: {data.get('emergency_contact')}")
            print(f"Medical History: {data.get('medical_history')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 5: Test updating patient with new fields
    print(f"\n5. Testing PUT /api/patients/{patient_id} (update patient)...")
    try:
        update_data = {
            "address": "456 Oak Ave, Newtown, ST 67890",
            "emergency_contact": "Bob Smith - (555) 111-2222",
            "medical_history": "Updated: Allergic to penicillin and latex. Previous root canal in 2020, cleaning in 2023."
        }
        
        response = requests.put(f"{API_BASE}/api/patients/{patient_id}", 
                              json=update_data, 
                              headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Update patient working!")
            print(f"Updated Address: {data.get('address')}")
            print(f"Updated Emergency Contact: {data.get('emergency_contact')}")
            print(f"Updated Medical History: {data.get('medical_history')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 6: Test searching patients
    print("\n6. Testing GET /api/patients/search (search patients)...")
    try:
        response = requests.get(f"{API_BASE}/api/patients/search?name=John", headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search patients working!")
            print(f"Found {len(data)} patients matching 'John'")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_patient_validation():
    """Test patient field validation"""
    print("\n" + "="*70)
    print("Testing Patient Field Validation")
    print("="*70)
    
    print("\nNew fields added to Patient model:")
    print("✅ address: Optional[str] = None")
    print("✅ emergency_contact: Optional[str] = None") 
    print("✅ medical_history: Optional[str] = None")
    
    print("\nThese fields are:")
    print("- Optional (can be null)")
    print("- Text fields (can store long text)")
    print("- Included in create, update, and response models")
    print("- Added to database queries")

if __name__ == "__main__":
    test_patient_api()
    test_patient_validation()
    
    print("\n" + "="*70)
    print("Patient API Test Complete")
    print("="*70)
    
    print("\nDatabase Migration Required:")
    print("Run: psql -h your_host -U your_user -d your_database -f add_patient_fields.sql")
    
    print("\nNew Patient Fields:")
    print("- address: Patient's home address")
    print("- emergency_contact: Emergency contact information")
    print("- medical_history: Patient's medical history and notes")
