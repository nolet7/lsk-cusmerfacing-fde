# Enterprise deliverable status — Azure 500 named users

The repository now contains code and files for every major enterprise workstream. **A present file is not proof of a configured customer system or live operational acceptance.**

| Workstream | File evidence | Implementation status |
| --- | --- | --- |
| CTO mandate / discovery | FDE-CTO-MANDATE, CUSTOMER-DISCOVERY-UAT | Simulated artifacts |
| Read-only ERP/WMS/TMS integration | services/mock_system.py, app/fde_integration.py | Working synthetic HTTP POC; real adapters pending |
| Enterprise API identity | app/identity.py, tests/test_azure_security.py | JWT verification code; Entra registration and trusted custom-claim issuance pending |
| Enterprise web UI | enterprise-ui/ | Buildable MSAL SPA; deployment, corporate proxy and real auth E2E pending |
| Cases | app/case_store.py, migrations/001_investigations.sql | PG code/migration; live DB and audits pending |
| Exception feed | app/exception_store.py, migrations/002_delivery_exceptions.sql, scripts/refresh_exceptions.py | Indexed feed and scheduled refresh code; Azure ingestion deployment pending |
| Compute/IaC | deploy/azure/foundation.bicep, aca-gateway.bicep | Bicep compilation checks; Azure provisioning not done |
| Ingestion job | deploy/azure/exception-refresh-job.bicep | Bicep compiled by CI; execution pending |
| Network/WAF | docs/NETWORK-SECURITY.md | Customer-specific implementation not possible without topology, approvals and subscription |
| Security/threat model | docs/SECURITY-THREAT-MODEL.md | Threat catalog and negative tests, formal review pending |
| Observability | docs/OBSERVABILITY-SLOS.md | Design and query examples, live instrumentation/dashboards pending |
| CI / release | .github/workflows/azure-validation.yml, azure-release.yml | Validation workflow; release deliberately does not deploy |
| 500 named-user capacity | load/azure-500-users.js | Load script; 50 VU nominal and 500 concurrent stress not executed |
| Runbooks | docs/RUNBOOK-INCIDENT-RECOVERY.md, DB-OPERATIONS.md | Prepared templates; restore/failover/on-call drill pending |
| Go-live | docs/RELEASE-GATES.md | No-go until customer-specific evidence and signoff |

## Required inputs for production completion
An approved Azure subscription and region, VNet/DNS/egress architecture, source API contracts/credentials, Entra app registrations, customer tenant authorization source, database roles and secrets, CI OIDC federation, governance ownership, real representative workloads, approved monitoring destinations and UAT signatories.

This branch is a **deployable reference candidate and testable synthetic integration**, not a verified 500-user production service.
