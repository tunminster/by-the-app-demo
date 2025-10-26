#!/usr/bin/env python3
"""
Kafka Producer Tests
Tests sending messages to Kafka topic
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.kafka_producer import ai_response_producer

def test_producer_connection():
    """Test if producer can connect to Kafka."""
    print("🔌 Testing Kafka Producer Connection...")
    
    try:
        if ai_response_producer.producer:
            print("✅ Producer connection: OK")
            return True
        else:
            print("❌ Producer connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_send_patient_creation():
    """Test sending patient creation message."""
    print("📝 Testing PATIENT_CREATION message...")
    
    try:
        success = ai_response_producer.send_ai_response(
            call_id="test-patient-001",
            response_type="PATIENT_CREATION",
            data={
                "name": "Test Patient",
                "email": "test@example.com",
                "phone": "555-1234",
                "date_of_birth": "01/01/1990"
            },
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        if success:
            print("✅ PATIENT_CREATION message sent successfully!")
            return True
        else:
            print("❌ Failed to send PATIENT_CREATION message")
            return False
            
    except Exception as e:
        print(f"❌ Error sending patient creation: {e}")
        return False

def test_send_booking_confirmation():
    """Test sending booking confirmation message."""
    print("📝 Testing BOOKING_CONFIRMATION message...")
    
    try:
        success = ai_response_producer.send_ai_response(
            call_id="test-booking-001",
            response_type="BOOKING_CONFIRMATION",
            data={
                "dentist": "Dr. Test Smith",
                "date": "2025-10-25",
                "time": "10:00",
                "patient_name": "Test Patient"
            },
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        if success:
            print("✅ BOOKING_CONFIRMATION message sent successfully!")
            return True
        else:
            print("❌ Failed to send BOOKING_CONFIRMATION message")
            return False
            
    except Exception as e:
        print(f"❌ Error sending booking confirmation: {e}")
        return False

def run_all_tests():
    """Run all producer tests."""
    print("🧪 Kafka Producer Tests")
    print("=" * 40)
    
    # Check environment
    required_vars = ['KAFKA_BOOTSTRAP_SERVERS', 'KAFKA_SSL_CA_FILE', 'KAFKA_SSL_CERT_FILE', 'KAFKA_SSL_KEY_FILE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables: OK")
    print()
    
    tests = [
        test_producer_connection,
        test_send_patient_creation,
        test_send_booking_confirmation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All producer tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()
