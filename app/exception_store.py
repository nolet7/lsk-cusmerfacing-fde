"""Indexed Azure exception feed. No upstream fan-out on user GET requests."""
import os
from datetime import datetime, timezone
from fastapi import HTTPException
from app.case_store import _postgres

def list_exceptions(tenant_id: str, limit: int, offset: int):
    if os.getenv("FDE_CASE_STORE","sqlite") != "postgres":
        raise HTTPException(503,"Exception read model requires PostgreSQL")
    max_age=int(os.getenv("EXCEPTION_MAX_AGE_SECONDS","900"))
    if not 60 <= max_age <= 86400:
        raise HTTPException(503,"Invalid freshness policy")
    with _postgres() as db:
        row=db.execute("SELECT MAX(refreshed_at) AS last_refresh FROM delivery_exceptions WHERE tenant_id=%s",(tenant_id,)).fetchone()
        last=row["last_refresh"] if row else None
        if last is None:
            raise HTTPException(503,"Exception index has not been populated")
        age=(datetime.now(timezone.utc)-last).total_seconds()
        if age>max_age:
            raise HTTPException(503,"Exception index is stale")
        rows=db.execute("""
            SELECT order_id,reason_code,promised_date,estimated_delivery,delivered_at,
                   shipment_status,source_event,source_updated_at,refreshed_at
              FROM delivery_exceptions WHERE tenant_id=%s
             ORDER BY refreshed_at DESC,order_id
             LIMIT %s OFFSET %s
        """,(tenant_id,limit,offset)).fetchall()
        return {"items":[{k:(v.isoformat() if hasattr(v,"isoformat") else v) for k,v in row.items()}
                         for row in rows],
                "limit":limit,"offset":offset,
                "last_refresh":last.isoformat(),"data_mode":"indexed-enterprise"}
