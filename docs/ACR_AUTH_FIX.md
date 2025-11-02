# Azure Container Registry Authentication Fix

## ❌ Problem
```
Failed to pull image "bytheapp.azurecr.io/bytheappdemo-consumer:20251026.3": 
failed to authorize: failed to fetch anonymous token: 
unexpected status from GET request to https://bytheapp.azurecr.io/oauth2/token: 401 Unauthorized
```

## 🔍 Root Cause
Kubernetes cluster cannot authenticate with your private Azure Container Registry (ACR).

## ✅ Solutions

### Solution 1: Automatic Fix (Recommended)
```bash
# Run the automatic fix script
./fix_acr_auth.sh
```

### Solution 2: Manual ACR Secret Creation

#### Step 1: Get ACR Credentials
```bash
# Get ACR login server
az acr list --query "[0].loginServer" -o tsv

# Get ACR credentials
az acr credential show --name <your-acr-name>
```

#### Step 2: Create Kubernetes Secret
```bash
kubectl create secret docker-registry by-the-app-acr-secret \
  --namespace=by-the-app-prod \
  --docker-server=bytheapp.azurecr.io \
  --docker-username=<username-from-step-1> \
  --docker-password=<password-from-step-1>
```

#### Step 3: Verify Secret
```bash
kubectl get secret by-the-app-acr-secret -n by-the-app-prod
kubectl describe secret by-the-app-acr-secret -n by-the-app-prod
```

### Solution 3: Use Azure CLI to Attach ACR to AKS
```bash
# Attach ACR to AKS (gives AKS pull access to ACR)
az aks update -n <your-aks-cluster> -g <your-resource-group> --attach-acr <your-acr-name>
```

## 🔧 Files Updated

### 1. `manifests/kafka-consumer-deployment.yaml`
Added `imagePullSecrets`:
```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: by-the-app-acr-secret
      containers:
      # ... rest of config
```

### 2. `fix_acr_auth.sh`
Automatic script to create ACR secret and deploy consumer.

## 🚀 Quick Fix Commands

```bash
# Option 1: Automatic fix
./fix_acr_auth.sh

# Option 2: Manual commands
az acr credential show --name bytheapp
kubectl create secret docker-registry by-the-app-acr-secret \
  --namespace=by-the-app-prod \
  --docker-server=bytheapp.azurecr.io \
  --docker-username=<username> \
  --docker-password=<password>

# Deploy consumer
kubectl apply -f manifests/kafka-consumer-deployment.yaml
```

## 🔍 Verification

After fixing, check:
```bash
# Check if secret exists
kubectl get secret by-the-app-acr-secret -n by-the-app-prod

# Check pod status
kubectl get pods -n by-the-app-prod -l app=kafka-consumer

# Check pod events for any remaining issues
kubectl describe pod -n by-the-app-prod -l app=kafka-consumer
```

## 💡 Prevention

To prevent this in the future:
1. **Attach ACR to AKS** - `az aks update --attach-acr <acr-name>`
2. **Use managed identity** - More secure than username/password
3. **Include imagePullSecrets** - Always add to deployment manifests
