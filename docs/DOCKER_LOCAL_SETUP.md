# 🐳 Docker Local Setup for Kafka Consumer

## 🚀 Quick Start

### 1. **Build the Consumer Image**
```bash
docker build -f Dockerfile.consumer -t kafka-consumer:latest .
```

### 2. **Run the Consumer Container**
```bash
docker run -d \
  --name kafka-consumer \
  --env-file .env \
  -v $(pwd)/certs:/app/certs \
  kafka-consumer:latest
```

### 3. **Check Status**
```bash
# View running containers
docker ps | grep kafka-consumer

# View logs
docker logs -f kafka-consumer

# Check container details
docker inspect kafka-consumer
```

## 🔧 **Manual Setup Steps**

### **Step 1: Prepare Environment**
```bash
# Make sure you have .env file with:
KAFKA_BOOTSTRAP_SERVERS=kafka-303b4b86-ragibull-4628.k.aivencloud.com:28372
KAFKA_SSL_CA_FILE=/app/certs/ca.pem
KAFKA_SSL_CERT_FILE=/app/certs/service.cert
KAFKA_SSL_KEY_FILE=/app/certs/service.key
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your_host
POSTGRES_PORT=5432
```

### **Step 2: Prepare Certificates**
```bash
# Make sure your certs are in ./certs/ directory
ls -la certs/
# Should show: ca.pem, service.cert, service.key
```

### **Step 3: Build and Run**
```bash
# Build image
docker build -f Dockerfile.consumer -t kafka-consumer:latest .

# Run container
docker run -d \
  --name kafka-consumer \
  --env-file .env \
  -v $(pwd)/certs:/app/certs \
  kafka-consumer:latest
```

## 📊 **Monitoring Commands**

### **View Logs**
```bash
# Follow logs in real-time
docker logs -f kafka-consumer

# View last 100 lines
docker logs --tail 100 kafka-consumer

# View logs with timestamps
docker logs -t kafka-consumer
```

### **Container Management**
```bash
# Stop consumer
docker stop kafka-consumer

# Start consumer
docker start kafka-consumer

# Restart consumer
docker restart kafka-consumer

# Remove container
docker rm kafka-consumer

# Remove image
docker rmi kafka-consumer:latest
```

### **Debug Container**
```bash
# Enter container shell
docker exec -it kafka-consumer /bin/bash

# Check environment variables
docker exec kafka-consumer env | grep KAFKA

# Check if certificates are mounted
docker exec kafka-consumer ls -la /app/certs/
```

## 🧪 **Testing**

### **Send Test Message**
```bash
# Run quick test to send message
python tests/kafka/quick_test.py
```

### **Check Consumer Processing**
```bash
# View consumer logs
docker logs -f kafka-consumer

# Should see messages like:
# ✅ Message sent to topic ai-responses partition 0 offset 123
# 📨 Processing message: PATIENT_CREATION for call test-123
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Container won't start**:
   ```bash
   docker logs kafka-consumer
   ```

2. **Kafka connection failed**:
   - Check KAFKA_BOOTSTRAP_SERVERS
   - Verify certificates are mounted
   - Check network connectivity

3. **Database connection failed**:
   - Check POSTGRES_* variables
   - Verify database is accessible

4. **Certificate issues**:
   ```bash
   # Check certificates are mounted
   docker exec kafka-consumer ls -la /app/certs/
   
   # Check certificate permissions
   docker exec kafka-consumer ls -la /app/certs/ca.pem
   ```

### **Clean Restart**
```bash
# Stop and remove container
docker stop kafka-consumer
docker rm kafka-consumer

# Rebuild and run
docker build -f Dockerfile.consumer -t kafka-consumer:latest .
docker run -d --name kafka-consumer --env-file .env -v $(pwd)/certs:/app/certs kafka-consumer:latest
```

## 🎯 **Production vs Local**

### **Local Development**:
- Uses Docker Desktop
- Single container
- Easy debugging
- Manual management

### **Production (Kubernetes)**:
- Uses Kubernetes deployment
- Multiple replicas
- Auto-scaling
- Managed by Azure Pipeline
