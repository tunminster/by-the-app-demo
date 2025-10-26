#!/usr/bin/env python3
"""
Kafka Consumer Service for AI Response Processing
Run this as a separate service to process AI responses from Kafka.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.kafka_consumer import AIResponseConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('kafka_consumer.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the Kafka consumer."""
    logger.info("🚀 Starting Kafka Consumer Service...")
    
    # Check environment variables
    required_vars = [
        'KAFKA_BOOTSTRAP_SERVERS',
        'KAFKA_SSL_CA_FILE',
        'KAFKA_SSL_CERT_FILE',
        'KAFKA_SSL_KEY_FILE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("Please set up your Kafka configuration in .env file")
        sys.exit(1)
    
    try:
        # Initialize and start consumer
        consumer = AIResponseConsumer()
        if consumer.consumer:
            logger.info("✅ Consumer initialized successfully")
            consumer.start_consuming()
        else:
            logger.error("❌ Failed to initialize consumer")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Consumer stopped by user")
    except Exception as e:
        logger.error(f"❌ Error running consumer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
