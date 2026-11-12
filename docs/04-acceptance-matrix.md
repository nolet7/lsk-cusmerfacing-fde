# Measurable delivery gates (targets, not measured results)
| Gate | Test | Acceptance |
|---|---|---|
| POC | Customer account 360 from three SQL tables | Returns orders, support and CRM fields with source labels |
| POC | API schema and JSON output | OpenAPI UI and reproducible curl samples |
| POC | Live LLM path | With valid configured key, grounding uses approved snapshot only; fallback clearly labeled |
| POC | Demo & objections | 20-minute demo, architecture diagram and discovery notes |
| Pilot | Auth | Missing/invalid API key rejected, cross-tenant access rejected |
| Pilot | Observability | Requests, error rate, latency and adoption events captured |
| Pilot | AI quality | Test fixture evaluated for factual grounding; human review of failures |
| Production | Operations | Deployment and rollback rehearsed, SLO dashboards, runbooks, ownership signoff |
| Production | Security | Pen-test/security review and data processing review completed before real customer rollout |
