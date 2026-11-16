"""Independent synthetic source-system HTTP simulator.

Run this module once per role (erp, wms, tms) as independent containers.
It is intentionally fictional and exposes read-only APIs only.
"""
import os
from fastapi import FastAPI, Header, HTTPException
from datetime import datetime, timezone

ROLE = os.getenv("SYSTEM_ROLE", "erp").lower()
if ROLE not in ("erp", "wms", "tms"):
    raise RuntimeError("SYSTEM_ROLE must be erp, wms or tms")
TOKEN = os.getenv("DEMO_CONNECTOR_TOKEN")
if not TOKEN:
    raise RuntimeError("DEMO_CONNECTOR_TOKEN is required for simulator auth")

app = FastAPI(title=f"LSK synthetic {ROLE.upper()} simulator", version="1.0.0")
ORDERS = [
    dict(order_id="SO-1001",tenant_id="acme-air",customer="Acme Air",sku="TURB-001",quantity=3,order_status="Fulfilled",promised_date="2026-11-10",warehouse_id="WH-EAST",shipment_id="SHIP-1001"),
    dict(order_id="SO-1002",tenant_id="acme-air",customer="Acme Air",sku="COMP-221",quantity=2,order_status="Processing",promised_date="2026-12-05",warehouse_id="WH-EAST",shipment_id="SHIP-1002"),
    dict(order_id="SO-2001",tenant_id="sky-jet",customer="Sky Jet",sku="TURB-001",quantity=1,order_status="Fulfilled",promised_date="2026-11-12",warehouse_id="WH-WEST",shipment_id="SHIP-2001"),
]
STOCK = [
    dict(tenant_id="acme-air",warehouse_id="WH-EAST",sku="TURB-001",on_hand=18,reserved=5,updated_at="2026-11-09T12:00:00Z"),
    dict(tenant_id="acme-air",warehouse_id="WH-EAST",sku="COMP-221",on_hand=4,reserved=2,updated_at="2026-11-09T12:00:00Z"),
    dict(tenant_id="sky-jet",warehouse_id="WH-WEST",sku="TURB-001",on_hand=6,reserved=1,updated_at="2026-11-09T12:00:00Z"),
]
SHIPMENTS = [
    dict(shipment_id="SHIP-1001",tenant_id="acme-air",order_id="SO-1001",carrier="DemoCarrier",tracking_number="TRACK-1001",shipment_status="In transit",estimated_delivery="2026-11-20",delivered_at=None,last_event="Weather disruption",updated_at="2026-11-15T09:00:00Z"),
    dict(shipment_id="SHIP-1002",tenant_id="acme-air",order_id="SO-1002",carrier="DemoCarrier",tracking_number="TRACK-1002",shipment_status="Label created",estimated_delivery="2026-12-04",delivered_at=None,last_event="Awaiting pickup",updated_at="2026-11-15T09:00:00Z"),
    dict(shipment_id="SHIP-2001",tenant_id="sky-jet",order_id="SO-2001",carrier="DemoCarrier",tracking_number="TRACK-2001",shipment_status="Delivered",estimated_delivery="2026-11-12",delivered_at="2026-11-12",last_event="Delivered to dock",updated_at="2026-11-12T17:00:00Z"),
]

def require(authorization: str | None):
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Connector credentials rejected")

def role_is(value: str):
    if ROLE != value:
        raise HTTPException(status_code=404, detail="Not available on this source")

@app.get("/health")
def health():
    return {"status":"ok","role":ROLE,"data_mode":"synthetic"}

@app.get("/v1/orders")
def orders(tenant_id: str, authorization: str | None = Header(default=None)):
    role_is("erp")
    require(authorization)
    return {"items":[{k:v for k,v in item.items() if k != "tenant_id"} for item in ORDERS if item["tenant_id"] == tenant_id]}

@app.get("/v1/orders/{order_id}")
def order(order_id: str, tenant_id: str, authorization: str | None = Header(default=None)):
    role_is("erp")
    require(authorization)
    for item in ORDERS:
        if item["tenant_id"] == tenant_id and item["order_id"] == order_id:
            return {k:v for k,v in item.items() if k != "tenant_id"}
    raise HTTPException(404, "Order not found")

@app.get("/v1/inventory")
def inventory(tenant_id: str, warehouse_id: str, sku: str, authorization: str | None = Header(default=None)):
    role_is("wms")
    require(authorization)
    return {"items":[{k:v for k,v in item.items() if k != "tenant_id"} for item in STOCK
                     if item["tenant_id"] == tenant_id and item["warehouse_id"] == warehouse_id and item["sku"] == sku]}

@app.get("/v1/shipments/{shipment_id}")
def shipment(shipment_id: str, tenant_id: str, order_id: str, authorization: str | None = Header(default=None)):
    role_is("tms")
    require(authorization)
    for item in SHIPMENTS:
        if item["tenant_id"] == tenant_id and item["shipment_id"] == shipment_id and item["order_id"] == order_id:
            return {k:v for k,v in item.items() if k != "tenant_id"}
    raise HTTPException(404, "Shipment not found")
