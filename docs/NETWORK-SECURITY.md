# Azure network and perimeter design — mandatory hardening before production

## Target boundary
- 500 named users access an approved enterprise DNS hostname through **Azure Front Door Premium + WAF**, using private-link origin connectivity to Azure Container Apps, or another customer-approved managed ingress.
- Route the SPA static assets and `/api/v2/*` to their respective origins under one authorized hostname. The SPA never sends the demo tenant header.
- Keep enterprise API origin inaccessible directly from the public internet once Front Door/private endpoints are validated; verify bypass attempts fail.
- Restrict private PostgreSQL to authorized subnet/IPs and least-privilege roles. Current PostgreSQL template is private, but audit and RLS are not complete.
- Use private endpoints and restricted DNS for ACR and Key Vault; **foundation.bicep currently enables public access to bootstrap them**, which is not an acceptable production configuration.
- Enforce approved outbound egress from ACA to only corporate identity/JWKS, database, and ERP/WMS/TMS allowlisted targets using organization network controls.
- Configure managed identity access to ACR and Key Vault, with role grants scoped to the exact resource.
- Enforce TLS, WAF policies, threat intelligence, request-size limits, DDoS protections per organization policy and audit logging. Do not treat Azure-managed HTTPS as a complete WAF.

## Validation checklist
- [ ] Private-link origin deployed and approved
- [ ] WAF deny tests and false-positive tuning passed
- [ ] Direct ACA origin cannot be bypassed
- [ ] ACR and Key Vault public access denied with private DNS
- [ ] Secret rotation proven without source downtime
- [ ] ERP, WMS, TMS connectivity has enterprise-approved OAuth/identity, no shared demo bearer token
- [ ] Network policies / egress flow logs reviewed
- [ ] TLS certificate ownership and renewal documented

Microsoft reference: https://learn.microsoft.com/en-us/azure/container-apps/how-to-integrate-with-azure-front-door

The repository intentionally includes **a deployable bootstrap reference** and **this mandatory hardening plan**, rather than pretending to include a customer-specific corporate network implementation without topology, DNS or approvals.
