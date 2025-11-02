# Docker Run vs Docker Compose

## Your Command
```bash
docker run -d --name dental-voice-app -p 8080:8080 dental-voice-app:latest
```

## Problems with This Approach

### ❌ Missing Environment Variables
Your container needs these environment variables to function:
- `POSTGRES_*` variables (database connection)
- `JWT_SECRET_KEY` (authentication)
- `OPENAI_API_KEY` (AI functionality)
- `KAFKA_*` variables (message queue)

### ❌ Missing Dependencies
Your app depends on:
- Kafka Consumer service (runs separately)
- Database connection
- SSL certificates for Kafka

### ❌ No Easy Management
- Hard to start/stop multiple services
- No networking between containers
- Manual cleanup required

## Better Options

### Option 1: Use `run_dental_voice.sh` (I just created it)
```bash
# Load environment variables
source .env

# Run the script
./run_dental_voice.sh

# View logs
docker logs -f dental-voice-app

# Stop and remove
docker stop dental-voice-app && docker rm dental-voice-app
```

**Still missing:** Kafka consumer won't be running!

### Option 2: Docker Compose (Recommended) ✅
```bash
# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f voice-api

# Stop everything
docker-compose down
```

**Benefits:**
- ✅ Starts both voice-api AND kafka-consumer
- ✅ All environment variables automatically loaded
- ✅ Proper networking between services
- ✅ Easy to manage

## Complete Comparison

| Feature | Docker Run | Docker Compose |
|---------|-----------|----------------|
| Environment Variables | Manual `-e` flags | Automatic from `.env` |
| Multiple Services | Run separately | All together |
| Networking | Manual setup | Automatic |
| Volumes (SSL certs) | Manual mount | Automatic |
| Dependencies | Manual start order | Automatic ordering |
| Cleanup | Manual stop/rm | Single command |

## Which Should You Use?

### Use `docker run` when:
- ✅ Quick testing of a single service
- ✅ You understand all dependencies
- ✅ You're just testing locally

### Use `docker-compose` when:
- ✅ **Development** (what you're doing now) ✅
- ✅ Multi-service application
- ✅ Need environment management
- ✅ Want easy startup/shutdown

## Recommendation for Your Project

**Use Docker Compose** because:

1. You have **two services** (voice-api + kafka-consumer)
2. They **depend on each other**
3. You need **consistent environment** across services
4. It's **easier to manage**

## Quick Commands

### Docker Compose (Recommended)
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Restart after code changes
docker-compose restart voice-api

# Stop everything
docker-compose down
```

### Docker Run (For Testing)
```bash
# Build image
docker build -t dental-voice-app:latest .

# Run with script
./run_dental_voice.sh

# View logs
docker logs -f dental-voice-app
```
