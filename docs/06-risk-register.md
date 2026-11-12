# Risks and mitigations
- Schema drift: versioned contract tests and sample payload fixtures.
- Data leakage: tenant-scoped query filters, redacted logs, scoped prompts.
- Hallucinations: model constrained to approved snapshot; show source fields; evaluate against fixtures.
- Slow/expensive inference: timeouts, per-tenant quotas, optional no-LLM fallback.
- Low adoption: champion enablement, task-based workshops, usage telemetry.
- Production cutover: feature flags, canary, rollback and written signoff.
