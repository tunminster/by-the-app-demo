#!/usr/bin/env python3
"""
Quick Kafka Test - Send a test message
"""

import os
import json
from datetime import datetime
from app.utils.kafka_producer import ai_response_producer

def quick_test():
    """Send a quick test message to Kafka."""
    print("🧪 Quick Kafka Test")
    print("=" * 30)
    
    # Check environment
    if not os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
        print("❌ KAFKA_BOOTSTRAP_SERVERS not set")
        return False
    
    print(f"📡 Kafka Server: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
    print(f"📁 CA File: {os.getenv('KAFKA_SSL_CA_FILE')}")
    print()
    
    try:
        # Send test message
        print("📤 Sending test message...")
        
        success = ai_response_producer.send_ai_response(
            call_id="quick-test-001",
            response_type="PATIENT_CREATION", 
            data={
                "name": "Quick Test Patient",
                "email": "quicktest@example.com",
                "phone": "555-9999", 
                "date_of_birth": "01/01/2000"
            },
            metadata={
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "message": "This is a quick test message"
            }
        )
        
        if success:
            print("✅ Message sent successfully!")
            print("🎉 Kafka connection is working!")
            print()
            print("💡 To test consumption, run:")
            print("   python run_kafka_consumer.py")
            return True
        else:
            print("❌ Failed to send message")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()
