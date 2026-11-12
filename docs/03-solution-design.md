# Architecture decision records
ADR-001: Extend legacy CRM + orders + support simulator instead of replacing it. Proves integration work.
ADR-002: Python FastAPI with sqlite for reproducible POC; PostgreSQL is production target and needs migration testing.
ADR-003: Deterministic SQL-backed approved account snapshot; never generated SQL from model outputs.
ADR-004: Optional hosted LLM through configured API; return deterministic evidence-based summary when no API key is configured. Never describe fallback as live inference.
ADR-005: Tenant comes from authenticated principal in pilot/production, not arbitrary request input; reject cross-tenant access.
ADR-006: Docker Compose for demo; production requires workload identity, managed secrets, migrations, backups, ingress, CI/CD, load tests and approval evidence.
## API contract
GET /health, GET /api/v1/accounts/{account_id}, GET /api/v1/accounts/{account_id}/briefing. POST /api/v1/events for demo event capture in later phases.
