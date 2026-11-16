// Vite injects public (nonsecret) Entra application configuration at build time.
// Both SPA app registration and API registration must be provisioned by IAM.
export const config = {
  tenantId: import.meta.env.VITE_ENTRA_TENANT_ID,
  clientId: import.meta.env.VITE_ENTRA_SPA_CLIENT_ID,
  apiScope: import.meta.env.VITE_ENTRA_API_SCOPE,
  // Same-origin /api/v2 via approved Front Door or corporate reverse proxy.
  apiBase: import.meta.env.VITE_API_BASE || "",
};
for (const [key,value] of Object.entries(config)) {
  if (key !== 'apiBase' && !value) throw new Error('Missing enterprise UI config: '+key);
}
if (config.apiBase && !config.apiBase.startsWith('/')) {
  throw new Error('VITE_API_BASE must be a same-origin relative path');
}
