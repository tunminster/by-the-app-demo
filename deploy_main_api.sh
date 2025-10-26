#!/bin/bash
# Deploy Main API to by-the-app-prod namespace

echo "🚀 Deploying Main API to by-the-app-prod namespace"
echo "================================================"

# Check if we're in the right context
echo "📋 Current Kubernetes context:"
kubectl config current-context

echo ""
echo "🔍 Checking if kafka-certs secret exists in by-the-app-prod namespace..."
kubectl get secret kafka-certs -n by-the-app-prod

if [ $? -eq 0 ]; then
    echo "✅ kafka-certs secret found in by-the-app-prod namespace"
    echo ""
    echo "🚀 Deploying Main API with Kafka SSL support..."
    kubectl apply -f manifests/deployment.yml
    
    if [ $? -eq 0 ]; then
        echo "✅ Main API deployed successfully!"
        echo ""
        echo "📊 Check deployment status:"
        kubectl get pods -n by-the-app-prod -l app=by-the-app-api-demo
        echo ""
        echo "📋 View logs:"
        echo "kubectl logs -n by-the-app-prod -l app=by-the-app-api-demo"
        echo ""
        echo "🌐 Check service:"
        kubectl get svc -n by-the-app-prod -l app=by-the-app-api-demo
        echo ""
        echo "🔗 Check ingress:"
        kubectl get ingress -n by-the-app-prod
    else
        echo "❌ Deployment failed"
        exit 1
    fi
else
    echo "❌ kafka-certs secret not found in by-the-app-prod namespace"
    echo ""
    echo "🔧 Please create the secret first:"
    echo "./generate_kafka_secret.sh"
    exit 1
fi
