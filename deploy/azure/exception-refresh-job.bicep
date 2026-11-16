targetScope = 'resourceGroup'

@description('Unique short resource prefix')
param prefix string
param location string = resourceGroup().location
param managedEnvironmentId string
param workloadIdentityId string
param acrLoginServer string
param jobImage string
@secure()
param databaseUrlSecretUri string
@secure()
param connectorTokenSecretUri string
param erpBaseUrl string
param wmsBaseUrl string
param tmsBaseUrl string
@description('Approved customer tenant IDs. Comma separated. Never supplied by an end-user request.')
param scopeTenants string
@description('Cron schedule, UTC; default every five minutes')
param cronExpression string = '*/5 * * * *'

resource job 'Microsoft.App/jobs@2024-03-01' = {
  name: '${prefix}-exception-refresh'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${workloadIdentityId}': {}
    }
  }
  properties: {
    environmentId: managedEnvironmentId
    configuration: {
      triggerType: 'Schedule'
      replicaTimeout: 240
      replicaRetryLimit: 1
      scheduleTriggerConfig: {
        cronExpression: cronExpression
        parallelism: 1
        replicaCompletionCount: 1
      }
      registries: [
        {
          server: acrLoginServer
          identity: workloadIdentityId
        }
      ]
      secrets: [
        {
          name: 'db-url'
          keyVaultUrl: databaseUrlSecretUri
          identity: workloadIdentityId
        }
        {
          name: 'connector-token'
          keyVaultUrl: connectorTokenSecretUri
          identity: workloadIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'exception-refresh'
          image: jobImage
          command: [
            'python'
            '-m'
            'scripts.refresh_exceptions'
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'FDE_ENV', value: 'production' }
            { name: 'FDE_CASE_STORE', value: 'postgres' }
            { name: 'DATABASE_URL', secretRef: 'db-url' }
            { name: 'DEMO_CONNECTOR_TOKEN', secretRef: 'connector-token' }
            { name: 'ERP_BASE_URL', value: erpBaseUrl }
            { name: 'WMS_BASE_URL', value: wmsBaseUrl }
            { name: 'TMS_BASE_URL', value: tmsBaseUrl }
            { name: 'SCOPE_TENANTS', value: scopeTenants }
            { name: 'DB_POOL_MAX', value: '3' }
          ]
        }
      ]
    }
  }
}
output jobId string = job.id
