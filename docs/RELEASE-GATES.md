# Enterprise release gates — evidence ledger

This checklist is **not approval**. Only named customer/platform owners can sign and authorize launch.

| Gate | Evidence required | Status |
| --- | --- | --- |
| G0 discovery | Approved CTO mandate, interview notes, owners, real contract mappings | Simulation only |
| G1 POC | Four-service smoke tests, API contracts, negative tenant tests, demos | Existing synthetic CI; check branch Actions |
| G2 identity | Entra app registrations, access-token roles, custom tenant claim issuance, MFA/Conditional Access, role revocation | Code scaffold only; customer config missing |
| G3 real integration | Authorized ERP/WMS/TMS sandbox endpoints, change data ownership, contract/load/rate limit tests | Missing |
| G4 persistence | Both migrations in Azure PG, least-privilege runtime/ingestion roles, RLS decision, backup/restore | Scripts only |
| G5 exceptions | Scheduled indexed feed, successful empty-result refresh, freshness SLO, poison-data handling | Code/Job template; not deployed or run on Azure |
| G6 frontend | SPA build, OIDC E2E, accessible UAT, same-origin API routing | SPA scaffold only |
| G7 cloud boundary | ACR/Key Vault private endpoints, ingress Front Door Premium/WAF, verified no direct origin, egress | Requires corporate network design |
| G8 observability | SLO burn-rate, per-upstream latency, traces/log sampling, alert tests, on-call | Documents/templates only |
| G9 resiliency | Load, 500 concurrency stretch, chaos, recovery, restore and rollback drills | k6 script only |
| G10 launch | Security approval, change request, customer UAT, signoff and support contract | No evidence |
| G11 handover | Runbooks, RACI, escalation training, monitoring ownership, support exercises | Templates only |

## Mandatory proof package (never fabricate)
For each gate store an authorized external evidence URL, reviewer, date/time, commit digest, environment, test sample size, test result, and any exception risk acceptance in the organization's change-management system. Do not store secrets, customer PII or raw bearer tokens in GitHub.

Use a controlled manual release process. `.github/workflows/azure-release.yml` currently authenticates via OIDC and validates, but **deliberately does not deploy to Azure** until environment-specific approved configuration and prerequisites are supplied.

## Go/no-go meeting notes template

- Release candidate SHA / immutable digest:
- Environment / region / subscription:
- Business owner:
- Security owner:
- SRE owner:
- Data owner:
- Baseline throughput / pilot cohort:
- Measured p95/p99 / source freshness:
- Restore RPO/RTO achieved:
- SLO and alert drill:
- Open vulnerabilities and risk acceptance:
- Rollback result:
- Approved decision / timestamp:

**Current decision: NO-GO for production.**
