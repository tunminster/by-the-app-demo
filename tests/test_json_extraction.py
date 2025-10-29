#!/usr/bin/env python3
"""
Test JSON Extraction from AI Response
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.kafka_consumer import AIResponseConsumer

def test_json_extraction():
    """Test the JSON extraction method."""
    print("🧪 Testing JSON Extraction")
    print("=" * 30)
    
    # Test text with both PATIENT_CREATION and BOOKING_CONFIRMATION
    test_text = 'PATIENT_CREATION: {"name": "David Sam", "email": "david.sam@gmail.com", "phone": "(408) 818-2809", "date_of_birth": "01/02/1984"} \n\nBOOKING_CONFIRMATION: {"dentist": "Dr. Sarah Nguyen", "date": "2025-11-15", "time": "15:00", "patient_name": "David Sam"} \n\nYour appointment is confirmed for November 15, 2025, at 3:00 PM with Dr. Sarah Nguyen. You\'re all set! If you have any other questions, feel free to ask.'
    
    print(f"📝 Test Text: {test_text[:100]}...")
    print()
    
    # Create consumer instance
    consumer = AIResponseConsumer()
    
    # Test patient creation extraction
    print("👤 Testing PATIENT_CREATION extraction...")
    patient_data = consumer.extract_json_from_text(test_text, r"PATIENT_CREATION:\s*(\{)")
    if patient_data:
        print(f"✅ Patient data extracted: {patient_data}")
    else:
        print("❌ Failed to extract patient data")
    
    print()
    
    # Test booking confirmation extraction
    print("📅 Testing BOOKING_CONFIRMATION extraction...")
    booking_data = consumer.extract_json_from_text(test_text, r"BOOKING_CONFIRMATION:\s*(\{)")
    if booking_data:
        print(f"✅ Booking data extracted: {booking_data}")
    else:
        print("❌ Failed to extract booking data")
    
    print()
    
    # Test full AI response processing
    print("🤖 Testing full AI response processing...")
    test_data = {
        "raw_text": test_text,
        "full_response": {"type": "response.done"},
        "timestamp": "2025-10-25T21:30:00"
    }
    
    result = consumer.process_ai_response(test_data, "test-001")
    if result:
        print("✅ Full AI response processing successful!")
    else:
        print("❌ Full AI response processing failed")
    
    print()
    print("🎉 JSON extraction test completed!")

if __name__ == "__main__":
    test_json_extraction()
