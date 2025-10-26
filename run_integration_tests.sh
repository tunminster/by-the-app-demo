#!/bin/bash
# Integration Test Runner
# Tests the complete AI response processing flow

echo "🧪 AI Response Integration Test Suite"
echo "====================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your configuration."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "📋 Available Tests:"
echo "1. Real AI Response Test (local)"
echo "2. Docker Integration Test"
echo "3. Simple Kafka Test"
echo "4. All Tests"
echo ""

read -p "Select test (1-4): " choice

case $choice in
    1)
        echo "🧪 Running Real AI Response Test..."
        python test_integration_real_response.py
        ;;
    2)
        echo "🐳 Running Docker Integration Test..."
        python test_integration_docker.py
        ;;
    3)
        echo "📡 Running Simple Kafka Test..."
        python test_kafka_simple.py
        ;;
    4)
        echo "🚀 Running All Tests..."
        echo ""
        echo "1️⃣ Real AI Response Test..."
        python test_integration_real_response.py
        echo ""
        echo "2️⃣ Simple Kafka Test..."
        python test_kafka_simple.py
        echo ""
        echo "3️⃣ Docker Integration Test..."
        python test_integration_docker.py
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Test suite completed!"
