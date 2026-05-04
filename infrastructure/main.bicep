@description('Resource Group Location')
param location string = resourceGroup().location

@description('App Name (lowercase, no spaces)')
param appName string = 'energyforecast'

@description('Environment (dev/staging/prod)')
param environment string = 'prod'

@description('Docker Image URI from Container Registry')
param dockerImageUri string

@description('MLflow Tracking URI')
param mlflowTrackingUri string = 'file:///app/mlruns'

// Variables
var appServicePlanName = '${appName}-plan-${environment}'
var appServiceName = '${appName}-api-${environment}'
var containerRegistryName = '${replace(appName, '-', '')}registry${environment}'
var storageAccountName = '${replace(appName, '-', '')}storage${uniqueString(resourceGroup().id)}'

// Storage Account (for MLruns / model artifacts)
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
  }
}

// App Service Plan (Linux, B1 for cost efficiency)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  kind: 'Linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
  }
}

// App Service (FastAPI Container)
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: appServiceName
  location: location
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerImageUri}'
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${containerRegistryName}.azurecr.io'
        }
        {
          name: 'DOCKER_ENABLE_CI'
          value: 'true'
        }
        {
          name: 'MLFLOW_TRACKING_URI'
          value: mlflowTrackingUri
        }
        {
          name: 'PYTHONUNBUFFERED'
          value: '1'
        }
      ]
      httpLoggingEnabled: true
      detailedErrorLoggingEnabled: true
    }
    httpsOnly: true
  }
}

// Application Insights for Monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appServiceName}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Output
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
output appServiceName string = appService.name
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output storageAccountName string = storageAccount.name
