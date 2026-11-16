"""FDE integration gateway: ERP/WMS/TMS HTTP APIs, bounded calls, exception case management.

Demo-only identity uses the pre-existing X-Demo-Tenant header. Replace with enterprise
OIDC and per-user policy enforcement before any real tenant or customer use.
"""
import os
import asyncio
import sqlite3
from datetime import date
from urllib.parse import quote
import httpx
from fastapi import APIRouter, HTTPException, Depends
from app.identity import authorized_tenant, authorized_write_tenant
from app import case_store
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v2/logistics", tags=["fde-integration"])
_connect = None
_tenant = None

def configure(connect, tenant):
    global _connect, _tenant
    _connect, _tenant = connect, tenant

def initialize(connect):
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS investigations(
          investigation_id INTEGER PRIMARY KEY AUTOINCREMENT,
          tenant_id TEXT NOT NULL,
          order_id TEXT NOT NULL,
          reason_code TEXT NOT NULL,
          note TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'OPEN',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_investigations_tenant
          ON investigations(tenant_id, investigation_id);
        """)

def config():
    values = {n:os.getenv(n) for n in ("ERP_BASE_URL","WMS_BASE_URL","TMS_BASE_URL","DEMO_CONNECTOR_TOKEN")}
    if any(not v for v in values.values()):
        raise HTTPException(503, "Upstream simulator integration is not configured")
    return values

async def source(client, base, path, params, token):
    try:
        resp = await client.get(
            base.rstrip("/") + path,
            params=params,
            headers={"Authorization":f"Bearer {token}"},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        # Log sanitized error type only. Do not return upstream URLs or credentials.
        raise HTTPException(502, f"Upstream {type(exc).__name__}; snapshot unavailable") from None

def assess(order, shipment):
    promised = date.fromisoformat(order["promised_date"])
    delivered = date.fromisoformat(shipment["delivered_at"]) if shipment and shipment.get("delivered_at") else None
    eta = date.fromisoformat(shipment["estimated_delivery"]) if shipment and shipment.get("estimated_delivery") else None
    if shipment is None:
        reason = "SHIPMENT_DATA_MISSING"
    elif delivered:
        reason = "DELIVERED_LATE" if delivered > promised else None
    elif eta and eta > promised:
        reason = "ETA_AFTER_PROMISE"
    elif date.today() > promised:
        reason = "PAST_DUE_NOT_DELIVERED"
    else:
        reason = None
    return {"is_late_or_at_risk":reason is not None,"reason_code":reason,
            "promised_date":order["promised_date"],"estimated_delivery":shipment.get("estimated_delivery") if shipment else None,
            "delivered_at":shipment.get("delivered_at") if shipment else None}

async def snapshot(client, cfg, tenant_id, order_id):
    order = await source(client,cfg["ERP_BASE_URL"],"/v1/orders/"+quote(order_id,safe=""),
                         {"tenant_id":tenant_id},cfg["DEMO_CONNECTOR_TOKEN"])
    if order is None:
        raise HTTPException(404,"Order not found")
    # Both downstream requests depend on ERP's identifiers, but not on each other.
    # Concurrent reads reduce critical-path latency. Any upstream failure still
    # fails the snapshot closed; no invented shipment/stock records are returned.
    stock, shipment = await asyncio.gather(
        source(client,cfg["WMS_BASE_URL"],"/v1/inventory",
               {"tenant_id":tenant_id,"warehouse_id":order["warehouse_id"],"sku":order["sku"]},
               cfg["DEMO_CONNECTOR_TOKEN"]),
        source(client,cfg["TMS_BASE_URL"],"/v1/shipments/"+quote(order["shipment_id"],safe=""),
               {"tenant_id":tenant_id,"order_id":order_id},cfg["DEMO_CONNECTOR_TOKEN"]),
    )
    stock_items = stock.get("items",[]) if stock else []
    inventory = stock_items[0] if stock_items else None
    if inventory is not None:
        inventory = {**inventory,"available":max(inventory["on_hand"]-inventory["reserved"],0)}
    return {"order":order,"inventory":inventory,"shipment":shipment,
            "late_delivery":assess(order,shipment),
            "sources":{"erp":"Configured ERP HTTP source","wms":"Configured WMS HTTP source","tms":"Configured TMS HTTP source"},
            "as_of_date":date.today().isoformat(),
            "data_mode":"synthetic-http-integration" if os.getenv("FDE_ENV","local") in ("local","test") else "configured-external-connectors"}

@router.get("/orders/{order_id}")
async def unified_order(order_id:str,tenant_id: str = Depends(authorized_tenant)):
    cfg=config()
    async with httpx.AsyncClient(timeout=httpx.Timeout(3.0),trust_env=False) as client:
        return await snapshot(client,cfg,tenant_id,order_id)

@router.get("/exceptions")
async def exceptions(tenant_id: str = Depends(authorized_tenant)):
    cfg=config()
    async with httpx.AsyncClient(timeout=httpx.Timeout(3.0),trust_env=False) as client:
        listing=await source(client,cfg["ERP_BASE_URL"],"/v1/orders",
                            {"tenant_id":tenant_id},cfg["DEMO_CONNECTOR_TOKEN"])
        orders=(listing or {}).get("items",[])
        if len(orders)>100:
            raise HTTPException(503,"POC source result exceeded bounded scan")
        items=[]
        for order in orders:
            result=await snapshot(client,cfg,tenant_id,order["order_id"])
            if result["late_delivery"]["is_late_or_at_risk"]:
                items.append(result)
        return {"count":len(items),"items":items,"data_mode":"synthetic-http-integration" if os.getenv("FDE_ENV","local") in ("local","test") else "configured-external-connectors"}

class InvestigationRequest(BaseModel):
    order_id:str=Field(min_length=3,max_length=64)
    note:str=Field(min_length=3,max_length=1000)

@router.post("/investigations",status_code=201)
async def open_investigation(body:InvestigationRequest,tenant_id: str = Depends(authorized_write_tenant)):
    cfg=config()
    async with httpx.AsyncClient(timeout=httpx.Timeout(3.0),trust_env=False) as client:
        result=await snapshot(client,cfg,tenant_id,body.order_id)
    reason=result["late_delivery"]["reason_code"]
    if not reason:
        raise HTTPException(409,"Order has no detected delivery exception")
    investigation_id=case_store.create_investigation(tenant_id,body.order_id,reason,body.note,_connect)
    return {"investigation_id":investigation_id,"order_id":body.order_id,
            "reason_code":reason,"status":"OPEN","data_mode":"synthetic" if os.getenv("FDE_ENV","local") in ("local","test") else "enterprise-case-store"}

@router.get("/investigations")
def list_investigations(tenant_id: str = Depends(authorized_tenant)):
    return {"items":case_store.list_investigations(tenant_id,_connect),"data_mode":"synthetic" if os.getenv("FDE_ENV","local") in ("local","test") else "enterprise-case-store"}
