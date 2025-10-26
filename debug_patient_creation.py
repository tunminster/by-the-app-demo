#!/usr/bin/env python3
"""
Debug PATIENT_CREATION Detection
Test if the AI is outputting PATIENT_CREATION format correctly
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_patient_creation_detection():
    """Test if PATIENT_CREATION detection is working."""
    print("🧪 Testing PATIENT_CREATION Detection")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        {
            "name": "Valid PATIENT_CREATION",
            "text": 'PATIENT_CREATION: {"name": "John Doe", "email": "john@example.com", "phone": "(555) 123-4567", "date_of_birth": "01/15/1990"}',
            "should_find": True
        },
        {
            "name": "PATIENT_CREATION with extra text",
            "text": 'I need to create a new patient. PATIENT_CREATION: {"name": "Jane Smith", "email": "jane@example.com", "phone": "(555) 987-6543", "date_of_birth": "02/20/1985"} Please confirm.',
            "should_find": True
        },
        {
            "name": "No PATIENT_CREATION",
            "text": 'Hello, how can I help you today?',
            "should_find": False
        },
        {
            "name": "Malformed PATIENT_CREATION",
            "text": 'PATIENT_CREATION: {"name": "Bob", "email": "bob@example.com"}',  # Missing phone and date_of_birth
            "should_find": True
        }
    ]
    
    from app.utils.kafka_consumer import AIResponseConsumer
    consumer = AIResponseConsumer()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        
        # Test detection
        found = "PATIENT_CREATION:" in test_case['text']
        print(f"Detection: {'✅ Found' if found else '❌ Not found'}")
        
        if found:
            # Test JSON extraction
            patient_data = consumer.extract_json_from_text(test_case['text'], r"PATIENT_CREATION:\s*(\{)")
            if patient_data:
                print(f"✅ JSON extracted: {patient_data}")
            else:
                print("❌ Failed to extract JSON")
        
        # Check if result matches expectation
        if found == test_case['should_find']:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")
    
    print("\n🎯 Debugging Tips:")
    print("1. Check if AI is following the instructions in inject_patient_context()")
    print("2. Look for 'PATIENT_CREATION detected in AI response!' in voice.py logs")
    print("3. Check Kafka consumer logs for 'Found PATIENT_CREATION in AI response'")
    print("4. Verify the AI is not speaking the PATIENT_CREATION format out loud")

if __name__ == "__main__":
    test_patient_creation_detection()
