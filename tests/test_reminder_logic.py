#!/usr/bin/env python3
"""
Test PATIENT_CREATION Reminder Function
Verify that reminders are sent when needed
"""

import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_reminder_logic():
    """Test the reminder logic for PATIENT_CREATION."""
    print("🧪 Testing PATIENT_CREATION Reminder Logic")
    print("=" * 45)
    
    # Test cases for reminder triggering
    test_cases = [
        {
            "text": "I'll need to create a new patient record for you. Let me collect your information.",
            "should_remind": True,
            "reason": "Contains 'create' keyword"
        },
        {
            "text": "I found your record. Let me confirm your details.",
            "should_remind": False,
            "reason": "Existing patient scenario"
        },
        {
            "text": "What's your name and phone number?",
            "should_remind": True,
            "reason": "Collecting information"
        },
        {
            "text": "Thank you for calling. How can I help you?",
            "should_remind": False,
            "reason": "General greeting"
        },
        {
            "text": "I need to collect your information for the new patient record.",
            "should_remind": True,
            "reason": "Contains 'new patient' and 'collect'"
        }
    ]
    
    # Test the reminder logic
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['reason']}")
        print(f"Text: {test_case['text']}")
        
        # Simulate the reminder logic
        keywords = ["new patient", "create", "collect", "information", "record"]
        should_remind = any(keyword in test_case['text'].lower() for keyword in keywords)
        
        print(f"Reminder triggered: {'✅ Yes' if should_remind else '❌ No'}")
        print(f"Expected: {'✅ Yes' if test_case['should_remind'] else '❌ No'}")
        
        if should_remind == test_case['should_remind']:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")
    
    print("\n🔧 Reminder Message Format:")
    reminder_message = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        "REMINDER: If you have collected all patient information (name, email, phone, date of birth) "
                        "and this is a NEW patient, you MUST output the PATIENT_CREATION format in your next response. "
                        "Example: PATIENT_CREATION: {\"name\": \"John Smith\", \"email\": \"john@email.com\", \"phone\": \"(555) 123-4567\", \"date_of_birth\": \"01/15/1985\"}"
                    )
                }
            ]
        }
    }
    
    print(json.dumps(reminder_message, indent=2))
    
    print("\n🎯 Expected Behavior:")
    print("1. AI collects patient information")
    print("2. If PATIENT_CREATION not detected, reminder is sent")
    print("3. AI should output PATIENT_CREATION format in next response")
    print("4. Debug logs will show the detection process")

if __name__ == "__main__":
    test_reminder_logic()
