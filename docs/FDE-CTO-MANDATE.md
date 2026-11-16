# CTO mandate — LSK Global Distribution Logistics Integration

> **Scenario:** Fictional multinational B2B distributor. All customer interviews, requirements, target measures and signoffs in this file are simulation artifacts, not actual enterprise engagements.

## Executive mandate

Our logistics and customer-success staff investigate customer orders by switching among ERP, warehouse management (WMS) and transportation management (TMS) systems. This creates fragmented visibility, repeated manual reconciliation and slow responses to late-delivery inquiries. As the forward deployed engineering team, design and deliver a **customer-specific integration** that unifies order, inventory, shipping events and delivery exceptions **without replacing the customer's systems of record**.

Start with a reproducible synthetic discovery-to-POC demonstration. Deliver a governed pilot and advance to production **only after** real contracts, security controls, reliability tests, user acceptance and operating-model approvals are evidenced.

## Sponsor, stakeholders and responsibilities

| Role | Key concern | Engagement responsibility |
| --- | --- | --- |
| CTO (executive sponsor) | Business value, integration risk, investment | Signs phase gates, approves scope |
| Logistics operations lead | Late-delivery investigation | Defines user workflows and accepts demonstrations |
| Customer-success lead | Customer communication consistency | Reviews inquiry response workflow |
| ERP owner | Order data and semantic correctness | Approves ERP contract and mapping |
| WMS owner | Inventory freshness and allocation | Approves WMS field definitions |
| TMS owner / carrier integration lead | Event accuracy, ETA provenance | Approves shipment contract |
| Security/IAM | Data access, tenant isolation, audit | Signs architecture and security gates |
| FDE lead | Discovery through customer handover | Owns integration decisions, demos, implementation and enablement |
| Platform/SRE | Deployment and reliability | Owns observability, incident playbooks, SLO operations |

## Required user journeys

**UJ-01 — Order lookup:** As a logistics coordinator, I enter an order ID and view authoritative order state, SKU, promised date, warehouse allocation and related shipment, with a source label for every field.

**UJ-02 — Inventory availability:** I can see on-hand, reserved and available stock for the order's warehouse/SKU; missing inventory must show missing rather than zero.

**UJ-03 — Shipment status:** I can inspect carrier, tracking reference, last event, ETA, delivered date and record freshness.

**UJ-04 — Exception management:** I can distinguish missing shipment data, ETA after promise, past-due-not-delivered and delivered-late orders, then open a human-owned investigation. The system does not automatically revise ERP commitments.

**UJ-05 — Customer-service inquiry:** The existing customer-services portal can draft an evidence-grounded answer; commercial or quality commitments require separate explicit human approval in future phases.

**UJ-06 — Tenant isolation:** Records belonging to one customer must never be accessible from another customer's identity.

**UJ-07 — Upstream failure:** A failed or slow source must cause an explicit error or marked partial/stale response; the service cannot silently invent the answer.

## Nonfunctional requirements and proposed targets

| Dimension | Proposal | Gate |
| --- | --- | --- |
| Access control | Enterprise OIDC + least privilege + per-object tenant/role enforcement | Required before real-user pilot |
| Data correctness | No unsupported status/ETA; visible source provenance and freshness | POC validation |
| Reliability | Target 99.9% monthly API availability (not measured) | Production design review |
| Performance | Target p95 lookup < 1.5s for approved pilot load (not measured) | Pilot load test |
| Recovery | RPO/RTO set by system owners after dependency analysis | Before production |
| Security | Secrets manager, approved network egress, encryption, audit logs, threat model | Pilot/production |
| Operability | Alerting, traces, incident playbooks, rollback drills | Before production |
| Cost | Per-environment budgets and spend alerts | Before managed cloud deployment |

## Scope and exclusions

In scope: customer discovery simulation, field mappings, synthetic networked service integration, unified API, user-facing lookup, deterministic exception detection, manual investigation intake, contract tests and phase-gate artifacts.

Out of scope in current implementation: live Salesforce/SAP/Oracle/NetSuite/WMS/TMS/carrier connections, actual enterprise SSO, billing or warehouse writeback, real-time event streaming, cloud certification, real customer adoption, autonomous shipment changes and business metrics claimed as achieved.

## Phase gates

- **Gate 0 — Discovery:** signed problem statement, sample payload contracts, data classifications, role matrix and baseline business measures
- **Gate 1 — POC:** multi-service demo, API and browser scenario, positive/negative tests, error behavior, stakeholder walkthrough
- **Gate 2 — Pilot:** approved real sandbox connectors, authenticated identity, audit/observability, operational readiness, signed UAT, measured results
- **Gate 3 — Production:** approved security architecture, secrets and IaC, SLOs, on-call ownership, load/failover/restore/rollback evidence, formal change approval
- **Gate 4 — Handover:** runbooks, customer training, source ownership agreements, support escalation and product feedback record

## CTO acceptance checklist

- [x] Independent synthetic ERP/WMS/TMS HTTP services implemented on feature branch
- [x] Tenant-filtered read-only integration gateway and browser lookup implemented
- [x] Deterministic late-delivery exception classification implemented
- [x] Manual investigation case intake and listing implemented in demo database
- [ ] CI and runtime smoke tests verified passing on this branch
- [ ] Real enterprise source contracts and owners approved
- [ ] Enterprise OIDC and user-level RBAC implemented and penetration-tested
- [ ] Real customer sandbox connectivity validated
- [ ] Pilot user acceptance and operational measurements recorded
- [ ] Production SLO, security, restore, failover and rollback gates met
- [ ] Customer operational handover signed

**Delivery rule:** A README, diagram, simulated dataset, proposed KPI or branch named `production` is not evidence of a completed pilot or production deployment.
