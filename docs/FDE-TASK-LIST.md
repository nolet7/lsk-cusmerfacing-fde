# Forward Deployed Engineer implementation backlog and task checklist

This is a working delivery backlog. Status **Implemented** means code was committed to `feature/full-fde-logistics-engagement`; it does **not** mean production validation or automated tests have passed.

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
| FDE-017 | Pilot | Replace spoofable tenant header with verified OIDC user identity and RBAC/ABAC | Security + FDE | P0 | Not started | Authorization negative tests |
| FDE-018 | Pilot | Implement Postgres migrations, investigation audit, idempotency and case ownership | Backend | P0 | Not started | Database tests and audit checks |
| FDE-019 | Pilot | Add data freshness, partial response semantics and reconciler | Integration lead | P0 | Not started | Stale-source and outage test scenarios |
| FDE-020 | Pilot | SLO telemetry: traces, RED metrics, source-level errors and latency | SRE | P1 | Not started | Dashboard and alert tests |
| FDE-021 | Pilot | Secure customer-facing case assignment/approval workflow | FDE + product | P1 | Not started | Case lifecycle UAT |
| FDE-022 | Pilot | Benchmarked user acceptance, workflow time savings and adoption | Customer operations | P0 | Not started | Signed pilot report |
| FDE-023 | Production | IaC for dev, pilot and prod on GCP; Workload Identity and Secret Manager | Platform | P0 | Not started | Reviewed plans and environment evidence |
| FDE-024 | Production | Managed database, backup/restore and migration rollback | DBA + SRE | P0 | Not started | Restore drill and RPO/RTO |
| FDE-025 | Production | Network policies, TLS, SAST/SCA/SBOM, secret scan and threat model | Security | P0 | Not started | Security signoff |
| FDE-026 | Production | Retry/backoff, circuit breaker, bulkhead and upstream chaos testing | SRE + FDE | P0 | Not started | Measured outage and recovery evidence |
| FDE-027 | Production | Performance/load and canary or rollback rehearsal | SRE | P0 | Not started | SLO and rollback results |
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
