# FDE engagement package — discovery, mapping, acceptance and handover

## Interview script
- CTO: what customer outcome matters? Who owns budget and phase gate?
- Logistics manager: show a real late-order investigation; how long does it take today?
- ERP owner: source IDs, ordering, order lifecycle, promise dates and contracts?
- WMS owner: stock definition, reservations, allocation, time consistency and warehouse identifiers?
- TMS owner: tracking ownership, ETA semantics, carrier events, late/cancelled statuses, rate limits?
- IAM/security: roles, tenancy, data residence, retention, conditional access?
- Customer service: required explanation, evidence, case ownership, approval and escalation rules?

## Data contract acceptance
- [ ] Source-specific API examples received and classified
- [ ] ERP order_id / tenant / warehouse / SKU / shipment crosswalk validated
- [ ] WMS `available` definition approved and missing-stock semantics documented
- [ ] TMS ETA freshness, timezone, event order, promised-date definition agreed
- [ ] Conflict resolution, retry window, source authority and outage semantics documented
- [ ] Data residency, retention, personally identifying fields and redaction approved

## End-user acceptance scripts
1. Correct tenant logs in and looks up an owned order.
2. Unauthorized tenant asks for another customer's order (must not leak).
3. User sees stock, shipment, ETA and source provenance for a valid order.
4. Logistics.Read-only user attempts to create a case (must be denied).
5. Logistics.Write user opens an investigation with accountable human ownership.
6. Indexed exception feed is up-to-date and paginated; stale refresh is visible as an error.
7. Source ERP/TMS returns invalid, missing, 429, slow or reordered data: expected behavior recorded.
8. SSO logout and role revocation validated.
9. 50-active-user representative load and separate 500-concurrent stress recorded.
10. Support team completes an incident and rollback exercise.

## Delivery evidence form
- Scenario and acceptance ID:
- Stakeholder and role:
- Environment and source system version:
- Expected result:
- Observed result / redacted screenshot:
- Performance and source freshness:
- Approved or rejected / reason:
- Follow-up issue:
- Signoff date and signatory:

**No real customer interviews, UAT or signoff have been performed through this repository.**
