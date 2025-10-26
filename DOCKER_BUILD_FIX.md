# Docker Build - Getting Latest Code

## Problem
Docker containers not reflecting the latest code changes.

## Solution Options

### Option 1: Development Mode (Recommended for Active Development)
The `docker-compose.yml` has been updated to mount your source code as a volume.

**Build once, then just restart:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**After that, just restart when you change code:**
```bash
docker-compose restart voice-api
```

✅ **Code changes are picked up automatically** (no rebuild needed)

### Option 2: Full Rebuild (Production-like)
If you want to test the production build process:

```bash
# Stop containers
docker-compose down

# Build with no cache
docker-compose build --no-cache

# Start
docker-compose up -d

# View logs
docker-compose logs -f voice-api
```

### Option 3: Manual Docker Build (Alternative)
Use your manual build command:

```bash
# Build image
docker build -f Dockerfile -t dental-voice-app:latest .

# Run container
docker run -d \
  -p 8000:8080 \
  --name dental-voice \
  --env-file .env \
  dental-voice-app:latest
```

## Verify Latest Code is Running

### Check the logs:
```bash
docker-compose logs voice-api | grep "Bcrypt"
```

You should see:
```
✅ Bcrypt is working correctly
```

### Check file timestamps in container:
```bash
docker-compose exec voice-api ls -la /app/app/routes/auth.py
```

Compare the modification time with your local file.

## Troubleshooting

### Still seeing old code?

1. **Force remove old containers:**
   ```bash
   docker-compose down -v  # Removes volumes too
   ```

2. **Remove old images:**
   ```bash
   docker rmi by-the-app-demo-voice-api by-the-app-demo-kafka-consumer
   ```

3. **Rebuild everything:**
   ```bash
   docker-compose build --no-cache --pull
   docker-compose up -d
   ```

### Check if code is being copied:
```bash
# Check what's in the container
docker-compose exec voice-api cat /app/app/routes/auth.py | head -30
```

Compare with your local file to ensure they match.

## Best Practice

For **development**, use Option 1 (volume mount) - fastest iteration.

For **testing production builds**, use Option 2 (full rebuild with --no-cache).

For **Kubernetes deployment**, use Azure Pipelines which will handle the build process.
