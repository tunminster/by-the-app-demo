# Kafka Consumer Azure Pipeline Setup

## 🎯 Overview

This guide helps you set up a separate Azure Pipeline for the Kafka Consumer deployment.

## 📁 Files Created

- `azure-pipelines-consumer.yml` - Separate pipeline for Kafka consumer
- `manifests/kafka-consumer-deployment.yaml` - Kubernetes deployment for consumer
- `Dockerfile.consumer` - Docker image for consumer

## 🚀 Pipeline Setup Steps

### 1. Create New Pipeline in Azure DevOps

1. Go to your Azure DevOps project
2. Navigate to **Pipelines** → **New Pipeline**
3. Select your repository source
4. Choose **Existing Azure Pipelines YAML file**
5. Select `azure-pipelines-consumer.yml` from the root directory

### 2. Configure Pipeline Variables

Add these variables to your pipeline (or variable group `bytheapp-demo`):

```yaml
# Required Variables
repository-image: bytheapp.azurecr.io/bytheappdemo-consumer:$(Build.BuildNumber)
postgres-host: your-postgres-host
postgres-port: 5432
kafka-bootstrap-servers: your-kafka-servers
kafka-topic: ai-responses
kafka-group-id: ai-response-processor
```

### 3. Update Variable Group

Add these to your `bytheapp-demo` variable group:

```bash
# Database Configuration
postgres-host: your-postgres-host
postgres-port: 5432

# Kafka Configuration  
kafka-bootstrap-servers: your-kafka-servers
kafka-topic: ai-responses
kafka-group-id: ai-response-processor
```

### 4. Create Kafka Certificates Secret

Create the Kafka certificates secret in your cluster:

```bash
kubectl create secret generic kafka-certs \
  --from-file=ca.pem=./certs/ca.pem \
  --from-file=service.cert=./certs/service.cert \
  --from-file=service.key=./certs/service.key \
  -n by-the-app-prod
```

## 🔄 Pipeline Flow

### Build Stage:
1. Install Python dependencies
2. Validate consumer code

### Deploy Stage:
1. Build Docker image using `Dockerfile.consumer`
2. Push to Azure Container Registry
3. Replace tokens in deployment YAML
4. Deploy to Kubernetes cluster
5. Wait for deployment to be ready
6. Verify deployment status

## 📊 Monitoring

### Check Consumer Status:
```bash
# View consumer pods
kubectl get pods -l app=kafka-consumer -n by-the-app-prod

# View consumer logs
kubectl logs -l app=kafka-consumer -n by-the-app-prod -f

# Check deployment status
kubectl get deployment kafka-consumer -n by-the-app-prod
```

### Scale Consumer:
```bash
# Scale consumer replicas
kubectl scale deployment kafka-consumer --replicas=3 -n by-the-app-prod
```

## 🔧 Troubleshooting

### Common Issues:

1. **Image Pull Errors**:
   - Check ACR credentials
   - Verify image exists in registry

2. **Consumer Not Starting**:
   - Check environment variables
   - Verify Kafka connectivity
   - Check SSL certificates

3. **Database Connection Issues**:
   - Verify PostgreSQL credentials
   - Check network connectivity

### Debug Commands:
```bash
# Check consumer logs
kubectl logs -l app=kafka-consumer -n by-the-app-prod

# Describe consumer pod
kubectl describe pod -l app=kafka-consumer -n by-the-app-prod

# Check secrets
kubectl get secret kafka-certs -n by-the-app-prod -o yaml
```

## 🎯 Benefits

- ✅ **Independent deployment** from voice API
- ✅ **Separate scaling** based on message load
- ✅ **Independent updates** without affecting API
- ✅ **Better resource management**
- ✅ **Fault isolation**

## 📈 Next Steps

1. **Set up monitoring** for consumer metrics
2. **Configure auto-scaling** based on message lag
3. **Set up alerts** for consumer failures
4. **Monitor Kafka topic** for message flow
