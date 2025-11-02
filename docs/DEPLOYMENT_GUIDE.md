# 🚀 Deployment Guide for AI Voice Assistant with Kafka

## 📋 Deployment Options

### Option 1: Direct Python Execution (Development)

```bash
# Terminal 1: Voice API
uvicorn app:app --reload

# Terminal 2: Kafka Consumer
python run_kafka_consumer.py
```

### Option 2: Using Startup Script (Recommended for Development)

```bash
# Make script executable (already done)
chmod +x start_services.sh

# Start both services
./start_services.sh
```

### Option 3: Docker Compose (Production)

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 4: Docker Individual Services

```bash
# Build consumer image
docker build -f Dockerfile.consumer -t kafka-consumer .

# Run consumer
docker run -d --name kafka-consumer \
  -e KAFKA_BOOTSTRAP_SERVERS=your-servers \
  -e POSTGRES_DB=your-db \
  -v $(pwd)/certs:/app/certs \
  kafka-consumer

# Build and run voice API
docker build -t voice-api .
docker run -d --name voice-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  voice-api
```

### Option 5: Systemd Service (Production Linux)

```bash
# Copy service file
sudo cp kafka-consumer.service /etc/systemd/system/

# Edit the service file with your paths
sudo nano /etc/systemd/system/kafka-consumer.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable kafka-consumer
sudo systemctl start kafka-consumer

# Check status
sudo systemctl status kafka-consumer

# View logs
sudo journalctl -u kafka-consumer -f
```

## 🔧 Environment Setup

### 1. Create .env file:
```bash
# Database
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your_host
POSTGRES_PORT=5432

# Kafka (Aiven)
KAFKA_BOOTSTRAP_SERVERS=kafka-12345678-12345678.aivencloud.com:12345
KAFKA_TOPIC=ai-responses
KAFKA_GROUP_ID=ai-response-processor
KAFKA_SSL_CA_FILE=./certs/ca.pem
KAFKA_SSL_CERT_FILE=./certs/service.cert
KAFKA_SSL_KEY_FILE=./certs/service.key

# OpenAI
OPENAI_API_KEY=your_openai_key
```

### 2. Download SSL certificates from Aiven:
```bash
mkdir -p certs
# Download ca.pem, service.cert, service.key to certs/ directory
```

## 📊 Monitoring

### Check Consumer Status:
```bash
# View consumer logs
tail -f kafka_consumer.log

# Check if consumer is running
ps aux | grep run_kafka_consumer

# Test Kafka connection
python -c "
from app.utils.kafka_producer import ai_response_producer
print('Kafka connection test:', ai_response_producer.producer is not None)
"
```

### Health Checks:
```bash
# Voice API health
curl http://localhost:8000/health

# Consumer health (check logs)
grep "✅" kafka_consumer.log
```

## 🚨 Troubleshooting

### Common Issues:

1. **Kafka Connection Failed**:
   - Check SSL certificates are in correct location
   - Verify KAFKA_BOOTSTRAP_SERVERS format
   - Ensure Aiven Kafka is running

2. **Database Connection Failed**:
   - Check PostgreSQL credentials
   - Verify database exists
   - Check network connectivity

3. **Consumer Not Processing Messages**:
   - Check consumer logs
   - Verify topic exists in Kafka
   - Check group ID configuration

### Debug Commands:
```bash
# Test database connection
python -c "from app.utils.db import conn; print('DB connected:', conn.closed == 0)"

# Test Kafka producer
python -c "
from app.utils.kafka_producer import ai_response_producer
result = ai_response_producer.send_ai_response('test', 'TEST', {'test': 'data'})
print('Kafka test:', result)
"
```

## 🔄 Scaling

### Multiple Consumer Instances:
```bash
# Run multiple consumers with different group IDs
KAFKA_GROUP_ID=consumer-1 python run_kafka_consumer.py &
KAFKA_GROUP_ID=consumer-2 python run_kafka_consumer.py &
```

### Load Balancing:
- Use different consumer group IDs for load balancing
- Scale horizontally with Docker Compose
- Monitor consumer lag in Kafka

## 📈 Production Recommendations

1. **Use Docker Compose** for easy orchestration
2. **Set up monitoring** with Prometheus/Grafana
3. **Use systemd** for automatic restarts
4. **Configure log rotation** for long-running services
5. **Set up health checks** for both services
6. **Use environment-specific configurations**
