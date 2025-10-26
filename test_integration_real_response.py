#!/usr/bin/env python3
"""
Integration Test with Real AI Response
Tests the complete flow with actual OpenAI response format
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
from app.utils.kafka_consumer import AIResponseConsumer

def test_real_ai_response():
    """Test with the actual AI response format from the logs."""
    print("🧪 Integration Test with Real AI Response")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
        print("❌ KAFKA_BOOTSTRAP_SERVERS not set")
        return False
    
    print(f"📡 Kafka Server: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
    print()
    
    # Real AI response from your logs
    real_ai_response = {
        "type": "response.done",
        "event_id": "event_CUjEeg8kQwdQEBax4HMH6",
        "response": {
            "object": "realtime.response",
            "id": "resp_CUjEVrd3yWJoJWHxyYsHJ",
            "status": "completed",
            "status_details": None,
            "output": [
                {
                    "id": "item_CUjEVzwWYJIXp2BybqGBR",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_audio",
                            "transcript": 'PATIENT_CREATION: {"name": "David Sam", "email": "david.sam@gmail.com", "phone": "(408) 818-2809", "date_of_birth": "01/02/1984"} \n\nBOOKING_CONFIRMATION: {"dentist": "Dr. Sarah Nguyen", "date": "2025-11-15", "time": "15:00", "patient_name": "David Sam"} \n\nYour appointment is confirmed for November 15, 2025, at 3:00 PM with Dr. Sarah Nguyen. You\'re all set! If you have any other questions, feel free to ask.'
                        }
                    ]
                }
            ],
            "conversation_id": "conv_CUjCOaW45UmWz0DgaGXJF",
            "output_modalities": ["audio"],
            "max_output_tokens": "inf",
            "audio": {
                "output": {
                    "format": {"type": "audio/pcmu"},
                    "voice": "alloy"
                }
            }
        },
        "usage": {
            "total_tokens": 2621,
            "input_tokens": 1790,
            "output_tokens": 831,
            "input_token_details": {
                "text_tokens": 1057,
                "audio_tokens": 733,
                "image_tokens": 0,
                "cached_tokens": 576,
                "cached_tokens_details": {
                    "text_tokens": 576,
                    "audio_tokens": 0,
                    "image_tokens": 0
                }
            },
            "output_token_details": {
                "text_tokens": 171,
                "audio_tokens": 660
            }
        },
        "metadata": None
    }
    
    # Extract text from the response (same logic as voice.py)
    text_chunk = []
    for item in real_ai_response["response"]["output"]:
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_audio" and "transcript" in c:
                    text_chunk.append(c["transcript"])
    
    raw_text = "".join(text_chunk)
    print(f"📝 Extracted Text: {raw_text}")
    print()
    
    # Test 1: Send to Kafka
    print("📤 Test 1: Sending to Kafka...")
    try:
        success = ai_response_producer.send_ai_response(
            call_id="integration-test-001",
            response_type="AI_RESPONSE",
            data={
                "raw_text": raw_text,
                "full_response": real_ai_response,
                "timestamp": datetime.now().isoformat()
            },
            metadata={
                "source": "integration_test",
                "test_type": "real_ai_response",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        if success:
            print("✅ Successfully sent to Kafka!")
        else:
            print("❌ Failed to send to Kafka")
            return False
            
    except Exception as e:
        print(f"❌ Error sending to Kafka: {e}")
        return False
    
    print()
    
    # Test 2: Parse the response locally (simulate consumer logic)
    print("🔍 Test 2: Parsing AI Response...")
    
    # Check for patient creation
    import re
    patient_match = re.search(r"PATIENT_CREATION:\s*(\{.*\})", raw_text, re.DOTALL)
    if patient_match:
        print("✅ Found PATIENT_CREATION")
        try:
            json_part = patient_match.group(1)
            patient_data = json.loads(json_part)
            print(f"📋 Patient Data: {patient_data}")
        except Exception as e:
            print(f"❌ Error parsing patient data: {e}")
    else:
        print("❌ No PATIENT_CREATION found")
    
    # Check for booking confirmation
    booking_match = re.search(r"BOOKING_CONFIRMATION:\s*(\{.*\})", raw_text, re.DOTALL)
    if booking_match:
        print("✅ Found BOOKING_CONFIRMATION")
        try:
            json_part = booking_match.group(1)
            booking_data = json.loads(json_part)
            print(f"📋 Booking Data: {booking_data}")
            
            # Add phone number from patient data if available
            if patient_match:
                try:
                    patient_json = json.loads(patient_match.group(1))
                    booking_data["phone"] = patient_json.get("phone", "N/A")
                    print(f"📞 Added phone to booking: {booking_data['phone']}")
                except:
                    booking_data["phone"] = "N/A"
            else:
                booking_data["phone"] = "N/A"
                
        except Exception as e:
            print(f"❌ Error parsing booking data: {e}")
    else:
        print("❌ No BOOKING_CONFIRMATION found")
    
    print()
    
    # Test 3: Test consumer processing (if available)
    print("🤖 Test 3: Testing Consumer Processing...")
    try:
        consumer = AIResponseConsumer()
        if consumer.consumer:
            print("✅ Consumer initialized successfully")
            
            # Test the process_ai_response method directly
            test_data = {
                "raw_text": raw_text,
                "full_response": real_ai_response,
                "timestamp": datetime.now().isoformat()
            }
            
            result = consumer.process_ai_response(test_data, "integration-test-001")
            if result:
                print("✅ Consumer processing successful!")
            else:
                print("❌ Consumer processing failed")
                
            consumer.close()
        else:
            print("❌ Consumer initialization failed")
            
    except Exception as e:
        print(f"❌ Error testing consumer: {e}")
    
    print()
    print("🎉 Integration test completed!")
    print("💡 Check your Kafka consumer logs to see the full processing results")
    
    return True

if __name__ == "__main__":
    test_real_ai_response()
