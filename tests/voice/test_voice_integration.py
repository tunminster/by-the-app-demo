#!/usr/bin/env python3
"""
Voice Integration Tests
Tests voice API integration with Kafka
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

def test_voice_kafka_integration():
    """Test voice API integration with Kafka."""
    print("🎤 Testing Voice-Kafka Integration...")
    
    try:
        # Simulate AI response processing
        print("📝 Simulating PATIENT_CREATION from voice AI...")
        
        # This simulates what happens in process_ai_text_response
        patient_data = {
            "name": "Voice Test Patient",
            "email": "voicetest@example.com",
            "phone": "555-VOICE",
            "date_of_birth": "01/01/1985"
        }
        
        success = ai_response_producer.send_ai_response(
            call_id="voice-test-001",
            response_type="PATIENT_CREATION",
            data=patient_data,
            metadata={
                "source": "voice_ai",
                "timestamp": datetime.now().isoformat(),
                "call_id": "voice-test-001"
            }
        )
        
        if success:
            print("✅ Voice-Kafka integration working!")
            return True
        else:
            print("❌ Voice-Kafka integration failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in voice integration: {e}")
        return False

def test_booking_flow():
    """Test complete booking flow."""
    print("📅 Testing Booking Flow...")
    
    try:
        # Simulate booking confirmation from voice AI
        booking_data = {
            "dentist": "Dr. Voice Test",
            "date": "2025-10-25",
            "time": "14:00",
            "patient_name": "Voice Test Patient"
        }
        
        success = ai_response_producer.send_ai_response(
            call_id="voice-booking-001",
            response_type="BOOKING_CONFIRMATION",
            data=booking_data,
            metadata={
                "source": "voice_ai",
                "timestamp": datetime.now().isoformat(),
                "call_id": "voice-booking-001"
            }
        )
        
        if success:
            print("✅ Booking flow integration working!")
            return True
        else:
            print("❌ Booking flow integration failed")
            return False
            
    except Exception as e:
        print(f"❌ Error in booking flow: {e}")
        return False

def run_all_tests():
    """Run all voice integration tests."""
    print("🧪 Voice Integration Tests")
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
        test_voice_kafka_integration,
        test_booking_flow
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All voice integration tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()
