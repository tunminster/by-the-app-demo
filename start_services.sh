#!/bin/bash

# Start Services Script for AI Voice Assistant with Kafka

echo "🚀 Starting AI Voice Assistant with Kafka Consumer..."

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

# Function to start services
start_services() {
    echo "🔄 Starting services..."
    
    # Start Kafka Consumer in background
    echo "📨 Starting Kafka Consumer..."
    nohup python run_kafka_consumer.py > kafka_consumer.log 2>&1 &
    CONSUMER_PID=$!
    echo "✅ Kafka Consumer started with PID: $CONSUMER_PID"
    
    # Start Voice API
    echo "🎤 Starting Voice API..."
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    if [ ! -z "$CONSUMER_PID" ]; then
        kill $CONSUMER_PID
        echo "✅ Kafka Consumer stopped"
    fi
    exit 0
}

# Set up signal handlers
trap stop_services SIGINT SIGTERM

# Start services
start_services
