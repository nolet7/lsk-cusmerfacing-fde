# Azure PostgreSQL migration, access and tenancy playbook

## Deployment order
1. Deploy private Flexible Server through approved infrastructure pipeline; validate private DNS and subnet access.
2. Run `migrations/001_investigations.sql` as schema owner with an audited **private** migration runner.
3. Run `migrations/002_delivery_exceptions.sql`; both migrations must exist before `GET /ready` succeeds in enterprise mode.
4. Create separate minimum-privilege roles:
   - `lsk_api_runtime`: SELECT/INSERT to `investigations`, SELECT to `delivery_exceptions` and `exception_refresh_state`; sequence USAGE.
   - `lsk_ingestion_runtime`: SELECT/DELETE/INSERT to `delivery_exceptions`, INSERT/UPDATE to `exception_refresh_state`; no inquiry case modification.
   - `lsk_schema_owner`: DDL/migrations only; no API runtime credentials.
5. Store each role's TLS-verified connection string in separate Key Vault secrets, with distinct workload identities for gateway and scheduled job.
6. Apply tenant-enforced RLS and transaction-scoped trusted tenant context where required by the data classification. **RLS is not implemented in the current migrations**; row filters in application SQL are not a substitute for DB-enforced isolation.
7. Verify rollback/restore using a disposable restored server. Record backup retention, RPO/RTO and recovery evidence.

## Read model
The ingestion job atomically replaces a tenant's exception rows and writes `exception_refresh_state` even if there are zero exceptions. The API refuses to return data older than `EXCEPTION_MAX_AGE_SECONDS` (default 900). For real enterprise volumes, replace full per-tenant refresh with change-event ingestion, deduplication and pagination.

## SQL checks
```sql
SELECT to_regclass('public.investigations'),
       to_regclass('public.delivery_exceptions'),
       to_regclass('public.exception_refresh_state');
SELECT tenant_id, refreshed_at, indexed_count
FROM exception_refresh_state ORDER BY refreshed_at DESC LIMIT 25;
```
## Production blockers
- Set up separate Key Vault identities and DB role grants in the customer's private environment.
- Add RLS/tenant audit, immutable change history and investigation actor IDs.
- Validate transactions under concurrent refresh, source downtime, malformed dates and DB failover.
- Establish retention and backup restoration tests, and environment-specific migration policy.

No live Azure database, credentials, or migration evidence is included in the repository.
