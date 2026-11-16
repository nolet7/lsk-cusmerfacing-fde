# Threat model and security validation

## Assets and trust boundaries
1. Browser/Entra SPA (untrusted client) -> same-origin API ingress
2. API ingress -> Entra JWKS validation -> verified customer scope and read/write roles
3. Gateway -> allowlisted external ERP/WMS/TMS system APIs
4. Gateway -> Azure PostgreSQL tenant-scoped investigation and indexed exceptions
5. Workload identity -> ACR and Key Vault secret references
6. Ingestion job -> customer-scoped source reads -> PostgreSQL index

## Threats and required mitigations
| STRIDE | Attack | Current mitigation | Before production |
| --- | --- | --- | --- |
| Spoofing | Forge X-Demo-Tenant | Demo header blocked in Azure; Entra access token verified | Real Entra claim mapping, role/group revocation tests |
| Tampering | Update records by injecting SQL | Parameterized queries, read-only connectors | Schema ACL, SQL hardening, signed images, change review |
| Repudiation | Dispute who opened investigation | DB stores case and tenant, not actor | Immutable audit with subject ID, correlation, retention |
| Information disclosure | Cross-tenant order/exception leak | Tenant parameters and token customer claim | DB RLS, penetration tests, object-level negative tests |
| Denial of service | Massive exception fan-out | Indexed feed for Azure, no per-request N+1 | Pagination, rate limits, quota/proxy/WAF |
| Elevation | Read-only actor creates case | Separate Logistics.Write app role | Approval and ownership policy tests |
| Supply-chain | Compromised image/dependencies | CI checks and Dependabot | Pin workflows to immutable SHAs, SBOM, signing, SAST/SCA |
| Secrets | Demo bearer token exposed | Key Vault reference in ACA template | Replace with per-upstream OAuth/managed identity; rotate |
| LLM | Prompt injection/exfiltration | Legacy AI route disabled in Azure mode | ACL-aware retrieval/evaluation and explicit tool boundaries if reenabled |

## Test suite ownership
- Security team: token tampering/expiry/role, tenant-claim mapping and JWT key rotation.
- Platform: direct-origin bypass, WAF enforcement, image provenance, secret rotation, egress.
- Database: RLS / statement grants / SQL injection / restore.
- FDE: customer-specific data contracts, malformed source results, out-of-order shipment events.
- SRE: load, quota exhaustion, upstream timeout/5xx, database failover and alert drill.

### Important limitation
Microsoft Entra ID does not automatically issue `customer_tenant_id`; a customer-owned claims policy or trusted token exchange must produce it. This requirement remains a blocker. This repository does not include an enterprise identity tenant or credentials.
