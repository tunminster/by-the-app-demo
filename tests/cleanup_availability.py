#!/usr/bin/env python3
"""
Quick cleanup script for availability test data
"""

import sys
import os
from os import getenv
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = getenv("API_BASE_URL", "http://localhost:8080")
if not API_BASE_URL.startswith("http"):
    API_BASE_URL = f"http://{API_BASE_URL}"

def cleanup():
    """Clean up availability test data"""
    print("Cleaning up availability test data...")
    
    # Get token
    login_url = f"{API_BASE_URL}/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code != 200:
            print("❌ Failed to authenticate")
            return
        token = response.json().get("access_token")
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return
    
    # Get all availability for dentist 11
    url = f"{API_BASE_URL}/api/availability"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"dentist_id": 11}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()
            print(f"Found {len(results)} availability record(s) for dentist 11")
            
            for result in results:
                availability_id = result.get('id')
                date = result.get('date')
                delete_url = f"{API_BASE_URL}/api/availability/{availability_id}"
                requests.delete(delete_url, headers=headers)
                print(f"   ✅ Deleted: ID {availability_id}, Date {date}")
            
            print(f"\n✅ Cleanup complete: {len(results)} record(s) deleted")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup()

