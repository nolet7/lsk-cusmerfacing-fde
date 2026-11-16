# Forward Deployed Engineer implementation backlog and task checklist

This backlog applies to the Azure enterprise branch. **Implemented** means source exists; only successful CI checks are verified. Azure deployment, real-user access, customer system integrations and 500-user load testing remain unverified.

| ID | Phase | Deliverable / task | Owner | Priority | Status | Acceptance evidence |
| --- | --- | --- | --- | --- | --- | --- |
| FDE-001 | Discovery | CTO mandate, personas, pain points, scope and phase gates | FDE lead | P0 | Implemented (simulated) | FDE-CTO-MANDATE.md |
| FDE-002 | Discovery | Interview logistics, ERP, warehouse and transport system owners | FDE + customer | P0 | Pending real engagement | Approved interview notes |
| FDE-003 | Discovery | Document baseline lookup time, cases/day, late-delivery error rate | Customer operations | P0 | Pending | Measurement plan and source evidence |
| FDE-004 | Design | Versioned ERP/WMS/TMS source contracts, field mapping and IDs | FDE + source owners | P0 | Implemented (synthetic) | services/mock_system.py and ADR |
| FDE-005 | Design | Sequence diagram, data flow, threat model and IAM matrix | FDE + security | P0 | Partially documented | README, design ADR; threat model pending |
| FDE-006 | POC | Independent synthetic ERP API | FDE | P0 | Implemented | ERP container, GET orders |
| FDE-007 | POC | Independent synthetic WMS API | FDE | P0 | Implemented | WMS container, GET inventory |
| FDE-008 | POC | Independent synthetic TMS API | FDE | P0 | Implemented | TMS container, GET shipment |
| FDE-009 | POC | Source adapters with bounded HTTP timeouts and credential header | FDE | P0 | Implemented (demo) | app/fde_integration.py |
| FDE-010 | POC | Tenant-scoped unified order lookup | FDE | P0 | Implemented (demo) | GET /api/v2/logistics/orders/{order_id} |
| FDE-011 | POC | Deterministic late-delivery classification | FDE | P0 | Implemented | assess() and exceptions API |
| FDE-012 | POC | Logistics browser lookup and exception list | FDE | P0 | Implemented | frontend/index.html |
| FDE-013 | POC | Manual investigation case creation/listing | FDE | P0 | Implemented (demo) | POST/GET investigations |
| FDE-014 | POC | Run Docker Compose end-to-end smoke and outage tests | FDE + QA | P0 | Pending execution | CI log / evidence |
| FDE-015 | POC | Customer demo and acceptance signoff | FDE + customer lead | P0 | Pending | UAT record |
| FDE-016 | Pilot | Implement configurable real ERP/WMS/TMS adapters and approved credentials | FDE + source owners | P0 | Not started | Integration contract test and sandbox evidence |
| FDE-017 | Pilot | Validate Entra access tokens and enforce real user-to-customer authorization and RBAC/ABAC | Security + FDE | P0 | Partial: JWT read/write roles and claim validator committed; app registration, claim issuance, user-level enforcement and UAT pending | Security and authorization negative tests |
| FDE-018 | Pilot | Implement Postgres migrations, investigation audit, idempotency and case ownership | Backend | P0 | Partial: PostgreSQL case store, migrations, index refresh table and connection pool; audit/idempotency/ownership/RLS pending | Private Postgres integration and audit checks |
| FDE-019 | Pilot | Add data freshness, partial response semantics and reconciler | Integration lead | P0 | Not started | Stale-source and outage test scenarios |
| FDE-020 | Pilot | SLO telemetry: traces, RED metrics, source-level errors and latency | SRE | P1 | Not started | Dashboard and alert tests |
| FDE-021 | Pilot | Secure customer-facing case assignment/approval workflow | FDE + product | P1 | Not started | Case lifecycle UAT |
| FDE-022 | Pilot | Benchmarked user acceptance, workflow time savings and adoption | Customer operations | P0 | Not started | Signed pilot report |
| FDE-023 | Production | Azure Bicep environments, ACA, ACR, Entra, managed identity and Key Vault | Platform | P0 | Partial: foundation, gateway and scheduled job Bicep compiling; cloud deployment, private endpoints and promotion pending | Azure what-if and deployment evidence |
| FDE-024 | Production | Azure PostgreSQL Flexible Server, private networking, restore and migration rollback | DBA + SRE | P0 | Partial: template and SQL; restore and migration not tested in Azure | Restore drill and RPO/RTO |
| FDE-025 | Production | Network policies, TLS, SAST/SCA/SBOM, secret scan and threat model | Security | P0 | Not started | Security signoff |
| FDE-026 | Production | Retry/backoff, circuit breaker, bulkhead and upstream chaos testing | SRE + FDE | P0 | Not started | Measured outage and recovery evidence |
| FDE-027 | Production | Validate 500 named-user Azure profile, burst, failover and rollback | SRE | P0 | Partial: k6 script, autoscale and indexed read-model code; load tests and Azure operations pending | Measured SLO and rollback results |
| FDE-028 | Handover | Runbooks, on-call ownership, enablement, demos and feedback backlog | FDE + CS + SRE | P0 | Not started | Signed handover |
| FDE-029 | AI option | ACL-aware RAG over approved delivery SOPs and incident guides | AI platform | P2 | Not started | Grounded citations, ACL and evaluation tests |
| FDE-030 | AI option | Read-only AI shipment explanation and human escalation drafting | AI platform | P2 | Not started | Safety eval and approval boundary |

## Phase-by-phase definition of done

### Discovery
- Data owners approve sample payloads and role scope; business stakeholders approve target workflows.
- Document baseline and target metrics; no fabricated percentage improvements.
- Escalation and approvals are assigned to named customer roles.

### POC
- Start all four containers using Compose; verify healthy services.
- Verify a single order resolves ERP + WMS + TMS and returns a deterministic reason.
- Verify cross-tenant access denied; verify upstream outage explicitly fails, never fabricates information.
- Demonstrate investigation case intake and listing; record actual test outputs.

### Pilot
- Replace every synthetic source or explicitly label retained simulators.
- Enforce authenticated user identity, field/object-level access and audit.
- Record pilot adoption, latency and correctness for agreed sample sizes.

### Production
- No deployment approval without passing security, reliability, restoration and release rehearsals.
- Publish SLOs and operational support; system-of-record write actions remain gated by explicit approval.
- Customer owns and accepts runbooks and post-launch escalation.

## Representative user acceptance scenarios

| Scenario | Expected behavior |
| --- | --- |
| Acme user looks up SO-1001 | ERP order + WH-EAST stock + SHIP-1001; ETA_AFTER_PROMISE |
| Acme user reads SO-2001 | 404, does not reveal Sky Jet |
| Acme opens SO-1001 investigation | 201 with OPEN case and reason code |
| No tenant header | 401 (demo-only scope, not enterprise authentication) |
| TMS unavailable | 502 upstream unavailable; never fabricate shipment status |
| Unknown order | 404 |
| Non-late order investigation | 409 |
| Real customer go-live request | Blocked pending pilot and production gates |

## Azure branch go-live blockers (2026-11-16)

- [ ] Validate Bicep with ARM what-if and actual sandbox deployment; enforce approved private endpoints and API Management/WAF ingress.
- [ ] Approve and issue Entra `Logistics.Read` and verified customer-tenant mapping; deliver corporate Entra-aware frontend.
- [ ] Replace simulated upstream sources with approved real ERP/WMS/TMS adapters and test failure, rate limits and idempotency.
- [ ] Replace the demo N+1 exception scan with a bounded indexed/paginated read model and monitored ingestion; Azure runtime currently returns 503 for this operation.
- [ ] Execute PostgreSQL schema migrations with least privilege, enable audited multi-tenant policy and restore testing.
- [ ] Run 50-VU nominal profile and separately authorized 500-concurrent-user stress, publish p95/p99 latency and error evidence.
- [ ] Complete threat model, secrets isolation, observability, runbooks, canary rollback and signoff.

See [Azure enterprise rollout guide](AZURE-ENTERPRISE-500-USERS.md).

## Added enterprise implementation files
- Identity, app roles and tests: `app/identity.py`, `tests/test_azure_security.py`, `tests/test_enterprise_routes.py`.
- Entra-aware SPA: `enterprise-ui/` (buildable; not hosted or signed off).
- Persistent indexed exception view: `app/exception_store.py`, `migrations/002_delivery_exceptions.sql`, `scripts/refresh_exceptions.py`.
- Azure job and validated CI: `deploy/azure/exception-refresh-job.bicep`, `.github/workflows/azure-validation.yml`.
- Approved release workflow **validation-only**: `.github/workflows/azure-release.yml`.
- SRE/security/customer gates: `docs/OPERATIONS-DELIVERABLES.md`, `docs/RELEASE-GATES.md`, `docs/SECURITY-THREAT-MODEL.md`, `docs/NETWORK-SECURITY.md`, `docs/DB-OPERATIONS.md`, `docs/OBSERVABILITY-SLOS.md`, `docs/RUNBOOK-INCIDENT-RECOVERY.md`, `docs/CUSTOMER-DISCOVERY-UAT.md`.

A completed file does not close customer-specific Azure, SSO, connectivity, deployment, 500-user testing or operational approval tasks.
