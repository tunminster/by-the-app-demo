#!/usr/bin/env python3
"""
Database Connection Tests
Tests PostgreSQL connection and basic operations
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.db import conn, fetch_dentists, find_patient_by_name

def test_db_connection():
    """Test database connection."""
    print("🔌 Testing Database Connection...")
    
    try:
        if conn.closed == 0:
            print("✅ Database connection: OK")
            return True
        else:
            print("❌ Database connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_fetch_dentists():
    """Test fetching dentists from database."""
    print("👨‍⚕️ Testing fetch_dentists()...")
    
    try:
        dentists = fetch_dentists()
        if dentists is not None:
            print(f"✅ Found {len(dentists)} dentists")
            if dentists:
                print(f"   First dentist: {dentists[0]}")
            return True
        else:
            print("❌ Failed to fetch dentists")
            return False
    except Exception as e:
        print(f"❌ Error fetching dentists: {e}")
        return False

def test_patient_lookup():
    """Test patient lookup functionality."""
    print("👤 Testing patient lookup...")
    
    try:
        # Test with a name that might not exist (should return empty list)
        patients = find_patient_by_name("TestPatient12345")
        if patients is not None:
            print(f"✅ Patient lookup working (found {len(patients)} patients)")
            return True
        else:
            print("❌ Patient lookup failed")
            return False
    except Exception as e:
        print(f"❌ Error in patient lookup: {e}")
        return False

def run_all_tests():
    """Run all database tests."""
    print("🧪 Database Tests")
    print("=" * 30)
    
    # Check environment
    required_vars = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_HOST']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables: OK")
    print()
    
    tests = [
        test_db_connection,
        test_fetch_dentists,
        test_patient_lookup
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All database tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()
