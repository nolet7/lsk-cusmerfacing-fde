targetScope = 'resourceGroup'

@description('Short unique deployment identifier; used for Container Apps names')
@minLength(3)
@maxLength(18)
param prefix string

@description('Deployment region')
param location string = resourceGroup().location

@description('Existing subnet resource ID. Workload profiles environment requires dedicated suitable ACA subnet (typically /27 or larger).')
param acaSubnetId string

@description('Existing ACR login server, e.g. myregistry.azurecr.io')
param acrLoginServer string

@description('Immutable container image reference by digest, e.g. registry.azurecr.io/lsk-api@sha256:...')
param gatewayImage string

@description('Existing user-assigned managed identity resource ID. Must have AcrPull and Key Vault Secrets User roles.')
param workloadIdentityId string

@description('Azure Key Vault secret URI holding PostgreSQL DATABASE_URL. Use sslmode=verify-full.')
@secure()
param databaseUrlSecretUri string

@description('Azure Key Vault secret URI holding the internal source connector bearer token.')
@secure()
param connectorTokenSecretUri string

@description('Microsoft Entra tenant ID')
param entraTenantId string

@description('Entra protected API audience/application ID URI')
param entraAudience string

@description('Approved ERP connector base URL, via private networking')
param erpBaseUrl string
@description('Approved WMS connector base URL, via private networking')
param wmsBaseUrl string
@description('Approved TMS connector base URL, via private networking')
param tmsBaseUrl string

@minValue(2)
@maxValue(50)
param minReplicas int = 2
@minValue(2)
@maxValue(100)
param maxReplicas int = 12

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-aca'
  location: location
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: acaSubnetId
      internal: false
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: listKeys(logs.id, '2020-08-01').primarySharedKey
      }
    }
  }
}

resource gateway 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${prefix}-gateway'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${workloadIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      registries: [
        {
          server: acrLoginServer
          identity: workloadIdentityId
        }
      ]
      secrets: [
        { name: 'db-url', keyVaultUrl: databaseUrlSecretUri, identity: workloadIdentityId }
        { name: 'connector-token', keyVaultUrl: connectorTokenSecretUri, identity: workloadIdentityId }
      ]
      ingress: {
        external: true
        targetPort: 18641
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'gateway'
          image: gatewayImage
          resources: { cpu: 1.0, memory: '2Gi' }
          env: [
            { name: 'FDE_ENV', value: 'production' }
            { name: 'FDE_IDENTITY_MODE', value: 'entra' }
            { name: 'FDE_CASE_STORE', value: 'postgres' }
            { name: 'ENTRA_TENANT_ID', value: entraTenantId }
            { name: 'ENTRA_API_AUDIENCE', value: entraAudience }
            { name: 'ERP_BASE_URL', value: erpBaseUrl }
            { name: 'WMS_BASE_URL', value: wmsBaseUrl }
            { name: 'TMS_BASE_URL', value: tmsBaseUrl }
            { name: 'DATABASE_URL', secretRef: 'db-url' }
            { name: 'DEMO_CONNECTOR_TOKEN', secretRef: 'connector-token' }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 18641 }
              initialDelaySeconds: 15
              periodSeconds: 20
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: { path: '/ready', port: 18641 }
              initialDelaySeconds: 5
              periodSeconds: 10
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-concurrency'
            http: { metadata: { concurrentRequests: '20' } }
          }
        ]
      }
    }
  }
}

output gatewayFqdn string = gateway.properties.configuration.ingress.fqdn
output gatewayResourceId string = gateway.id
output logsResourceId string = logs.id
