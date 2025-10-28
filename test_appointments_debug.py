#!/usr/bin/env python3
"""
Debug appointments API issues
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8080"

def test_appointments_endpoints():
    """Test appointments endpoints to identify 500 errors"""
    
    print("="*70)
    print("Testing Appointments API Endpoints")
    print("="*70)
    
    # Test 1: Get all appointments (requires auth)
    print("\n1. Testing GET /api/appointments (requires auth)")
    try:
        response = requests.get(f"{API_BASE}/api/appointments")
        print(f"Status: {response.status_code}")
        if response.status_code == 500:
            print("❌ 500 Error - likely authentication or database issue")
            print(f"Error: {response.text}")
        elif response.status_code == 401:
            print("✅ 401 Unauthorized - authentication working, need token")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 2: Get appointment statuses (no auth required)
    print("\n2. Testing GET /api/appointments/statuses")
    try:
        response = requests.get(f"{API_BASE}/api/appointments/statuses")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Endpoint working")
            data = response.json()
            print(f"Statuses: {data.get('statuses', [])}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 3: Test with a simple auth token (if available)
    print("\n3. Testing with authentication")
    try:
        # Try to login first to get a token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('access_token')
            
            if token:
                print("✅ Got auth token, testing appointments with auth")
                headers = {"Authorization": f"Bearer {token}"}
                
                response = requests.get(f"{API_BASE}/api/appointments", headers=headers)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Appointments endpoint working with auth")
                    data = response.json()
                    print(f"Found {len(data)} appointments")
                elif response.status_code == 500:
                    print("❌ Still getting 500 error with valid auth")
                    print(f"Error: {response.text}")
                else:
                    print(f"Response: {response.text[:200]}...")
            else:
                print("❌ No token in login response")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Auth test error: {e}")

def test_database_connection():
    """Test database connection directly"""
    print("\n" + "="*70)
    print("Testing Database Connection")
    print("="*70)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT', 5432)
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Test basic query
            cur.execute("SELECT COUNT(*) as count FROM appointments")
            result = cur.fetchone()
            print(f"✅ Database connection working")
            print(f"✅ Found {result['count']} appointments in database")
            
            # Check if created_at/updated_at columns exist
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'appointments' 
                AND column_name IN ('created_at', 'updated_at')
            """)
            timestamp_columns = cur.fetchall()
            
            if timestamp_columns:
                print("✅ created_at and updated_at columns exist")
            else:
                print("❌ Missing created_at and updated_at columns")
                
            # Test a simple appointment query
            cur.execute("""
                SELECT a.*, d.name as dentist_name
                FROM appointments a
                LEFT JOIN dentists d ON a.dentist_id = d.id
                LIMIT 1
            """)
            appointment = cur.fetchone()
            
            if appointment:
                print("✅ Appointment query working")
                print(f"Sample appointment: {appointment['patient']} - {appointment.get('dentist_name', 'No dentist')}")
            else:
                print("❌ No appointments found or query failed")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")

if __name__ == "__main__":
    test_appointments_endpoints()
    test_database_connection()
    
    print("\n" + "="*70)
    print("Debug Complete")
    print("="*70)
