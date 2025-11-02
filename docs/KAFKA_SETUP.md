# Kafka Setup Guide for AI Response Processing

## 🎯 Architecture Overview

```
Voice Call → AI Response → Kafka Producer → Kafka Topic → Consumer → Database Operations
```

## 📋 Prerequisites

1. **Aiven Kafka Service** - Set up a Kafka cluster on Aiven
2. **SSL Certificates** - Download CA, cert, and key files from Aiven
3. **Python Dependencies** - Install kafka-python

## 🔧 Environment Variables

Add these to your `.env` file:

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=your-kafka-bootstrap-servers
KAFKA_TOPIC=ai-responses
KAFKA_GROUP_ID=ai-response-processor

# SSL Configuration (from Aiven)
KAFKA_SSL_CA_FILE=/path/to/ca.pem
KAFKA_SSL_CERT_FILE=/path/to/service.cert
KAFKA_SSL_KEY_FILE=/path/to/service.key
```

## 🚀 Running the System

### 1. Start the Voice API
```bash
uvicorn app:app --reload
```

### 2. Start the Kafka Consumer (separate terminal)
```bash
python app/utils/kafka_consumer.py
```

## 📊 Message Flow

### Patient Creation Flow:
1. AI collects patient information
2. AI outputs: `PATIENT_CREATION: {"name": "John", "email": "john@email.com", "phone": "555-1234", "date_of_birth": "01/15/1985"}`
3. Voice API sends message to Kafka
4. Consumer processes patient creation
5. Database updated with new patient

### Booking Confirmation Flow:
1. AI confirms appointment details
2. AI outputs: `BOOKING_CONFIRMATION: {"dentist": "Dr. Smith", "date": "2025-10-25", "time": "10:00", "patient_name": "John"}`
3. Voice API sends message to Kafka
4. Consumer processes booking
5. Database updated with appointment

## 🔍 Monitoring

- Check Kafka topic for message flow
- Monitor consumer logs for processing status
- Database logs for successful operations

## 🛠️ Development

### Testing Kafka Connection:
```python
from app.utils.kafka_producer import ai_response_producer

# Test message
success = ai_response_producer.send_ai_response(
    call_id="test-123",
    response_type="PATIENT_CREATION",
    data={"name": "Test User", "email": "test@email.com", "phone": "555-1234", "date_of_birth": "01/01/1990"}
)
```

### Consumer Testing:
```python
from app.utils.kafka_consumer import AIResponseConsumer

consumer = AIResponseConsumer()
consumer.start_consuming()
```

## 📈 Benefits

- **Scalability**: Handle multiple concurrent calls
- **Reliability**: Message persistence and retry
- **Monitoring**: Better observability
- **Decoupling**: Voice processing separate from business logic
