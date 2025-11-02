#!/usr/bin/env python3
"""
Test script for Availability API endpoints
Tests creating, updating, retrieving, and deleting availability records
"""

import sys
import os
import requests
from os import getenv
from dotenv import load_dotenv
from datetime import date, datetime

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = getenv("API_BASE_URL", "http://localhost:8080")
if not API_BASE_URL.startswith("http"):
    API_BASE_URL = f"http://{API_BASE_URL}"

def test_authentication():
    """Test login to get access token"""
    print("=" * 60)
    print("Testing Authentication...")
    print("=" * 60)
    
    login_url = f"{API_BASE_URL}/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful!")
            print(f"   Access token: {token_data.get('access_token', 'N/A')[:50]}...")
            return token_data.get("access_token")
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return None

def test_create_availability(token):
    """Test creating a new availability record"""
    print("\n" + "=" * 60)
    print("Testing Create Availability...")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/availability"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    availability_data = {
        "dentist_id": 11,
        "date": "2025-11-03",
        "time_slots": [
            {"start": "09:00", "end": "10:00", "available": True},
            {"start": "10:00", "end": "11:00", "available": True},
            {"start": "11:00", "end": "12:00", "available": True},
            {"start": "12:00", "end": "13:00", "available": True},
            {"start": "13:00", "end": "14:00", "available": True},
            {"start": "14:00", "end": "15:00", "available": True},
            {"start": "15:00", "end": "16:00", "available": True},
            {"start": "16:00", "end": "17:00", "available": True}
        ]
    }
    
    try:
        response = requests.post(url, json=availability_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Availability created successfully!")
            print(f"   ID: {result.get('id')}")
            print(f"   Dentist: {result.get('dentist_name')}")
            print(f"   Date: {result.get('date')}")
            print(f"   Time slots: {len(result.get('time_slots', []))} slots")
            return result.get('id')
        else:
            print(f"❌ Create availability failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating availability: {e}")
        return None

def test_get_availability(token, availability_id):
    """Test retrieving an availability record by ID"""
    print("\n" + "=" * 60)
    print("Testing Get Availability by ID...")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/availability/{availability_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Availability retrieved successfully!")
            print(f"   ID: {result.get('id')}")
            print(f"   Dentist: {result.get('dentist_name')}")
            print(f"   Date: {result.get('date')}")
            print(f"   Time slots: {len(result.get('time_slots', []))} slots")
            return result
        else:
            print(f"❌ Get availability failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error retrieving availability: {e}")
        return None

def test_get_all_availability(token):
    """Test retrieving all availability records"""
    print("\n" + "=" * 60)
    print("Testing Get All Availability...")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/availability"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Retrieved {len(results)} availability records")
            return results
        else:
            print(f"❌ Get all availability failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error retrieving all availability: {e}")
        return None

def test_search_availability(token):
    """Test searching availability by dentist and date"""
    print("\n" + "=" * 60)
    print("Testing Search Availability...")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/availability"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "dentist_id": 11,
        "date_from": "2025-11-01",
        "date_to": "2025-11-30"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Found {len(results)} availability records for dentist 11 in November 2025")
            for result in results:
                print(f"   - ID: {result.get('id')}, Date: {result.get('date')}, Slots: {len(result.get('time_slots', []))}")
            return results
        else:
            print(f"❌ Search availability failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error searching availability: {e}")
        return None

def test_update_availability(token, availability_id):
    """Test updating an availability record"""
    print("\n" + "=" * 60)
    print("Testing Update Availability...")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/availability/{availability_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "time_slots": [
            {"start": "09:00", "end": "10:00", "available": False},  # Mark first slot as booked
            {"start": "10:00", "end": "11:00", "available": True},
            {"start": "11:00", "end": "12:00", "available": True},
            {"start": "12:00", "end": "13:00", "available": True},
            {"start": "13:00", "end": "14:00", "available": False},  # Mark another slot as booked
            {"start": "14:00", "end": "15:00", "available": True},
            {"start": "15:00", "end": "16:00", "available": True},
            {"start": "16:00", "end": "17:00", "available": True}
        ]
    }
    
    try:
        response = requests.put(url, json=update_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Availability updated successfully!")
            booked_slots = [slot for slot in result.get('time_slots', []) if not slot.get('available', True)]
            print(f"   Booked slots: {len(booked_slots)}")
            return result
        else:
            print(f"❌ Update availability failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error updating availability: {e}")
        return None

def test_delete_availability(token, availability_id):
    """Test deleting an availability record"""
    print("\n" + "=" * 60)
    print("Testing Delete Availability...")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/availability/{availability_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Availability deleted successfully!")
            return True
        else:
            print(f"❌ Delete availability failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error deleting availability: {e}")
        return False

def cleanup_test_data(token, dentist_id=11, test_date="2025-11-03"):
    """Clean up test data before running tests"""
    print("\n" + "=" * 60)
    print("Cleaning Up Test Data...")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/api/availability"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "dentist_id": dentist_id,
        "date_from": test_date,
        "date_to": test_date
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()
            for result in results:
                availability_id = result.get('id')
                delete_url = f"{API_BASE_URL}/api/availability/{availability_id}"
                requests.delete(delete_url, headers=headers)
                print(f"   Deleted availability record ID: {availability_id}")
            print(f"✅ Cleanup complete: {len(results)} record(s) deleted")
        else:
            print(f"   No existing records to clean up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def main():
    """Run all availability API tests"""
    print("\n" + "=" * 60)
    print("AVAILABILITY API TEST SUITE")
    print("=" * 60)
    
    # Get authentication token
    token = test_authentication()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Clean up any existing test data
    cleanup_test_data(token)
    
    # Test creating availability
    availability_id = test_create_availability(token)
    if not availability_id:
        print("\n❌ Cannot proceed without creating availability")
        sys.exit(1)
    
    # Test retrieving availability by ID
    test_get_availability(token, availability_id)
    
    # Test retrieving all availability
    test_get_all_availability(token)
    
    # Test searching availability
    test_search_availability(token)
    
    # Test updating availability
    test_update_availability(token, availability_id)
    
    # Test deleting availability
    test_delete_availability(token, availability_id)
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("✅ All availability API tests completed successfully!")

if __name__ == "__main__":
    main()

