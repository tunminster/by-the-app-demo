#!/usr/bin/env python3
"""
Test AI Response Processing via Kafka
Tests the new approach of sending entire AI response to Kafka
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.kafka_producer import ai_response_producer

def test_ai_response_processing():
    """Test sending AI response to Kafka for processing."""
    print("🧪 Testing AI Response Processing via Kafka")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
        print("❌ KAFKA_BOOTSTRAP_SERVERS not set")
        return False
    
    print(f"📡 Kafka Server: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
    print()
    
    # Simulate AI response with patient creation
    ai_response_with_patient = {
        "raw_text": "I'll help you create a new patient record. PATIENT_CREATION: {\"name\": \"John Doe\", \"email\": \"john@example.com\", \"phone\": \"555-1234\", \"date_of_birth\": \"01/15/1990\"} Please confirm these details.",
        "full_response": {
            "type": "response.done",
            "response": {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_audio",
                                "transcript": "I'll help you create a new patient record. PATIENT_CREATION: {\"name\": \"John Doe\", \"email\": \"john@example.com\", \"phone\": \"555-1234\", \"date_of_birth\": \"01/15/1990\"} Please confirm these details."
                            }
                        ]
                    }
                ]
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Simulate AI response with booking confirmation
    ai_response_with_booking = {
        "raw_text": "Perfect! I'll book your appointment. BOOKING_CONFIRMATION: {\"dentist\": \"Dr. Smith\", \"date\": \"2025-10-25\", \"time\": \"10:00\", \"patient_name\": \"John Doe\"} Your appointment is confirmed.",
        "full_response": {
            "type": "response.done",
            "response": {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_audio",
                                "transcript": "Perfect! I'll book your appointment. BOOKING_CONFIRMATION: {\"dentist\": \"Dr. Smith\", \"date\": \"2025-10-25\", \"time\": \"10:00\", \"patient_name\": \"John Doe\"} Your appointment is confirmed."
                            }
                        ]
                    }
                ]
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Simulate regular AI response (no actions)
    ai_response_regular = {
        "raw_text": "Hello! How can I help you today? I can assist with booking appointments or creating new patient records.",
        "full_response": {
            "type": "response.done",
            "response": {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_audio",
                                "transcript": "Hello! How can I help you today? I can assist with booking appointments or creating new patient records."
                            }
                        ]
                    }
                ]
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    test_cases = [
        ("Patient Creation", ai_response_with_patient),
        ("Booking Confirmation", ai_response_with_booking),
        ("Regular Response", ai_response_regular)
    ]
    
    success_count = 0
    
    for test_name, ai_response in test_cases:
        print(f"📤 Testing: {test_name}")
        
        try:
            success = ai_response_producer.send_ai_response(
                call_id=f"test-{test_name.lower().replace(' ', '-')}-001",
                response_type="AI_RESPONSE",
                data=ai_response,
                metadata={
                    "source": "test",
                    "test_case": test_name,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            if success:
                print(f"✅ {test_name} sent successfully!")
                success_count += 1
            else:
                print(f"❌ {test_name} failed to send")
                
        except Exception as e:
            print(f"❌ Error sending {test_name}: {e}")
        
        print()
    
    print(f"📊 Results: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("🎉 All AI response tests passed!")
        print("💡 Check your Kafka consumer logs to see the processing results")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    test_ai_response_processing()
