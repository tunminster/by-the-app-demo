#!/bin/bash
# Run dental-voice-app with all environment variables

docker run -d \
  --name dental-voice-app \
  -p 8080:8080 \
  -e POSTGRES_DB="${POSTGRES_DB}" \
  -e POSTGRES_USER="${POSTGRES_USER}" \
  -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  -e POSTGRES_HOST="${POSTGRES_HOST}" \
  -e POSTGRES_PORT="${POSTGRES_PORT}" \
  -e JWT_SECRET_KEY="${JWT_SECRET_KEY:-your-secret-key-change-this-in-production}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS}" \
  -e KAFKA_TOPIC="${KAFKA_TOPIC}" \
  dental-voice-app:latest

echo "Container started. View logs with: docker logs -f dental-voice-app"
