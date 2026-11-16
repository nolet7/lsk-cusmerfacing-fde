# Enterprise deliverable index

This is the entry point for the Azure deployment readiness file set.

| Area | Primary files | Status |
| --- | --- | --- |
| CTO/business discovery | FDE-CTO-MANDATE.md; CUSTOMER-DISCOVERY-UAT.md | Fictional engagement documentation |
| Integration | app/fde_integration.py; services/mock_system.py | Tested synthetic HTTP integrations |
| Entra auth / roles | app/identity.py; tests/test_azure_security.py | Implementation; actual Entra customer config pending |
| Enterprise UI | enterprise-ui/index.html, src/main.js, package.json | Buildable MSAL SPA; hosting/SSO UAT pending |
| Cases and indexed exceptions | app/case_store.py; app/exception_store.py; migrations/001 and 002 | Code and SQL, live Azure migration pending |
| Scheduled feed | scripts/refresh_exceptions.py; deploy/azure/exception-refresh-job.bicep | Defined but live job not executed |
| Azure baseline | deploy/azure/foundation.bicep; aca-gateway.bicep | IaC compilation, actual provisioning pending |
| Perimeter | NETWORK-SECURITY.md | WAF/Private Link/ACR/KV hardening customer-specific and outstanding |
| Releases | .github/workflows/azure-validation.yml; azure-release.yml | CI validates; deploy workflow deliberately non-deploying |
| Security | SECURITY-THREAT-MODEL.md | Proposed threat mitigations, review pending |
| Database | DB-OPERATIONS.md | Role plan, restore and RLS pending |
| SLOs | OBSERVABILITY-SLOS.md; RUNBOOK-INCIDENT-RECOVERY.md | Design/runbooks, instrumentation and drills pending |
| Capacity | load/azure-500-users.js; AZURE-ENTERPRISE-500-USERS.md | 500 named-user hypothesis, live load pending |
| Signoff | RELEASE-GATES.md; IMPLEMENTATION-STATUS.md | No-go for production |

**Release rule:** Presence of file, placeholder, simulation or successful Bicep compilation is not customer deployment evidence. All incomplete enterprise artifacts remain tracked as gates.
