# 🚀 Azure Deployment Guide

This guide walks you through deploying the Energy Demand Forecaster API to **Azure App Service** using Infrastructure-as-Code (Bicep) and GitHub Actions CI/CD.

## Prerequisites
- Azure subscription (free tier eligible)
- Azure CLI installed (`az --version`)
- Docker Desktop running
- GitHub account with this repo

---

## Step 1: Create Azure Resources (Local Setup)

### 1.1 Login to Azure
```bash
az login
```

### 1.2 Create Resource Group
```bash
az group create \
  --name energy-forecast-rg \
  --location eastus
```

### 1.3 Create Container Registry
```bash
az acr create \
  --resource-group energy-forecast-rg \
  --name energyforecastacr \
  --sku Basic
```

### 1.4 Deploy Infrastructure via Bicep
```bash
az deployment group create \
  --name energy-forecast-deployment \
  --resource-group energy-forecast-rg \
  --template-file infrastructure/main.bicep \
  --parameters infrastructure/parameters.json \
  --parameters appName=energyforecast environment=prod
```

This will create:
- ✅ App Service Plan (B1 tier = ~$10/month)
- ✅ App Service (Linux container host)
- ✅ Application Insights (monitoring)
- ✅ Storage Account (for model artifacts)

---

## Step 2: Build & Push Docker Image

### 2.1 Login to ACR
```bash
az acr login --name energyforecastacr
```

### 2.2 Build Docker Image
```bash
docker build -t energy-forecaster:latest .
```

### 2.3 Tag for ACR
```bash
docker tag energy-forecaster:latest energyforecastacr.azurecr.io/energy-forecaster:latest
```

### 2.4 Push to Container Registry
```bash
docker push energyforecastacr.azurecr.io/energy-forecaster:latest
```

---

## Step 3: Configure App Service

### 3.1 Enable Continuous Deployment
```bash
az webapp deployment container config \
  --name energyforecast-api-prod \
  --resource-group energy-forecast-rg \
  --enable-cd true
```

### 3.2 Set Docker Configuration
```bash
az webapp config container set \
  --name energyforecast-api-prod \
  --resource-group energy-forecast-rg \
  --docker-custom-image-name energyforecastacr.azurecr.io/energy-forecaster:latest \
  --docker-registry-server-url https://energyforecastacr.azurecr.io \
  --docker-registry-server-user <admin-username> \
  --docker-registry-server-password <admin-password>
```

*Get admin credentials:*
```bash
az acr credential show --name energyforecastacr --query "passwords[0].value" -o tsv
```

### 3.3 Configure App Settings
```bash
az webapp config appsettings set \
  --name energyforecast-api-prod \
  --resource-group energy-forecast-rg \
  --settings \
    MLFLOW_TRACKING_URI=file:///app/mlruns \
    PYTHONUNBUFFERED=1
```

---

## Step 4: Verify Deployment

### 4.1 Get App URL
```bash
az webapp show \
  --name energyforecast-api-prod \
  --resource-group energy-forecast-rg \
  --query defaultHostName -o tsv
```

### 4.2 Test Health Endpoint
```bash
curl https://<your-app-url>/health
```

Expected response:
```json
{"status": "ok", "model_loaded": true}
```

### 4.3 View Live Logs
```bash
az webapp log tail \
  --name energyforecast-api-prod \
  --resource-group energy-forecast-rg
```

---

## Step 5: Setup GitHub Actions CD (Automated)

### 5.1 Create GitHub Secrets
In your GitHub repo, go to **Settings → Secrets → New repository secret** and add:

| Secret Name | Value |
|---|---|
| `AZURE_SUBSCRIPTION_ID` | From `az account show --query id` |
| `AZURE_RESOURCE_GROUP` | `energy-forecast-rg` |
| `AZURE_APP_SERVICE_NAME` | `energyforecast-api-prod` |
| `AZURE_ACR_LOGIN_SERVER` | `energyforecastacr.azurecr.io` |
| `AZURE_ACR_USERNAME` | From `az acr credential show` |
| `AZURE_ACR_PASSWORD` | From `az acr credential show` |

### 5.2 GitHub Actions Automatically Deploys
Push to `main` branch → GitHub Actions builds Docker image → Pushes to ACR → App Service auto-updates! 🚀

---

## 📊 Monitoring & Logs

### View Application Insights
```bash
az monitor metrics list \
  --resource-group energy-forecast-rg \
  --resource-type "microsoft.insights/components" \
  --resource-namespace microsoft.insights
```

### Set Up Alerts
```bash
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group energy-forecast-rg \
  --scopes /subscriptions/{subscription-id}/resourceGroups/energy-forecast-rg/providers/microsoft.insights/components/energyforecast-api-prod-insights \
  --condition "avg HTTP 5xx > 10" \
  --window-size 5m
```

---

## 💰 Cost Estimate (Monthly)
- **App Service (B1):** ~$10
- **Container Registry:** ~$5
- **Storage Account:** ~$0.50
- **Application Insights:** ~$2
- **Total:** ~**$17.50/month**

---

## Cleanup (Optional)
```bash
az group delete --name energy-forecast-rg --yes
```

---

## Troubleshooting

### Port issues?
App Service automatically maps port 8000 → 80/443

### Model not loading?
Check logs:
```bash
az webapp log tail --name energyforecast-api-prod --resource-group energy-forecast-rg
```

### Docker pull issues?
Ensure ACR credentials are correct:
```bash
az acr login --name energyforecastacr
```
