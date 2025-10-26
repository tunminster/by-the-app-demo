#!/usr/bin/env python3
"""
Test Booking Confirmation Fix
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.kafka_consumer import AIResponseConsumer

def test_booking_confirmation():
    """Test the booking confirmation processing."""
    print("🧪 Testing Booking Confirmation Fix")
    print("=" * 40)
    
    # Test data with both patient creation and booking confirmation
    test_data = {
        "raw_text": 'PATIENT_CREATION: {"name": "David Sam", "email": "david.sam@gmail.com", "phone": "(408) 818-2809", "date_of_birth": "01/02/1984"} \n\nBOOKING_CONFIRMATION: {"dentist": "Dr. Sarah Nguyen", "date": "2025-11-15", "time": "15:00", "patient_name": "David Sam"} \n\nYour appointment is confirmed for November 15, 2025, at 3:00 PM with Dr. Sarah Nguyen. You\'re all set! If you have any other questions, feel free to ask.',
        "full_response": {"type": "response.done"},
        "timestamp": "2025-10-25T21:30:00"
    }
    
    print(f"📝 Test Data: {test_data['raw_text'][:100]}...")
    print()
    
    # Create consumer instance
    consumer = AIResponseConsumer()
    
    # Test JSON extraction
    print("🔍 Testing JSON extraction...")
    
    # Extract patient data
    patient_data = consumer.extract_json_from_text(test_data["raw_text"], r"PATIENT_CREATION:\s*(\{)")
    if patient_data:
        print(f"✅ Patient data: {patient_data}")
    else:
        print("❌ Failed to extract patient data")
    
    # Extract booking data
    booking_data = consumer.extract_json_from_text(test_data["raw_text"], r"BOOKING_CONFIRMATION:\s*(\{)")
    if booking_data:
        print(f"✅ Booking data: {booking_data}")
        
        # Add phone number from patient data
        if patient_data and "phone" in patient_data:
            booking_data["phone"] = patient_data["phone"]
            print(f"📞 Added phone to booking: {booking_data['phone']}")
        else:
            booking_data["phone"] = "N/A"
            print("📞 No phone found, using N/A")
    else:
        print("❌ Failed to extract booking data")
    
    print()
    
    # Test full processing (without actual database operations)
    print("🤖 Testing full AI response processing...")
    try:
        result = consumer.process_ai_response(test_data, "test-booking-001")
        if result:
            print("✅ Full AI response processing successful!")
        else:
            print("❌ Full AI response processing failed")
    except Exception as e:
        print(f"❌ Error in processing: {e}")
    
    print()
    print("🎉 Booking confirmation test completed!")

if __name__ == "__main__":
    test_booking_confirmation()
