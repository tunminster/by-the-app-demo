#!/bin/bash
# Docker run script for Kafka Consumer on port 8082

echo "🐳 Running Kafka Consumer with Docker on port 8082"
echo "================================================="

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

# Run the consumer container with port 8082
echo "🚀 Starting Kafka Consumer container on port 8082..."
docker run -d \
  --name kafka-consumer \
  --env-file .env \
  -v $(pwd)/certs:/app/certs \
  -p 8082:8082 \
  kafka-consumer:latest

if [ $? -eq 0 ]; then
    echo "✅ Kafka Consumer started successfully!"
    echo ""
    echo "📊 Container Status:"
    docker ps | grep kafka-consumer
    echo ""
    echo "🌐 Consumer accessible at: http://localhost:8082"
    echo ""
    echo "📝 View logs:"
    echo "   docker logs -f kafka-consumer"
    echo ""
    echo "🛑 Stop consumer:"
    echo "   docker stop kafka-consumer"
    echo "   docker rm kafka-consumer"
else
    echo "❌ Failed to start Kafka Consumer"
    exit 1
fi
