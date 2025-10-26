#!/usr/bin/env python3
"""
Quick Kafka Test Script
Tests both producer and consumer functionality
"""

import os
import json
import time
from datetime import datetime
from app.utils.kafka_producer import ai_response_producer
from app.utils.kafka_consumer import AIResponseConsumer

def test_kafka_producer():
    """Test sending messages to Kafka."""
    print("🧪 Testing Kafka Producer...")
    
    try:
        # Test 1: Patient Creation Message
        print("📝 Sending PATIENT_CREATION message...")
        success1 = ai_response_producer.send_ai_response(
            call_id="test-call-123",
            response_type="PATIENT_CREATION",
            data={
                "name": "Test Patient",
                "email": "test@example.com", 
                "phone": "555-1234",
                "date_of_birth": "01/01/1990"
            },
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        if success1:
            print("✅ PATIENT_CREATION message sent successfully!")
        else:
            print("❌ Failed to send PATIENT_CREATION message")
            return False
        
        # Test 2: Booking Confirmation Message
        print("📝 Sending BOOKING_CONFIRMATION message...")
        success2 = ai_response_producer.send_ai_response(
            call_id="test-call-456",
            response_type="BOOKING_CONFIRMATION",
            data={
                "dentist": "Dr. Test Smith",
                "date": "2025-10-25",
                "time": "10:00",
                "patient_name": "Test Patient"
            },
            metadata={"test": True, "timestamp": datetime.now().isoformat()}
        )
        
        if success2:
            print("✅ BOOKING_CONFIRMATION message sent successfully!")
        else:
            print("❌ Failed to send BOOKING_CONFIRMATION message")
            return False
            
        print("🎉 All producer tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Producer test failed: {e}")
        return False

def test_kafka_consumer():
    """Test consuming messages from Kafka."""
    print("\n🧪 Testing Kafka Consumer...")
    
    try:
        consumer = AIResponseConsumer()
        if not consumer.consumer:
            print("❌ Consumer not initialized")
            return False
            
        print("✅ Consumer initialized successfully!")
        print("📨 Consumer is ready to process messages...")
        print("💡 Note: Consumer will run until you stop it (Ctrl+C)")
        
        # Start consuming (this will run until interrupted)
        consumer.start_consuming()
        
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")
        return False

def test_kafka_connection():
    """Test basic Kafka connection."""
    print("🔌 Testing Kafka Connection...")
    
    try:
        # Test producer connection
        if ai_response_producer.producer:
            print("✅ Producer connection: OK")
        else:
            print("❌ Producer connection: FAILED")
            return False
            
        # Test consumer connection
        consumer = AIResponseConsumer()
        if consumer.consumer:
            print("✅ Consumer connection: OK")
            consumer.close()  # Close immediately for test
        else:
            print("❌ Consumer connection: FAILED")
            return False
            
        print("🎉 Kafka connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Run all Kafka tests."""
    print("🚀 Starting Kafka Tests...")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'KAFKA_BOOTSTRAP_SERVERS',
        'KAFKA_SSL_CA_FILE', 
        'KAFKA_SSL_CERT_FILE',
        'KAFKA_SSL_KEY_FILE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please set up your .env file with Kafka configuration")
        return
    
    print("✅ Environment variables: OK")
    print()
    
    # Test 1: Connection
    if not test_kafka_connection():
        print("❌ Connection test failed. Check your Kafka configuration.")
        return
    
    print()
    
    # Test 2: Producer
    if not test_kafka_producer():
        print("❌ Producer test failed. Check your Kafka setup.")
        return
    
    print()
    print("🎉 All tests passed! Your Kafka setup is working correctly.")
    print()
    print("💡 Next steps:")
    print("1. Run the consumer: python run_kafka_consumer.py")
    print("2. Deploy to Kubernetes: kubectl apply -f manifests/kafka-consumer-deployment.yaml")
    print("3. Check logs: kubectl logs -l app=kafka-consumer -n by-the-app-prod")

if __name__ == "__main__":
    main()
