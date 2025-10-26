#!/usr/bin/env python3
"""
Kafka Consumer Tests
Tests consuming messages from Kafka topic
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.kafka_consumer import AIResponseConsumer

def test_consumer_connection():
    """Test if consumer can connect to Kafka."""
    print("🔌 Testing Kafka Consumer Connection...")
    
    try:
        consumer = AIResponseConsumer()
        if consumer.consumer:
            print("✅ Consumer connection: OK")
            consumer.close()
            return True
        else:
            print("❌ Consumer connection: FAILED")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_consumer_startup():
    """Test consumer startup and basic functionality."""
    print("🚀 Testing Consumer Startup...")
    
    try:
        consumer = AIResponseConsumer()
        if not consumer.consumer:
            print("❌ Consumer not initialized")
            return False
        
        print("✅ Consumer initialized successfully!")
        print("📨 Consumer is ready to process messages")
        
        # Test that consumer can start (but don't run indefinitely)
        print("⏱️  Testing consumer for 5 seconds...")
        print("💡 Note: This will consume any messages in the topic")
        
        # Start consumer in a separate thread for testing
        import threading
        import time
        
        def run_consumer():
            try:
                consumer.start_consuming()
            except KeyboardInterrupt:
                pass
        
        consumer_thread = threading.Thread(target=run_consumer, daemon=True)
        consumer_thread.start()
        
        # Let it run for 5 seconds
        time.sleep(5)
        
        print("✅ Consumer test completed")
        consumer.close()
        return True
        
    except Exception as e:
        print(f"❌ Consumer test failed: {e}")
        return False

def run_all_tests():
    """Run all consumer tests."""
    print("🧪 Kafka Consumer Tests")
    print("=" * 40)
    
    # Check environment
    required_vars = ['KAFKA_BOOTSTRAP_SERVERS', 'KAFKA_SSL_CA_FILE', 'KAFKA_SSL_CERT_FILE', 'KAFKA_SSL_KEY_FILE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables: OK")
    print()
    
    tests = [
        test_consumer_connection,
        test_consumer_startup
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All consumer tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()
