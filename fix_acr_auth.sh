#!/bin/bash
# Fix Azure Container Registry Authentication for Kubernetes

echo "🔐 Fixing ACR Authentication for Kubernetes"
echo "=========================================="

# Check if we're connected to the right cluster
echo "📋 Current Kubernetes context:"
kubectl config current-context

echo ""
echo "🔍 Checking if ACR secret exists in by-the-app-prod namespace..."
kubectl get secret by-the-app-acr-secret -n by-the-app-prod

if [ $? -eq 0 ]; then
    echo "✅ ACR secret already exists"
    echo ""
    echo "🔍 Checking secret details..."
    kubectl describe secret by-the-app-acr-secret -n by-the-app-prod
else
    echo "❌ ACR secret not found. Creating it..."
    echo ""
    
    # Get ACR login server
    echo "🔍 Getting ACR login server..."
    ACR_LOGIN_SERVER=$(az acr list --query "[0].loginServer" -o tsv)
    echo "ACR Login Server: $ACR_LOGIN_SERVER"
    
    # Create ACR secret
    echo "🔐 Creating ACR secret..."
    kubectl create secret docker-registry by-the-app-acr-secret \
        --namespace=by-the-app-prod \
        --docker-server=$ACR_LOGIN_SERVER \
        --docker-username=$(az acr credential show --name $(echo $ACR_LOGIN_SERVER | cut -d'.' -f1) --query "username" -o tsv) \
        --docker-password=$(az acr credential show --name $(echo $ACR_LOGIN_SERVER | cut -d'.' -f1) --query "passwords[0].value" -o tsv)
    
    if [ $? -eq 0 ]; then
        echo "✅ ACR secret created successfully!"
    else
        echo "❌ Failed to create ACR secret"
        echo ""
        echo "🔧 Manual creation steps:"
        echo "1. Get ACR credentials:"
        echo "   az acr credential show --name <your-acr-name>"
        echo ""
        echo "2. Create secret manually:"
        echo "   kubectl create secret docker-registry by-the-app-acr-secret \\"
        echo "     --namespace=by-the-app-prod \\"
        echo "     --docker-server=bytheapp.azurecr.io \\"
        echo "     --docker-username=<username> \\"
        echo "     --docker-password=<password>"
        exit 1
    fi
fi

echo ""
echo "🚀 Now deploying Kafka Consumer..."
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
