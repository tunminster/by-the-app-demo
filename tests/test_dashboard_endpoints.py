#!/usr/bin/env python3
"""
Test dashboard endpoints
"""

import requests
from datetime import datetime
import json

API_BASE = "http://localhost:8080"  # or your API URL

def test_dashboard_stats():
    """Test /api/dashboard/stats endpoint"""
    print("\n" + "="*70)
    print("Testing /api/dashboard/stats")
    print("="*70)
    
    try:
        url = f"{API_BASE}/api/dashboard/stats"
        response = requests.get(url)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            # Validate structure
            if 'stats' in data and isinstance(data['stats'], list):
                print("\n✅ Response structure is correct")
                print(f"✅ Found {len(data['stats'])} stats")
                
                for stat in data['stats']:
                    print(f"  - {stat['name']}: {stat['value']} ({stat['change']})")
            else:
                print("❌ Response structure is incorrect")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_today_appointments():
    """Test /api/dashboard/appointments/today endpoint"""
    print("\n" + "="*70)
    print("Testing /api/dashboard/appointments/today")
    print("="*70)
    
    try:
        url = f"{API_BASE}/api/dashboard/appointments/today"
        response = requests.get(url)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse:")
            print(json.dumps(data, indent=2))
            
            # Validate structure
            if 'appointments' in data and isinstance(data['appointments'], list):
                print("\n✅ Response structure is correct")
                print(f"✅ Found {len(data['appointments'])} appointments")
                
                for apt in data['appointments']:
                    print(f"  - {apt['time']}: {apt['patient']} - {apt['treatment']} ({apt['status']})")
            else:
                print("❌ Response structure is incorrect")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Dashboard Endpoints Test")
    print("="*70)
    print(f"API Base URL: {API_BASE}")
    
    test_dashboard_stats()
    test_today_appointments()
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
