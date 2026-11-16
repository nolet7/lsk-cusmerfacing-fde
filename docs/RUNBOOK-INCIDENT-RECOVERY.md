# Operational incident response, restoration and rollout

**P0: customer data leak or auth bypass.** Block ingress/disable affected revision, invalidate or revoke compromised identities, rotate secrets, activate security incident plan, preserve immutable audit evidence and follow customer notification policy.

**P1: API errors.** Check ACA revision health, replica saturation, request 5xx and source-level timeout metrics. Distinguish internal API failures from upstream ERP/WMS/TMS API 429/503. Disable case write path if database integrity is at risk. Never fallback to fabricated shipment values.

**P2: stale exception index.** Query `exception_refresh_state` for freshness and `delivery_exceptions` row counts, inspect scheduled ACA job executions and approved source API health. Re-run ingestion **only after** checking current data ownership and quotas; per-tenant replace is atomic. Do not silently show stale results: API returns 503.

**Database restore:** Coordinate with DBA. Verify backup retention and point-in-time restore in a separate temporary Azure PostgreSQL instance; check migration state, row counts, integrity, tenant isolation, index refresh state, and connection string/secret rotation before switching traffic. Obtain production restore approval.

**Release rollback:** Redeploy last known good immutable ACR digest or shift ACA traffic to approved previous revision according to chosen rollout mode. Check DB backward compatibility. Schema rollback must be independently reviewed, not assumed safe.

**Security rotation:** Revoke/rotate Entra app credentials and external source tokens via approved systems; update Key Vault secret versions; validate workload identity and 401/403 tests. Do not print secrets.

**On-call checklist:** record incident ID, start/end, impacted tenants (do not expose PII), source status, SLO impact, mitigation, approvals, change timeline, customer notification and postmortem owners.

**Escalation matrix — replace placeholders:** CTO sponsor, logistics lead, integration source owners (ERP/WMS/TMS), DBA, SRE pager, identity admin, security incident commander, customer success lead.

**Operational state:** Runbooks created; tabletop drills, live Azure alert routing, restoration/failover and pager validation still pending.
