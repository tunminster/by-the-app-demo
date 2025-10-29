#!/usr/bin/env python3
"""
Test Updated SYSTEM_MESSAGE
Verify that PATIENT_CREATION and BOOKING_CONFIRMATION are both included
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_system_message():
    """Test the updated SYSTEM_MESSAGE."""
    print("🧪 Testing Updated SYSTEM_MESSAGE")
    print("=" * 35)
    
    # Import the SYSTEM_MESSAGE from voice.py
    from app.routes.voice import SYSTEM_MESSAGE
    
    print("\n📝 SYSTEM_MESSAGE Content:")
    print("=" * 30)
    print(SYSTEM_MESSAGE)
    
    print("\n🔍 Key Checks:")
    print("=" * 30)
    
    # Check 1: PATIENT_CREATION mentioned
    has_patient_creation = "PATIENT_CREATION" in SYSTEM_MESSAGE
    print(f"✅ PATIENT_CREATION mentioned: {has_patient_creation}")
    
    # Check 2: BOOKING_CONFIRMATION mentioned
    has_booking_confirmation = "BOOKING_CONFIRMATION" in SYSTEM_MESSAGE
    print(f"✅ BOOKING_CONFIRMATION mentioned: {has_booking_confirmation}")
    
    # Check 3: "Do NOT speak" instruction
    has_no_speak = "Do NOT speak" in SYSTEM_MESSAGE or "do NOT speak" in SYSTEM_MESSAGE
    print(f"✅ 'Do NOT speak' instruction: {has_no_speak}")
    
    # Check 4: Patient information fields
    has_patient_fields = all(field in SYSTEM_MESSAGE for field in ["name", "email", "phone", "date_of_birth"])
    print(f"✅ All patient fields mentioned: {has_patient_fields}")
    
    # Check 5: Example format provided
    has_example = '"name": "John Smith"' in SYSTEM_MESSAGE
    print(f"✅ Example format provided: {has_example}")
    
    print("\n📊 Summary:")
    print("=" * 30)
    all_checks = [
        has_patient_creation,
        has_booking_confirmation,
        has_no_speak,
        has_patient_fields,
        has_example
    ]
    
    if all(all_checks):
        print("✅ All checks passed! SYSTEM_MESSAGE is complete.")
    else:
        print("❌ Some checks failed. Please review the SYSTEM_MESSAGE.")
    
    print("\n🎯 Expected Behavior:")
    print("1. AI receives SYSTEM_MESSAGE at the start of conversation")
    print("2. AI knows about both PATIENT_CREATION and BOOKING_CONFIRMATION formats")
    print("3. AI understands not to speak these formats out loud")
    print("4. RAG injections add more detailed context when needed")
    
    print("\n💡 Why Both Are Needed:")
    print("- SYSTEM_MESSAGE: Initial knowledge at conversation start")
    print("- RAG Injection: Detailed context when patient lookup happens")
    print("- Reminder: Extra prompt if AI forgets to output format")

if __name__ == "__main__":
    test_system_message()
