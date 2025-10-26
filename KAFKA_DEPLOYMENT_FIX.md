# Kafka Consumer Deployment Fix

## ❌ Problem
The deployment fails with: `spec.template.spec.containers[0].volumeMounts[0].name: Not found: "kafka-certs"`

This happens because the Kubernetes secret `kafka-certs` doesn't exist in your cluster.

## ✅ Solutions

### Option 1: Create SSL Secret (Recommended for Production)

1. **Generate the secret from your certificates:**
   ```bash
   ./generate_kafka_secret.sh
   ```

2. **Deploy the consumer:**
   ```bash
   kubectl apply -f manifests/kafka-consumer-deployment.yaml
   ```

### Option 2: Use Non-SSL Configuration (For Testing)

1. **Deploy without SSL:**
   ```bash
   kubectl apply -f manifests/kafka-consumer-deployment-no-ssl.yaml
   ```

2. **Update your Kafka configuration** to use PLAINTEXT instead of SSL.

### Option 3: Manual Secret Creation

If you prefer to create the secret manually:

1. **Encode your certificates:**
   ```bash
   # Encode each certificate file
   base64 -i certs/ca.pem
   base64 -i certs/service.cert
   base64 -i certs/service.key
   ```

2. **Create the secret YAML:**
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: kafka-certs
     namespace: default
   type: Opaque
   data:
     ca.pem: <base64-encoded-ca.pem>
     service.cert: <base64-encoded-service.cert>
     service.key: <base64-encoded-service.key>
   ```

3. **Apply the secret:**
   ```bash
   kubectl apply -f kafka-certs-secret.yaml
   ```

## 🔍 Verification

After deploying, check the status:

```bash
# Check if secret exists
kubectl get secret kafka-certs

# Check consumer pods
kubectl get pods -l app=kafka-consumer

# View logs
kubectl logs -l app=kafka-consumer
```

## 📋 Files Created

- `manifests/kafka-certs-secret.yaml` - Kubernetes secret template
- `manifests/kafka-consumer-deployment-no-ssl.yaml` - Non-SSL deployment
- `generate_kafka_secret.sh` - Script to generate secret from certificates
- Updated `app/utils/kafka_consumer.py` - Handles both SSL and non-SSL

## 🚀 Quick Fix

For immediate deployment, use the non-SSL version:

```bash
kubectl apply -f manifests/kafka-consumer-deployment-no-ssl.yaml
```

This will work if your Kafka setup supports PLAINTEXT connections.
