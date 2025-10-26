#!/bin/bash
# Generate Kafka Certificates Secret for Kubernetes

echo "🔐 Generating Kafka Certificates Secret"
echo "======================================"

# Check if certs directory exists
if [ ! -d "certs" ]; then
    echo "❌ certs directory not found. Please ensure your Kafka certificates are in the certs/ directory."
    exit 1
fi

# Check if required certificate files exist
required_files=("ca.pem" "service.cert" "service.key")
for file in "${required_files[@]}"; do
    if [ ! -f "certs/$file" ]; then
        echo "❌ Required certificate file not found: certs/$file"
        exit 1
    fi
done

echo "✅ All required certificate files found"
echo ""

# Create the secret YAML file
echo "📝 Creating kafka-certs-secret.yaml..."

cat > manifests/kafka-certs-secret.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: kafka-certs
  namespace: by-the-app-prod
type: Opaque
data:
  ca.pem: $(base64 -i certs/ca.pem | tr -d '\n')
  service.cert: $(base64 -i certs/service.cert | tr -d '\n')
  service.key: $(base64 -i certs/service.key | tr -d '\n')
EOF

echo "✅ Secret file created: manifests/kafka-certs-secret.yaml"
echo ""

# Apply the secret to Kubernetes
echo "🚀 Applying secret to Kubernetes..."
kubectl apply -f manifests/kafka-certs-secret.yaml

if [ $? -eq 0 ]; then
    echo "✅ Kafka certificates secret created successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Deploy the kafka-consumer: kubectl apply -f manifests/kafka-consumer-deployment.yaml"
    echo "2. Check the deployment: kubectl get pods -l app=kafka-consumer"
    echo "3. View logs: kubectl logs -l app=kafka-consumer"
else
    echo "❌ Failed to create secret. Please check your Kubernetes connection."
    exit 1
fi
