"""Explicit scheduled ingestion job; requires allowlisted upstreams and DB connectivity.

Run with SCOPE_TENANTS=acme-air,sky-jet in a controlled synthetic sandbox.
Do NOT accept tenant IDs from request parameters or end users.
"""
import asyncio
import os
import sys
import httpx
from app.fde_integration import config, source, snapshot
from app.case_store import _postgres

async def refresh_tenant(client,cfg,tenant):
    listing=await source(client,cfg["ERP_BASE_URL"],"/v1/orders",
                         {"tenant_id":tenant},cfg["DEMO_CONNECTOR_TOKEN"])
    orders=(listing or {}).get("items",[])
    if len(orders)>1000:
        raise RuntimeError("Source order limit exceeded; implement upstream cursor paging")
    results=[]
    for order in orders:
        result=await snapshot(client,cfg,tenant,order["order_id"])
        if result["late_delivery"]["is_late_or_at_risk"]:
            r=result["late_delivery"];s=result["shipment"] or {}
            results.append((tenant,order["order_id"],r["reason_code"],r["promised_date"],
                           r["estimated_delivery"],r["delivered_at"],s.get("shipment_status"),
                           s.get("last_event"),s.get("updated_at")))
    with _postgres() as db:
        # Transaction ensures readers see only a committed per-tenant refresh.
        with db.transaction():
            db.execute("DELETE FROM delivery_exceptions WHERE tenant_id=%s",(tenant,))
            for values in results:
                db.execute("""INSERT INTO delivery_exceptions
                   (tenant_id,order_id,reason_code,promised_date,estimated_delivery,delivered_at,
                    shipment_status,source_event,source_updated_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",values)
    return len(results)

async def main():
    tenants=[t.strip() for t in os.getenv("SCOPE_TENANTS","").split(",") if t.strip()]
    if not tenants:
        raise RuntimeError("SCOPE_TENANTS must be explicitly approved and configured")
    cfg=config()
    async with httpx.AsyncClient(timeout=httpx.Timeout(3.0),trust_env=False) as client:
        for tenant in tenants:
            n=await refresh_tenant(client,cfg,tenant)
            print(f"Tenant {tenant}: indexed {n} delivery exceptions")

if __name__=="__main__":
    asyncio.run(main())
