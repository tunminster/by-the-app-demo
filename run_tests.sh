#!/bin/bash
# Test runner script for AI Voice Assistant

echo "🧪 AI Voice Assistant Test Runner"
echo "================================="

# Check if we're in the right directory
if [ ! -d "tests" ]; then
    echo "❌ Please run from project root directory"
    exit 1
fi

# Function to run tests
run_tests() {
    local test_type=$1
    
    case $test_type in
        "quick")
            echo "⚡ Running Quick Kafka Test..."
            python tests/kafka/quick_test.py
            ;;
        "kafka")
            echo "🔌 Running Kafka Tests..."
            python tests/kafka/test_producer.py
            echo ""
            python tests/kafka/test_consumer.py
            ;;
        "database")
            echo "🗄️ Running Database Tests..."
            python tests/database/test_db_connection.py
            ;;
        "voice")
            echo "🎤 Running Voice Integration Tests..."
            python tests/voice/test_voice_integration.py
            ;;
        "all")
            echo "🚀 Running All Tests..."
            python tests/kafka/test_producer.py
            echo ""
            python tests/kafka/test_consumer.py
            echo ""
            python tests/database/test_db_connection.py
            echo ""
            python tests/voice/test_voice_integration.py
            ;;
        *)
            echo "❌ Unknown test type: $test_type"
            echo "Available: quick, kafka, database, voice, all"
            exit 1
            ;;
    esac
}

# Main execution
if [ $# -eq 0 ]; then
    echo "Usage: $0 [quick|kafka|database|voice|all]"
    echo ""
    echo "Examples:"
    echo "  $0 quick     # Quick Kafka connection test"
    echo "  $0 kafka     # All Kafka tests"
    echo "  $0 database  # Database tests"
    echo "  $0 voice     # Voice integration tests"
    echo "  $0 all       # All tests"
    exit 1
fi

run_tests $1
