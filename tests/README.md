# 🧪 Test Suite for AI Voice Assistant

Organized test suite for the AI Voice Assistant with Kafka integration.

## 📁 Test Structure

```
tests/
├── kafka/                    # Kafka integration tests
│   ├── test_producer.py      # Producer functionality
│   ├── test_consumer.py      # Consumer functionality
│   └── quick_test.py         # Quick connection test
├── database/                 # Database tests
│   └── test_db_connection.py # PostgreSQL connection
├── voice/                    # Voice integration tests
│   └── test_voice_integration.py # Voice-Kafka integration
└── run_all_tests.py         # Main test runner
```

## 🚀 Running Tests

### Quick Test (Recommended)
```bash
# Test Kafka connection and message sending
python tests/run_all_tests.py quick
```

### Individual Test Categories
```bash
# Kafka tests (producer + consumer)
python tests/run_all_tests.py kafka

# Database tests
python tests/run_all_tests.py database

# Voice integration tests
python tests/run_all_tests.py voice
```

### All Tests
```bash
# Run all tests
python tests/run_all_tests.py
```

### Individual Test Files
```bash
# Quick Kafka test
python tests/kafka/quick_test.py

# Producer test
python tests/kafka/test_producer.py

# Consumer test
python tests/kafka/test_consumer.py

# Database test
python tests/database/test_db_connection.py

# Voice integration test
python tests/voice/test_voice_integration.py
```

## 🔧 Prerequisites

### Environment Variables Required:
```bash
# Database
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your_host
POSTGRES_PORT=5432

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka-303b4b86-ragibull-4628.k.aivencloud.com:28372
KAFKA_SSL_CA_FILE=./certs/ca.pem
KAFKA_SSL_CERT_FILE=./certs/service.cert
KAFKA_SSL_KEY_FILE=./certs/service.key
```

## 📊 Test Categories

### 🔌 Kafka Tests
- **Producer**: Tests sending messages to Kafka
- **Consumer**: Tests consuming messages from Kafka
- **Quick Test**: Fast connection verification

### 🗄️ Database Tests
- **Connection**: Tests PostgreSQL connection
- **Functions**: Tests database utility functions
- **Patient Lookup**: Tests patient search functionality

### 🎤 Voice Integration Tests
- **Voice-Kafka**: Tests voice API integration with Kafka
- **Booking Flow**: Tests complete appointment booking flow
- **Message Processing**: Tests AI response processing

## 🎯 Test Results

### ✅ Success Indicators:
- All environment variables set correctly
- Kafka connection established
- Database connection working
- Messages sent and received successfully
- Voice integration functioning

### ❌ Common Issues:
- Missing environment variables
- Kafka SSL certificate issues
- Database connection problems
- Network connectivity issues

## 🚀 Deployment Verification

After running tests successfully:

1. **Deploy to Kubernetes**:
   ```bash
   kubectl apply -f manifests/kafka-consumer-deployment.yaml
   ```

2. **Check deployment**:
   ```bash
   kubectl get pods -l app=kafka-consumer -n by-the-app-prod
   kubectl logs -l app=kafka-consumer -n by-the-app-prod
   ```

3. **Monitor message flow**:
   - Check Kafka topic for messages
   - Monitor consumer logs
   - Verify database updates

## 🔍 Troubleshooting

### Kafka Connection Issues:
- Check SSL certificates are in correct location
- Verify KAFKA_BOOTSTRAP_SERVERS format
- Ensure Aiven Kafka is running

### Database Connection Issues:
- Verify PostgreSQL credentials
- Check network connectivity
- Ensure database exists

### Consumer Issues:
- Check consumer logs
- Verify topic exists in Kafka
- Check group ID configuration
