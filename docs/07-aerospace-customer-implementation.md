# Aerospace Customer Operations — FDE Customer Implementation Brief

## CTO mandate
A fictional aerospace repair services enterprise receives customer requests about work-order status, overhaul turnaround time, service quotes, shipping and documentation. Customer services staff reconcile ERP work orders, CRM accounts, quality holds, shipping events and email manually. Build a customer-facing AI/data SaaS integration showing faster responses **without** overriding quality engineering or commercial approval.

This is an independent educational simulation inspired by the **business domain** of aerospace repair providers such as Chromalloy; **not Chromalloy systems, data, brand endorsement or an actual engagement.**

## Personas
- External aerospace fleet/MRO customer: sees only own work orders and inquiries
- Customer account manager: prepares responses and seeks quote approval
- Repair operations specialist: updates fictional work-order progress
- Quality/engineering representative: reviews hold status; no model-authored airworthiness decisions
- Enterprise CTO/security: approves data residency, identity, integration and audit controls
- FDE + Sales/Customer Success: discovery, POC demonstrations, pilot adoption and onboarding

## Legacy-first scope
CRM accounts and contacts; ERP repair orders and quote requests; customer case queue; quality hold flags; shipping milestones. Integrate by versioned REST JSON endpoints, SQL views and mapping adapters. Keep simulated ERP authoritative; the AI **never invents** release dates, certifications, prices, or work-order changes.

## Customer interaction
1. Customer signs in and selects a repair order.
2. Portal submits tenant-scoped question.
3. Legacy API validates role/account and fetches authoritative work-order snapshot.
4. AI service receives an allowlisted, minimal dataset and a versioned policy prompt; it returns a *draft* with record references.
5. Server-side policy blocks unsupported facts and risky actions.
6. Account manager reviews any quote/ETA/quality commitment and approves or rejects.
7. Response/case is recorded with audit event, latency and feedback.
8. FDE inspects adoption, correct-answer rate and customer feedback with stakeholders.

## Success gates (targets, not achieved results)
POC: one full demo, valid SQL+REST+JSON flows, cross-tenant negative tests, optional real LLM inference, reproducible setup.
Pilot: >=30 synthetic use-case runs, grounded-answer >=95% on a labeled benchmark, zero cross-tenant leaks, manual approval coverage 100% for commercial commitments, signed UAT.
Production readiness: approved threat model and data flows, real enterprise SSO, secrets rotation, backup restore, measurable SLO, release/rollback rehearsal, on-call and customer handover. Deployment claims require live evidence.

## Explicit guardrails
No sensitive real enterprise data. No automatic airworthiness release, pricing approval, export-classification decisions, or safety-critical disposition. Hosted model use is opt-in and must pass customer security approvals.

## FDE workflow
Discovery -> stakeholder map -> legacy data contract -> architecture/ADR -> custom demo -> POC acceptance -> pilot user training -> monitored rollout -> documentation/product feedback -> handover.
