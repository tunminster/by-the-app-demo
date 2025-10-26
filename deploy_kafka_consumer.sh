#!/bin/bash
# Deploy Kafka Consumer to by-the-app-prod namespace

echo "🚀 Deploying Kafka Consumer to by-the-app-prod namespace"
echo "======================================================"

# Check if we're in the right context
echo "📋 Current Kubernetes context:"
kubectl config current-context

echo ""
echo "🔍 Checking if kafka-certs secret exists in by-the-app-prod namespace..."
kubectl get secret kafka-certs -n by-the-app-prod

if [ $? -eq 0 ]; then
    echo "✅ kafka-certs secret found in by-the-app-prod namespace"
    echo ""
    echo "🚀 Deploying Kafka Consumer with SSL..."
    kubectl apply -f manifests/kafka-consumer-deployment.yaml
    
    if [ $? -eq 0 ]; then
        echo "✅ Kafka Consumer deployed successfully!"
        echo ""
        echo "📊 Check deployment status:"
        kubectl get pods -n by-the-app-prod -l app=kafka-consumer
        echo ""
        echo "📋 View logs:"
        echo "kubectl logs -n by-the-app-prod -l app=kafka-consumer"
    else
        echo "❌ Deployment failed"
        exit 1
    fi
else
    echo "❌ kafka-certs secret not found in by-the-app-prod namespace"
    echo ""
    echo "🔧 Options:"
    echo "1. Deploy without SSL: kubectl apply -f manifests/kafka-consumer-deployment-no-ssl.yaml"
    echo "2. Create the secret first: ./generate_kafka_secret.sh"
    exit 1
fi
