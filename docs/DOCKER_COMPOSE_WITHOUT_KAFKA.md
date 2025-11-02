# Running Without Kafka Consumer

## What Changed

The Kafka consumer service has been commented out in `docker-compose.yml` for testing purposes.

## What Will Work ✅

- ✅ Voice API service (listening on port 8000)
- ✅ Authentication endpoints (`/auth/login`, `/auth/register`)
- ✅ All API endpoints (dentists, patients, appointments, etc.)
- ✅ Database operations

## What Won't Work ❌

- ❌ AI response processing (no Kafka consumer to process messages)
- ❌ Patient creation automation (requires Kafka)
- ❌ Booking confirmation automation (requires Kafka)
- ❌ Kafka message processing

## Running the Service

### Start Voice API Only
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f voice-api
```

### Stop the Service
```bash
docker-compose down
```

## Testing Authentication

With Kafka commented out, you can test authentication:

```bash
# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Should return JWT token
```

## Re-enabling Kafka Consumer

When you want Kafka consumer back:

1. **Uncomment** the `kafka-consumer` section in `docker-compose.yml`
2. **Uncomment** the `depends_on` line in voice-api service
3. **Restart** services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

Or simply search/replace in the file:
- Replace `# kafka-consumer:` with `kafka-consumer:`
- Uncomment all lines in that section
- Uncomment the `depends_on` section

## Use Case

This is useful when:
- ✅ Testing authentication without Kafka complexity
- ✅ Debugging API endpoints independently
- ✅ Faster startup during development
- ✅ Reducing resource usage

## Expected Logs

When running without Kafka, you should see:

```
✅ Bcrypt is working correctly
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Started server process
```

But any messages sent to Kafka will just queue up in Kafka and not be processed.
