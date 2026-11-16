# LSK Customer-Facing Data & AI FDE

A fictional B2B SaaS customer implementation lab, built for discovery, presales POCs, pilot adoption, and controlled production handover.

## CTO mandate
Enable enterprise customers to connect CRM, ERP and support datasets via versioned REST/JSON APIs, ask questions about their data with auditable AI assistance, and automate safe read-only workflows. Prove value in live demonstrations before investing in a controlled pilot. Deliver repeatable integration accelerators and customer enablement.

## Branch strategy
- `main`: mandate, architecture, discovery, acceptance criteria and project charter.
- `poc`: runnable legacy SaaS CRM/support simulator plus Python/SQL integration API, seeded demo data and optional live LLM support.
- `pilot`: POC plus tenant-access enforcement, adoption telemetry, evaluation and pilot runbooks.
- `production`: pilot plus health/readiness endpoints, container setup, release/handover and security review checklist.

Branches are progressive snapshots; production is NOT proof of a cloud deployment or production certification.

## Customer journey
Sales discovery -> requirements -> reusable demo environment -> integration mapping -> technical workshop -> POC acceptance -> pilot onboarding -> monitored launch -> support handover -> product-feedback backlog.

## Start
See branch-specific README, `docs/` and `architecture/`. No real customer data. Demo credentials and sample records are fictional.

## Safety
AI never executes database queries or arbitrary HTTP requests supplied by an LLM. It uses pre-approved read-only tool results. Avoid putting customer secrets or sensitive records in prompts.

## Logistics ERP / WMS / TMS feature

The `feature/erp-wms-tms-logistics` branch adds a read-only, tenant-scoped, **synthetic** logistics integration alongside the original customer inquiry demo:

- `GET /api/v1/logistics/orders/{order_id}` — unified ERP order + WMS availability + TMS shipment and delivery-risk assessment.
- `GET /api/v1/logistics/inventory/{sku}` — simulated available inventory by warehouse.
- `GET /api/v1/logistics/shipments/{shipment_id}` — carrier, tracking and last event.
- `GET /api/v1/logistics/exceptions` — delayed or at-risk delivery records.

See [docs/LOGISTICS-INTEGRATION.md](docs/LOGISTICS-INTEGRATION.md) for the architecture, request flow, run commands, negative tenant-isolation tests, and real enterprise deployment blockers. No real ERP, WMS, TMS, carrier, or customer integration is represented.
