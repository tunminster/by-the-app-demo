# Azure Pipeline Troubleshooting Guide

## ❌ Problem: kubectl connection refused

**Error:**
```
The connection to the server localhost:8080 was refused - did you specify the right host or port?
```

## 🔍 Root Cause
The `kubectl` commands in the pipeline are trying to connect to `localhost:8080` instead of your actual Azure Kubernetes Service cluster.

## ✅ Solutions

### Solution 1: Use Kubernetes Tasks (Recommended)
The updated `azure-pipelines-consumer.yml` now uses Kubernetes tasks for all kubectl operations:

```yaml
- task: Kubernetes@1
  displayName: 'Wait for consumer deployment to be ready'
  inputs:
    connectionType: 'Kubernetes Service Connection'
    kubernetesServiceEndpoint: 'by-the-app-cluster'
    namespace: 'by-the-app-prod'
    command: 'wait'
    arguments: '--for=condition=available --timeout=300s deployment/kafka-consumer'
```

### Solution 2: Use Azure CLI (Alternative)
If Solution 1 doesn't work, use the alternative pipeline:

```bash
# Use the alternative pipeline
azure-pipelines-consumer-alternative.yml
```

This uses Azure CLI to configure kubectl properly:
```yaml
- task: AzureCLI@2
  inputs:
    azureSubscription: 'containerRegistry'
    scriptType: 'bash'
    inlineScript: |
      az aks get-credentials --resource-group $(AKS_RESOURCE_GROUP) --name $(AKS_CLUSTER_NAME) --overwrite-existing
      kubectl apply -f deployment.yaml
```

## 🔧 Required Azure DevOps Configuration

### 1. Kubernetes Service Connection
Ensure you have a service connection named `by-the-app-cluster` configured in Azure DevOps.

### 2. Variable Groups
Make sure the `bytheapp-demo` variable group contains:
- `AKS_RESOURCE_GROUP` - Your AKS resource group
- `AKS_CLUSTER_NAME` - Your AKS cluster name
- `containerRegistry` - Your Azure Container Registry connection

### 3. Container Registry
Ensure `containerRegistry` service connection is properly configured.

## 🚀 Quick Fix

If you need to deploy immediately:

```bash
# Deploy manually using Azure CLI
az aks get-credentials --resource-group <your-resource-group> --name <your-cluster-name>
kubectl apply -f manifests/kafka-consumer-deployment.yaml
```

## 🔍 Verification

After successful deployment:

```bash
# Check deployment
kubectl get deployment kafka-consumer -n by-the-app-prod

# Check pods
kubectl get pods -l app=kafka-consumer -n by-the-app-prod

# Check logs
kubectl logs -l app=kafka-consumer -n by-the-app-prod
```

## 📋 Files Updated

- `azure-pipelines-consumer.yml` - Fixed kubectl context issues
- `azure-pipelines-consumer-alternative.yml` - Alternative using Azure CLI
- `AZURE_PIPELINE_TROUBLESHOOTING.md` - This troubleshooting guide
