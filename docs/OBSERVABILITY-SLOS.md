# SRE observability and SLO design for 500 named users

Targets must be accepted by the customer and baselined in an Azure pilot.

| SLI | Proposed target | Instrumentation required |
| --- | --- | --- |
| API availability | >=99.9% per calendar month | Authorized API request successes / total, excluding agreed client errors |
| Order lookup p95 | <1,500ms at 50 active VUs | Gateway request timing histogram |
| Indexed exception freshness | <=15 minutes | `exception_refresh_state.refreshed_at`, alert on stale tenant |
| Internal connector reliability | >99% successful authorized reads | ERP/WMS/TMS timeout, response and circuit-breaker metrics |
| DB saturation | Pool wait p95 / active connections below limits | PG Flexible Server / per-replica pool metrics |
| Unauthorized cross-tenant leakage | Zero confirmed leaks | Security alerts, contract tests, forensic logs |

**Alert candidates (not deployed):** 5xx >2% for 5 minutes, p95 >1.5s for 10 minutes, exception refresh age >15 minutes, database failover not recovered, prolonged ACA max replica saturation, repeated 401/403 anomalies.

## Suggested Azure Monitor KQL (adapt fields after ingestion)
```kusto
ContainerAppConsoleLogs_CL
| where TimeGenerated > ago(1h)
| summarize ErrorLines=countif(Log_s has_any ("ERROR", "exception")) by bin(TimeGenerated, 5m), ContainerAppName_s
```

The example query is **schema-dependent**: validate actual Log Analytics table names and columns after Azure provisioning. Do not claim dashboards or alerts exist until they are wired and tested.

## Telemetry architecture work outstanding
- Add OpenTelemetry request/HTTP-client spans with correlation IDs and *sensitive-data redaction*.
- Export trace/metric streams to approved Azure Monitor / Application Insights.
- Capture source-specific latency histograms, success/error counts, and stale-feed gauge.
- Implement SLO multiwindow burn-rate alerts and route to a staffed pager.
- Trace ERP -> WMS/TMS relationships without logging JWTs, customer names or unredacted order payloads.

## Validation evidence
Attach k6 results, named user count vs concurrent active users, median/p95/p99, RPS, provider throttling and DB pool consumption to the release ledger. No test has yet certified 500 concurrent users.
