#!/usr/bin/env python3
"""
Docker Integration Test
Tests the complete flow with Docker consumer
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.kafka_producer import ai_response_producer

def test_docker_integration():
    """Test complete integration with Docker consumer."""
    print("🐳 Docker Integration Test")
    print("=" * 40)
    
    # Check if Docker is running
    try:
        subprocess.run(["docker", "ps"], check=True, capture_output=True)
        print("✅ Docker is running")
    except subprocess.CalledProcessError:
        print("❌ Docker is not running")
        return False
    
    # Check environment
    if not os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
        print("❌ KAFKA_BOOTSTRAP_SERVERS not set")
        return False
    
    print(f"📡 Kafka Server: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
    print()
    
    # Start Docker consumer in background
    print("🚀 Starting Docker consumer...")
    try:
        # Build and run consumer
        subprocess.run([
            "docker", "build", "-f", "Dockerfile.consumer", 
            "-t", "kafka-consumer:latest", "."
        ], check=True)
        
        # Run consumer in background
        consumer_process = subprocess.Popen([
            "docker", "run", "--rm", "-i",
            "--name", "kafka-consumer-test",
            "--env-file", ".env",
            "-v", f"{os.getcwd()}/certs:/app/certs:ro",
            "kafka-consumer:latest",
            "python", "run_kafka_consumer.py"
        ])
        
        print("✅ Docker consumer started")
        
        # Wait a moment for consumer to initialize
        print("⏳ Waiting for consumer to initialize...")
        time.sleep(5)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Docker consumer: {e}")
        return False
    
    # Send test message
    print("📤 Sending test message...")
    
    real_ai_response = {
        "raw_text": 'PATIENT_CREATION: {"name": "Tun Hein", "email": "tun.hein@gmail.com", "phone": "(408) 858-2309", "date_of_birth": "01/02/1984"} \n\nBOOKING_CONFIRMATION: {"dentist": "Dr. Sarah Nguyen", "date": "2025-11-15", "time": "15:00", "patient_name": "Tun Hein"} \n\nYour appointment is confirmed for November 15, 2025, at 3:00 PM with Dr. Sarah Nguyen. You\'re all set! If you have any other questions, feel free to ask.',
        "full_response": {
            "type": "response.done",
            "response": {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_audio",
                                "transcript": 'PATIENT_CREATION: {"name": "Tun Hein", "email": "tun.hein@gmail.com", "phone": "(408) 858-2309", "date_of_birth": "01/02/1984"} \n\nBOOKING_CONFIRMATION: {"dentist": "Dr. Sarah Nguyen", "date": "2025-11-15", "time": "15:00", "patient_name": "Tun Hein"} \n\nYour appointment is confirmed for November 15, 2025, at 3:00 PM with Dr. Sarah Nguyen. You\'re all set! If you have any other questions, feel free to ask.'
                            }
                        ]
                    }
                ]
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        success = ai_response_producer.send_ai_response(
            call_id="docker-integration-test-001",
            response_type="AI_RESPONSE",
            data=real_ai_response,
            metadata={
                "source": "docker_integration_test",
                "test_type": "real_ai_response",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        if success:
            print("✅ Message sent successfully!")
        else:
            print("❌ Failed to send message")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False
    
    # Wait for processing
    print("⏳ Waiting for consumer to process message...")
    time.sleep(10)
    
    # Check consumer logs
    print("📋 Checking consumer logs...")
    try:
        logs = subprocess.run([
            "docker", "logs", "kafka-consumer-test"
        ], capture_output=True, text=True)
        
        print("Consumer Logs:")
        print("-" * 40)
        print(logs.stdout)
        if logs.stderr:
            print("Errors:")
            print(logs.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting logs: {e}")
    
    # Clean up
    print("🧹 Cleaning up...")
    try:
        subprocess.run(["docker", "stop", "kafka-consumer-test"], 
                      capture_output=True)
        print("✅ Consumer stopped")
    except subprocess.CalledProcessError:
        pass  # Container might have already stopped
    
    print("🎉 Docker integration test completed!")
    return True

if __name__ == "__main__":
    test_docker_integration()
