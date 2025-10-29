#!/usr/bin/env python3
"""
Test Improved AI Instructions
Verify that the new instructions are clearer and more explicit
"""

import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_improved_instructions():
    """Test the improved RAG injection instructions."""
    print("🧪 Testing Improved AI Instructions")
    print("=" * 40)
    
    # Simulate the improved RAG injection message
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
                        "CRITICAL PATIENT MANAGEMENT INSTRUCTIONS:\n\n"
                        "SCENARIO 1 - EXISTING PATIENT FOUND:\n"
                        "1. Confirm their details: 'I found your record. Let me confirm your details.'\n"
                        "2. Verify: name, phone, email, date of birth\n"
                        "3. Proceed with appointment booking\n\n"
                        
                        "SCENARIO 2 - NEW PATIENT (NO EXISTING RECORDS):\n"
                        "1. Say: 'I'll need to create a new patient record for you. Let me collect your information.'\n"
                        "2. Collect ALL required information:\n"
                        "   - Full name (first and last)\n"
                        "   - Phone number (with area code)\n"
                        "   - Email address\n"
                        "   - Date of birth (MM/DD/YYYY format)\n"
                        "3. Verify each piece of information with the caller\n"
                        "4. IMPORTANT: After collecting ALL information, you MUST output this EXACT format in your response (do NOT speak this out loud):\n\n"
                        
                        "PATIENT_CREATION: {\"name\": \"[FULL_NAME]\", \"email\": \"[EMAIL]\", \"phone\": \"[PHONE]\", \"date_of_birth\": \"[MM/DD/YYYY]\"}\n\n"
                        
                        "EXAMPLE OUTPUT (do not speak this):\n"
                        "PATIENT_CREATION: {\"name\": \"John Smith\", \"email\": \"john@email.com\", \"phone\": \"(555) 123-4567\", \"date_of_birth\": \"01/15/1985\"}\n\n"
                        
                        "CRITICAL RULES:\n"
                        "- You MUST output PATIENT_CREATION format for NEW patients\n"
                        "- Replace [FULL_NAME], [EMAIL], [PHONE], [DATE_OF_BIRTH] with actual values\n"
                        "- Do NOT speak the PATIENT_CREATION format out loud\n"
                        "- Only output PATIENT_CREATION after collecting ALL required information\n"
                        "- Always verify information before outputting PATIENT_CREATION"
                    )
                }
            ]
        }
    }
    
    print("📝 Improved Instructions:")
    print("=" * 30)
    
    instructions = context_message["item"]["content"][0]["text"]
    lines = instructions.split('\n')
    
    for i, line in enumerate(lines, 1):
        if "PATIENT_CREATION:" in line:
            print(f"⭐ Line {i}: {line}")
        elif line.strip().startswith(('CRITICAL', 'SCENARIO', 'IMPORTANT', 'EXAMPLE', 'CRITICAL RULES')):
            print(f"🔥 Line {i}: {line}")
        elif line.strip().startswith(('1.', '2.', '3.', '4.')):
            print(f"📋 Line {i}: {line}")
    
    print("\n🎯 Key Improvements:")
    print("✅ More explicit 'MUST output' language")
    print("✅ Clear scenario separation (existing vs new)")
    print("✅ Template with placeholders [FULL_NAME], [EMAIL], etc.")
    print("✅ Multiple reminders about not speaking the format")
    print("✅ Critical rules section with emphasis")
    print("✅ Example output provided")
    
    print("\n🔧 Additional Features Added:")
    print("✅ Automatic reminder if PATIENT_CREATION not detected")
    print("✅ Keyword detection for new patient scenarios")
    print("✅ Enhanced debug logging")
    
    print("\n📊 Expected Results:")
    print("1. AI should be more likely to follow instructions")
    print("2. Debug logs will show if PATIENT_CREATION is detected")
    print("3. Automatic reminders will prompt AI if needed")
    print("4. Clearer separation between existing and new patients")

if __name__ == "__main__":
    test_improved_instructions()
