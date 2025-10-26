#!/usr/bin/env python3
"""
Test Runner - Run all tests
Organized test suite for the AI Voice Assistant
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change to project root directory
os.chdir(project_root)

def run_kafka_tests():
    """Run Kafka tests."""
    print("🧪 Running Kafka Tests...")
    print("=" * 50)
    
    try:
        from tests.kafka.test_producer import run_all_tests as test_producer
        from tests.kafka.test_consumer import run_all_tests as test_consumer
        
        producer_success = test_producer()
        print()
        consumer_success = test_consumer()
        
        return producer_success and consumer_success
    except Exception as e:
        print(f"❌ Kafka tests failed: {e}")
        return False

def run_database_tests():
    """Run database tests."""
    print("\n🧪 Running Database Tests...")
    print("=" * 50)
    
    try:
        from tests.database.test_db_connection import run_all_tests as test_db
        return test_db()
    except Exception as e:
        print(f"❌ Database tests failed: {e}")
        return False

def run_voice_tests():
    """Run voice integration tests."""
    print("\n🧪 Running Voice Integration Tests...")
    print("=" * 50)
    
    try:
        from tests.voice.test_voice_integration import run_all_tests as test_voice
        return test_voice()
    except Exception as e:
        print(f"❌ Voice tests failed: {e}")
        return False

def run_quick_test():
    """Run quick Kafka test."""
    print("⚡ Running Quick Kafka Test...")
    print("=" * 50)
    
    try:
        from tests.kafka.quick_test import quick_kafka_test
        return quick_kafka_test()
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 AI Voice Assistant Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Please run from project root directory")
        return False
    
    print("✅ Project structure: OK")
    print()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "kafka":
            success = run_kafka_tests()
        elif test_type == "database":
            success = run_database_tests()
        elif test_type == "voice":
            success = run_voice_tests()
        elif test_type == "quick":
            success = run_quick_test()
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Available: kafka, database, voice, quick")
            return False
    else:
        # Run all tests
        print("Running all tests...")
        print()
        
        kafka_success = run_kafka_tests()
        database_success = run_database_tests()
        voice_success = run_voice_tests()
        
        success = kafka_success and database_success and voice_success
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
        print("✅ Your system is ready for deployment!")
    else:
        print("❌ Some tests failed")
        print("🔧 Please check the errors above")
    
    return success

if __name__ == "__main__":
    main()
