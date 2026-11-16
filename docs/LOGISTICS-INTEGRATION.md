# ERP–WMS–TMS Logistics Visibility — Implementation and Validation

## Business outcome
A logistics specialist can look up an order across three simulated source systems without switching applications. The service brings together ERP order data, WMS stock availability, and TMS shipment status, and flags delivery-risk exceptions. All sample records are synthetic.

## Request path
1. A logistics user requests `GET /api/v1/logistics/orders/SO-1001`.
2. The demonstration tenant header is validated; for real users this must be replaced by verified OIDC access tokens.
3. ERP read model returns customer, SKU, quantity, promise date and fulfillment status.
4. Warehouse read model returns stock on hand and reserved quantity; available = max(on_hand - reserved, 0).
5. TMS read model returns carrier, tracking reference, last event, ETA and delivery status.
6. A deterministic policy compares the promised date, ETA and delivery date, returning a reason code with the source records.
7. User can review all flagged orders through `GET /api/v1/logistics/exceptions`.

## API contract
| Method | Path | Purpose |
| --- | --- | --- |
| GET | /api/v1/logistics/orders/{order_id} | ERP+WMS+TMS unified order snapshot |
| GET | /api/v1/logistics/inventory/{sku} | Tenant-filtered stock locations |
| GET | /api/v1/logistics/shipments/{shipment_id} | Tenant-filtered tracking details |
| GET | /api/v1/logistics/exceptions | Tenant-filtered at-risk and late orders; limit 1..100 |

Errors: 401 missing/invalid demonstration tenant header; 404 a foreign or unknown order/shipment; 422 invalid limits. Use read-only endpoints.

## Quick demonstration

```bash
docker compose -f deploy/compose.yaml up --build -d
curl -fsS -H 'X-Demo-Tenant: acme-air' http://127.0.0.1:18641/api/v1/logistics/orders/SO-1001
curl -fsS -H 'X-Demo-Tenant: acme-air' http://127.0.0.1:18641/api/v1/logistics/inventory/TURB-001
curl -fsS -H 'X-Demo-Tenant: acme-air' http://127.0.0.1:18641/api/v1/logistics/shipments/SHIP-1001
curl -fsS -H 'X-Demo-Tenant: acme-air' http://127.0.0.1:18641/api/v1/logistics/exceptions
python -m pytest -q
```

For the synthetic SO-1001 case: ERP promised date 2026-11-10; TMS estimated delivery 2026-11-20; last event is weather disruption. The deterministic exception reason is ETA_AFTER_PROMISE. This is a demonstration, not evidence of a real late shipment.

## Design decisions
- Preserve the original customer inquiry and aerospace work-order demo.
- Keep source-system tables separate to represent ERP/WMS/TMS domains; aggregation occurs only inside the logistics API.
- Parameterize every SQL query; scope every lookup by the tenant selected by the demo identity layer.
- No generative model is needed to calculate late-delivery decisions; source records and deterministic rules remain authoritative.
- Avoid claims of live carrier tracking, live ERP connectors, enterprise security certification or production deployment.

## Enterprise production gaps
1. Build real ERP/WMS/TMS adapters with approved upstream credentials, contract tests, pagination, retries/backoff, circuit breakers and timeouts; do not permit arbitrary outbound URLs.
2. Replace `X-Demo-Tenant` with OIDC validation (issuer, signature, audience, expiry), RBAC, fine-grained object authorization and immutable audit records.
3. Move source data to managed Postgres and/or event-driven integration via Pub/Sub; add schema migrations, source change capture, deduplication, idempotency, event ordering, and reconciliation.
4. Define freshness SLOs and display per-source timestamps, partial failures, explicit stale-data indicators and upstream outage handling.
5. Build logistics UI for search, fulfillment timeline, tracking and exceptions; implement operational dashboards.
6. Implement OpenTelemetry, RED metrics, tracing, SLO alerting, load tests, security scans and API contract regression gates.
7. Provision environment-specific GCP infrastructure with Terraform and GKE/Cloud Run, Secret Manager, workload identity, HA database, backups and restore rehearsals.
8. Execute acceptance tests with real enterprise test environments before using the resume bullet as a claim of actual system integration.

## Resume alignment
The branch provides **working synthetic demonstration** of an API that combines ERP, warehouse and transportation information for order lookup, inventory visibility, shipment status and delivery-risk investigation. It does not establish actual integrations with business systems.
