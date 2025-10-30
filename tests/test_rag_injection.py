#!/usr/bin/env python3
"""
Test RAG Injection for Patient Context
Verify that the AI instructions are being sent correctly
"""

import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_rag_injection():
    """Test the RAG injection message format."""
    print("🧪 Testing RAG Injection for Patient Context")
    print("=" * 50)
    
    # Simulate the RAG injection message
    patient_context = "NO EXISTING PATIENTS FOUND - This appears to be a new patient.\n\n"
    
    context_message = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        f"{patient_context}"
                        "PATIENT VERIFICATION INSTRUCTIONS:\n"
                        "1. If existing patients are found above, confirm their details (name, phone, email, date of birth)\n"
                        "2. If no existing patients found, collect NEW PATIENT information:\n"
                        "   - Full name\n"
                        "   - Phone number\n"
                        "   - Email address\n"
                        "   - Date of birth (MM/DD/YYYY format)\n"
                        "3. For new patients, say: 'I'll need to create a new patient record for you. Let me collect your information.'\n"
                        "4. For existing patients, say: 'I found your record. Let me confirm your details.'\n"
                        "5. Always verify the information before proceeding with appointment booking.\n"
                        "6. If creating a new patient, use the collected information to create the patient record before booking.\n"
                        "7. When you have collected all patient information, output exactly this format (do not speak this out loud):\n"
                        "PATIENT_CREATION: {\"name\": \"John Smith\", \"email\": \"john@email.com\", \"phone\": \"(555) 123-4567\", \"date_of_birth\": \"01/15/1985\"}"
                    )
                }
            ]
        }
    }
    
    print("📝 RAG Injection Message:")
    print(json.dumps(context_message, indent=2))
    
    print("\n🔍 Key Instructions:")
    instructions = context_message["item"]["content"][0]["text"]
    lines = instructions.split('\n')
    
    for i, line in enumerate(lines, 1):
        if "PATIENT_CREATION:" in line:
            print(f"⭐ Line {i}: {line}")
        elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.')):
            print(f"📋 Line {i}: {line}")
    
    print("\n🎯 Expected AI Behavior:")
    print("1. AI should collect patient information")
    print("2. AI should output PATIENT_CREATION format (not speak it)")
    print("3. Voice.py should detect PATIENT_CREATION in the response")
    print("4. Kafka consumer should process the PATIENT_CREATION")
    
    print("\n🔧 Debugging Steps:")
    print("1. Check voice.py logs for '✅ PATIENT_CREATION detected in AI response!'")
    print("2. Check Kafka consumer logs for '👤 Found PATIENT_CREATION in AI response'")
    print("3. Verify the AI is not speaking the JSON format out loud")
    print("4. Test with: python debug_patient_creation.py")

if __name__ == "__main__":
    test_rag_injection()
