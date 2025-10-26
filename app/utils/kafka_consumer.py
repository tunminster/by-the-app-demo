import json
import os
import logging
import re
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime
from app.utils.db import create_new_patient, find_patient_by_name, find_patient_by_phone
from app.utils.booking import book_if_possible

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIResponseConsumer:
    def __init__(self):
        self.consumer = None
        self.topic = os.getenv("KAFKA_TOPIC", "ai-responses")
        self._initialize_consumer()
    
    def _initialize_consumer(self):
        """Initialize Kafka consumer with Aiven configuration."""
        try:
            kafka_config = {
                'bootstrap_servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
                'security_protocol': 'SSL',
                'ssl_cafile': os.getenv("KAFKA_SSL_CA_FILE"),
                'ssl_certfile': os.getenv("KAFKA_SSL_CERT_FILE"),
                'ssl_keyfile': os.getenv("KAFKA_SSL_KEY_FILE"),
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'key_deserializer': lambda m: m.decode('utf-8') if m else None,
                'group_id': os.getenv("KAFKA_GROUP_ID", "ai-response-processor"),
                'auto_offset_reset': 'latest',
                'enable_auto_commit': True,
                'api_version': (0, 10, 1)
            }
            
            # Remove None values
            kafka_config = {k: v for k, v in kafka_config.items() if v is not None}
            
            self.consumer = KafkaConsumer(self.topic, **kafka_config)
            logger.info("✅ Kafka consumer initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kafka consumer: {e}")
            self.consumer = None
    
    def process_patient_creation(self, data, call_id):
        """Process patient creation request."""
        try:
            logger.info(f"🔄 Processing patient creation for call {call_id}")
            
            # Extract patient information
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            date_of_birth = data.get('date_of_birth', '').strip()
            
            if not all([name, email, phone, date_of_birth]):
                logger.error(f"❌ Missing required patient information: {data}")
                return False
            
            # Check if patient already exists
            existing_patient = find_patient_by_phone(phone)
            if existing_patient:
                logger.info(f"ℹ️ Patient already exists: {existing_patient['name']} (ID: {existing_patient['id']})")
                return True
            
            # Create new patient
            patient_id = create_new_patient(name, email, phone, date_of_birth)
            if patient_id:
                logger.info(f"✅ Created new patient: {name} (ID: {patient_id})")
                return True
            else:
                logger.error(f"❌ Failed to create patient: {name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing patient creation: {e}")
            return False
    
    def process_booking_confirmation(self, data, call_id):
        """Process booking confirmation request."""
        try:
            logger.info(f"🔄 Processing booking confirmation for call {call_id}")
            
            # Attempt booking
            success = book_if_possible(data)
            if success:
                logger.info(f"✅ Booking confirmed for {data.get('patient_name')} with {data.get('dentist')} on {data.get('date')} at {data.get('time')}")
                return True
            else:
                logger.error(f"❌ Booking failed for {data.get('patient_name')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing booking confirmation: {e}")
            return False
    
    def extract_json_from_text(self, text, pattern):
        """Extract JSON from text using a more robust method."""
        try:
            # Find the pattern
            match = re.search(pattern, text)
            if not match:
                return None
            
            json_start = match.start(1)
            json_text = text[json_start:]
            
            # Find the end of the JSON object by counting braces
            brace_count = 0
            json_end = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(json_text):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
            
            if json_end > 0:
                json_str = json_text[:json_end]
                logger.info(f"🔍 Extracted JSON: {json_str}")
                return json.loads(json_str)
            else:
                logger.error("❌ Could not find end of JSON object")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting JSON: {e}")
            return None

    def process_ai_response(self, data, call_id):
        """Process complete AI response and identify actions needed."""
        try:
            logger.info(f"🤖 Processing AI response for call {call_id}")
            
            raw_text = data.get('raw_text', '')
            full_response = data.get('full_response', {})
            
            logger.info(f"📝 AI Response Text: {raw_text[:200]}...")
            
            # Parse the AI response for different actions
            actions_taken = []
            
            # Check for patient creation
            if "PATIENT_CREATION:" in raw_text:
                logger.info("👤 Found PATIENT_CREATION in AI response")
                patient_data = self.extract_json_from_text(raw_text, r"PATIENT_CREATION:\s*(\{)")
                if patient_data:
                    logger.info(f"📋 Patient data: {patient_data}")
                    
                    # Process patient creation
                    if self.process_patient_creation(patient_data, call_id):
                        actions_taken.append("PATIENT_CREATION")
                        logger.info("✅ Patient creation completed")
                    else:
                        logger.error("❌ Patient creation failed")
                else:
                    logger.error("❌ Failed to extract patient data")
            
            # Check for booking confirmation
            if "BOOKING_CONFIRMATION:" in raw_text:
                logger.info("📅 Found BOOKING_CONFIRMATION in AI response")
                booking_data = self.extract_json_from_text(raw_text, r"BOOKING_CONFIRMATION:\s*(\{)")
                if booking_data:
                    logger.info(f"📋 Booking data: {booking_data}")
                    
                    # Add phone number from patient data if available
                    if "PATIENT_CREATION:" in raw_text:
                        patient_data = self.extract_json_from_text(raw_text, r"PATIENT_CREATION:\s*(\{)")
                        if patient_data and "phone" in patient_data:
                            booking_data["phone"] = patient_data["phone"]
                            logger.info(f"📞 Added phone to booking: {booking_data['phone']}")
                        else:
                            booking_data["phone"] = "N/A"
                    else:
                        booking_data["phone"] = "N/A"
                    
                    # Process booking confirmation
                    if self.process_booking_confirmation(booking_data, call_id):
                        actions_taken.append("BOOKING_CONFIRMATION")
                        logger.info("✅ Booking confirmation completed")
                    else:
                        logger.error("❌ Booking confirmation failed")
                else:
                    logger.error("❌ Failed to extract booking data")
            
            # Log summary
            if actions_taken:
                logger.info(f"✅ AI Response processed successfully. Actions taken: {', '.join(actions_taken)}")
                return True
            else:
                logger.info("ℹ️ No specific actions identified in AI response")
                return True  # Still successful, just no actions needed
                
        except Exception as e:
            logger.error(f"❌ Error processing AI response: {e}")
            return False
    
    def process_message(self, message):
        """Process a single Kafka message."""
        try:
            call_id = message.key
            response_type = message.value.get('response_type')
            data = message.value.get('data', {})
            metadata = message.value.get('metadata', {})
            
            logger.info(f"📨 Processing message: {response_type} for call {call_id}")
            
            success = False
            if response_type == "AI_RESPONSE":
                success = self.process_ai_response(data, call_id)
            elif response_type == "PATIENT_CREATION":
                success = self.process_patient_creation(data, call_id)
            elif response_type == "BOOKING_CONFIRMATION":
                success = self.process_booking_confirmation(data, call_id)
            else:
                logger.warning(f"⚠️ Unknown response type: {response_type}")
            
            if success:
                logger.info(f"✅ Successfully processed {response_type} for call {call_id}")
            else:
                logger.error(f"❌ Failed to process {response_type} for call {call_id}")
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    def start_consuming(self):
        """Start consuming messages from Kafka."""
        if not self.consumer:
            logger.error("❌ Kafka consumer not initialized")
            return
        
        logger.info(f"🚀 Starting to consume messages from topic: {self.topic}")
        
        try:
            for message in self.consumer:
                self.process_message(message)
        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped by user")
        except Exception as e:
            logger.error(f"❌ Error consuming messages: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close the Kafka consumer."""
        if self.consumer:
            self.consumer.close()
            logger.info("🔒 Kafka consumer closed")

# Standalone consumer for running as a separate service
if __name__ == "__main__":
    consumer = AIResponseConsumer()
    consumer.start_consuming()
