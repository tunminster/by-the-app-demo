#!/bin/bash
# Simple Docker run for Kafka Consumer (consumer only, no producer)

echo "🐳 Running Kafka Consumer (Simple Test)"
echo "======================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your configuration."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
required_vars=("KAFKA_BOOTSTRAP_SERVERS" "POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_HOST")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    fi
done

echo "✅ Environment variables loaded"

# Build the consumer image
echo "🔨 Building Kafka Consumer Docker image..."
docker build -f Dockerfile.consumer -t kafka-consumer:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Run the consumer container with simple test
echo "🚀 Starting Kafka Consumer container (simple test)..."
docker run -it --rm \
  --name kafka-consumer-test \
  --env-file .env \
  -v "$(pwd)/certs:/app/certs:ro" \
  -p 8082:8082 \
  kafka-consumer:latest \
  python test_kafka_simple.py

echo "✅ Test completed"
