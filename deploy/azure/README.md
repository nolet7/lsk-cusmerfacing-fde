# Azure infrastructure files and deployment order

| Step | File | Purpose | Production status |
| --- | --- | --- | --- |
| 1 | foundation.bicep | VNet, PostgreSQL, ACR, identity, Key Vault | Sandbox bootstrap; private ACR/KV endpoints and controls outstanding |
| 2 | migrations/001_investigations.sql | Investigation persistence | Requires controlled migration principal |
| 3 | migrations/002_delivery_exceptions.sql | Indexed exception view + refresh state | Requires controlled migration principal |
| 4 | aca-gateway.bicep | Entra-protected API on Azure Container Apps | Azure environment setup still unverified |
| 5 | exception-refresh-job.bicep | Scheduled refresh of exception index | CI syntax validation only; source contract/rate limits not validated |
| 6 | Corporate ingress / private endpoints | Azure Front Door Premium Private Link, WAF, approved DNS | **Not implemented**; see docs/NETWORK-SECURITY.md |

**Do not directly deploy these templates into production.** An infrastructure team must supply environment-specific parameter files *without secrets*, application registrations, identity federation, quotas, private endpoint architecture, WAF and approved real upstream endpoints.

The release workflow is approval-gated and intentionally validation-only until those prerequisites are available. There is no Azure tenant access in this repository.

See [docs/AZURE-ENTERPRISE-500-USERS.md](../../docs/AZURE-ENTERPRISE-500-USERS.md) and [docs/RELEASE-GATES.md](../../docs/RELEASE-GATES.md).
