#!/usr/bin/env python3
"""
Simple Kafka Test - Test only consumer without producer
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_kafka_consumer_only():
    """Test only the consumer without producer."""
    print("🧪 Testing Kafka Consumer Only")
    print("=" * 40)
    
    # Check environment
    required_vars = ['KAFKA_BOOTSTRAP_SERVERS', 'KAFKA_SSL_CA_FILE', 'KAFKA_SSL_CERT_FILE', 'KAFKA_SSL_KEY_FILE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables: OK")
    print(f"📡 Kafka Server: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
    print(f"📁 CA File: {os.getenv('KAFKA_SSL_CA_FILE')}")
    print()
    
    try:
        from app.utils.kafka_consumer import AIResponseConsumer
        
        print("🔌 Testing consumer connection...")
        consumer = AIResponseConsumer()
        
        if consumer.consumer:
            print("✅ Consumer connection: OK")
            print("📨 Consumer is ready to process messages")
            print("💡 Consumer will run for 10 seconds to test...")
            
            # Test for 10 seconds
            import time
            import threading
            
            def run_consumer():
                try:
                    consumer.start_consuming()
                except KeyboardInterrupt:
                    pass
            
            consumer_thread = threading.Thread(target=run_consumer, daemon=True)
            consumer_thread.start()
            
            # Let it run for 10 seconds
            time.sleep(10)
            
            print("✅ Consumer test completed successfully!")
            consumer.close()
            return True
        else:
            print("❌ Consumer connection: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_kafka_consumer_only()
