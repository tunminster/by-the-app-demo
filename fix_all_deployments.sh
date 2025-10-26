#!/bin/bash
# Fix All Deployment Issues - ACR Auth, Namespaces, etc.

echo "🔧 Fixing All Deployment Issues"
echo "=============================="

# Check if we're connected to the right cluster
echo "📋 Current Kubernetes context:"
kubectl config current-context

echo ""
echo "🔍 Checking current namespace..."
kubectl config view --minify --output 'jsonpath={..namespace}'

echo ""
echo "🔐 Step 1: Fixing ACR Authentication..."

# Check if ACR secret exists
kubectl get secret by-the-app-acr-secret -n by-the-app-prod > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ ACR secret already exists"
else
    echo "❌ ACR secret not found. Creating it..."
    
    # Get ACR login server
    ACR_LOGIN_SERVER=$(az acr list --query "[0].loginServer" -o tsv 2>/dev/null)
    if [ -z "$ACR_LOGIN_SERVER" ]; then
        echo "❌ Could not get ACR login server. Please run:"
        echo "   az login"
        echo "   az acr list --query '[0].loginServer' -o tsv"
        exit 1
    fi
    
    echo "ACR Login Server: $ACR_LOGIN_SERVER"
    
    # Get ACR name (remove .azurecr.io)
    ACR_NAME=$(echo $ACR_LOGIN_SERVER | cut -d'.' -f1)
    
    # Create ACR secret
    echo "🔐 Creating ACR secret..."
    kubectl create secret docker-registry by-the-app-acr-secret \
        --namespace=by-the-app-prod \
        --docker-server=$ACR_LOGIN_SERVER \
        --docker-username=$(az acr credential show --name $ACR_NAME --query "username" -o tsv) \
        --docker-password=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
    
    if [ $? -eq 0 ]; then
        echo "✅ ACR secret created successfully!"
    else
        echo "❌ Failed to create ACR secret"
        echo "Please create it manually:"
        echo "kubectl create secret docker-registry by-the-app-acr-secret \\"
        echo "  --namespace=by-the-app-prod \\"
        echo "  --docker-server=bytheapp.azurecr.io \\"
        echo "  --docker-username=<username> \\"
        echo "  --docker-password=<password>"
        exit 1
    fi
fi

echo ""
echo "🔍 Step 2: Checking kafka-certs secret..."
kubectl get secret kafka-certs -n by-the-app-prod > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ kafka-certs secret exists"
else
    echo "❌ kafka-certs secret not found"
    echo "Please run: ./generate_kafka_secret.sh"
    exit 1
fi

echo ""
echo "🚀 Step 3: Deploying Kafka Consumer..."
kubectl apply -f manifests/kafka-consumer-deployment.yaml

if [ $? -eq 0 ]; then
    echo "✅ Kafka Consumer deployed successfully!"
else
    echo "❌ Kafka Consumer deployment failed"
    exit 1
fi

echo ""
echo "🚀 Step 4: Deploying Main API..."
kubectl apply -f manifests/deployment.yml

if [ $? -eq 0 ]; then
    echo "✅ Main API deployed successfully!"
else
    echo "❌ Main API deployment failed"
    exit 1
fi

echo ""
echo "📊 Step 5: Checking deployment status..."
echo ""
echo "🔍 Kafka Consumer:"
kubectl get pods -n by-the-app-prod -l app=kafka-consumer

echo ""
echo "🔍 Main API:"
kubectl get pods -n by-the-app-prod -l app=by-the-app-api-demo

echo ""
echo "🎉 All deployments completed!"
echo ""
echo "📋 Useful commands:"
echo "  View logs: kubectl logs -n by-the-app-prod -l app=kafka-consumer"
echo "  Check events: kubectl get events -n by-the-app-prod"
echo "  Describe pod: kubectl describe pod -n by-the-app-prod <pod-name>"
