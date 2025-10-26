import json
import os
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIResponseProducer:
    def __init__(self):
        self.producer = None
        self.topic = os.getenv("KAFKA_TOPIC", "ai-responses")
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize Kafka producer with Aiven configuration."""
        try:
            kafka_config = {
                'bootstrap_servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
                'security_protocol': 'SSL',
                'ssl_cafile': os.getenv("KAFKA_SSL_CA_FILE"),
                'ssl_certfile': os.getenv("KAFKA_SSL_CERT_FILE"),
                'ssl_keyfile': os.getenv("KAFKA_SSL_KEY_FILE"),
                'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                'key_serializer': lambda v: v.encode('utf-8') if v else None,
                'retries': 3,
                'retry_backoff_ms': 1000,
                'request_timeout_ms': 30000,
                'api_version': (0, 10, 1)
            }
            
            # Remove None values
            kafka_config = {k: v for k, v in kafka_config.items() if v is not None}
            
            self.producer = KafkaProducer(**kafka_config)
            logger.info("✅ Kafka producer initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kafka producer: {e}")
            self.producer = None
    
    def send_ai_response(self, call_id, response_type, data, metadata=None):
        """
        Send AI response to Kafka topic.
        
        Args:
            call_id (str): Unique identifier for the call
            response_type (str): Type of response (PATIENT_CREATION, BOOKING_CONFIRMATION)
            data (dict): The actual data to process
            metadata (dict): Additional metadata about the call
        """
        if not self.producer:
            logger.error("❌ Kafka producer not initialized")
            return False
        
        try:
            message = {
                "call_id": call_id,
                "response_type": response_type,
                "data": data,
                "metadata": metadata or {},
                "timestamp": json.dumps({"timestamp": "now"})  # Will be replaced with actual timestamp
            }
            
            # Use call_id as key for partitioning
            future = self.producer.send(
                self.topic,
                key=call_id,
                value=message
            )
            
            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            logger.info(f"✅ Message sent to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
            
        except KafkaError as e:
            logger.error(f"❌ Kafka error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending message to Kafka: {e}")
            return False
    
    def close(self):
        """Close the Kafka producer."""
        if self.producer:
            self.producer.close()
            logger.info("🔒 Kafka producer closed")

# Global producer instance
ai_response_producer = AIResponseProducer()
