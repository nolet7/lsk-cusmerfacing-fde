# Pilot — Customer Adoption and Risk-Managed Evaluation

## Pilot users and scope
Two simulated customer organizations, 5-10 internal account managers, 30+ labeled synthetic inquiries spanning order status, shipping, quote requests, quality holds, cross-tenant attempts and missing data. This is an implementation plan, not an assertion a real customer pilot has occurred.

## Entry gate
1. POC tests pass in CI.
2. External IdP/OIDC design approved before real accounts; never use X-Demo-Tenant for real data.
3. Security-approved model endpoint and data processing agreement when real LLM inference is enabled.
4. Baseline manually handled case response latency and accuracy collected.
5. Clear human approval owner assigned for pricing, release status and delivery commitments.

## Workstreams
- **Integration:** map CRM account IDs and ERP work-order IDs; schema validation; sandbox API keys; replayable synthetic fixtures; error/retry mapping.
- **AI evaluation:** 30+ question-answer pairs; measure factual support, refusal on unknowns, answer groundedness, unsafe commitments, latency and token spend. Run prompt-injection and cross-tenant adversarial cases.
- **Adoption:** workshop deck, customer-facing POC script, user onboarding checklist, support queue, CSAT and response disposition dashboard.
- **Feedback:** triage customer problems weekly into product bugs, feature requests and implementation accelerators.
- **Reliability:** histogram p50/p95 latency, requests/case approval counters, structured logs with request ID; redact prompts and sensitive records.

## Exit gate — targets, not measured results
Grounded accuracy >=95%; 0 cross-tenant record leaks; 100% risky commercial/quality responses routed for manual approval; p95 under agreed SLO; stakeholders sign UAT. Otherwise do not promote.

## RACI
FDE builds integrations and runs the customer workshop; customer IT owns identity and ERP authorization; CISO approves data handling; Customer Success owns adoption; CTO signs release; Sales validates business value.

## Decision log
- ADR-001: managed Postgres over demo SQLite for multi-user pilot
- ADR-002: tenant identity from verified OIDC JWT, never a client-supplied header
- ADR-003: model can generate drafts but cannot invoke unapproved state-changing tools
- ADR-004: fail closed when external provider or data contract unavailable
