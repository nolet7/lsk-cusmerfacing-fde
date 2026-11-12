# Production handover / launch readiness (template — NOT a real deployment)

## Deployment demonstration
```bash
docker compose -f deploy/compose.yaml up --build -d
curl -fsS http://127.0.0.1:18641/health
docker compose -f deploy/compose.yaml logs -f
```
A demo uses local SQLite and the header tenant mechanism. **It is not permitted for real customers.**

## Required blockers before enterprise go-live
- Replace demo X-Demo-Tenant header with validated issuer, audience, signature, expiry and tenant claims from enterprise OIDC; enforce RBAC in DB query and write path.
- Replace SQLite with managed Postgres + migrations, transactional outbox, backups, retention and recovery tests.
- Use managed secrets and approved private inference endpoint; enforce egress controls, customer data agreements and content minimization.
- Add quote and quality approval persistence + authenticated approval endpoints. Current `approval_required` is a label, not a complete approval workflow.
- Implement structured audit logging, tracing, PII redaction, latency histograms and SLO dashboards.
- Add rate limits, WAF/TLS, customer-scoped authorization tests, SBOM/image scanning and vulnerability remediation.
- Exercise blue/green or canary release, rollback and versioned API compatibility, operational support rota and incident drill.

## Proposed environment map
Dev -> POC local demo; Pilot -> sandbox cloud namespace and enterprise IdP; Production -> hardened GKE cluster with external HTTPS load balancer, Workload Identity, Secret Manager, private service networking, Cloud SQL Postgres, managed telemetry, GitOps approval, autoscaling and budgets. Infrastructure described here is proposed and not provisioned.

## Release evidence checklist
PR reviewed; tests green; no secrets in git; image digest signed; vulnerability gate clear; migration dry run; smoke test and negative tenant tests; model eval passed; customer UAT signed; threat model accepted; rollback rehearsal; change approval.

## SLO candidate
99.9% monthly API availability and p95 under 1.5s (targets pending enterprise workload sizing); alert on 5xx errors and sustained latency; no automated decisions for airworthiness, pricing, or contractual delivery dates.

## Handover packet
Architecture diagrams, customer integration mapping, API documentation, implementation guide, demo script, prompt/model versions, evaluation evidence, security decisions, runbook, escalation path, release checklist, known limitations, Product feedback and Customer Success enablement.
