"""Read-only ERP/WMS/TMS logistics integration using synthetic source-system adapters.

The three tables represent independent simulator sources. An actual integration must
replace these adapters with authenticated, bounded and observable upstream clients.
"""
import sqlite3
from datetime import date
from fastapi import APIRouter, Header, HTTPException, Query

router = APIRouter(prefix="/api/v1/logistics", tags=["logistics"])
_connect = None
_tenant = None

def configure(connect, tenant):
    global _connect, _tenant
    _connect, _tenant = connect, tenant

def initialize(connect):
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS erp_orders (
          order_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, customer TEXT NOT NULL,
          sku TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0),
          order_status TEXT NOT NULL, promised_date TEXT NOT NULL,
          warehouse_id TEXT NOT NULL, shipment_id TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS wms_inventory (
          tenant_id TEXT NOT NULL, warehouse_id TEXT NOT NULL, sku TEXT NOT NULL,
          on_hand INTEGER NOT NULL, reserved INTEGER NOT NULL, updated_at TEXT NOT NULL,
          PRIMARY KEY(tenant_id,warehouse_id,sku)
        );
        CREATE TABLE IF NOT EXISTS tms_shipments (
          shipment_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, order_id TEXT NOT NULL,
          carrier TEXT NOT NULL, tracking_number TEXT NOT NULL,
          shipment_status TEXT NOT NULL, estimated_delivery TEXT,
          delivered_at TEXT, last_event TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_erp_tenant ON erp_orders(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_tms_tenant_order ON tms_shipments(tenant_id,order_id);
        INSERT OR IGNORE INTO erp_orders VALUES
          ('SO-1001','acme-air','Acme Air','TURB-001',3,'Fulfilled','2026-11-10','WH-EAST','SHIP-1001'),
          ('SO-1002','acme-air','Acme Air','COMP-221',2,'Processing','2026-12-05','WH-EAST','SHIP-1002'),
          ('SO-2001','sky-jet','Sky Jet','TURB-001',1,'Fulfilled','2026-11-12','WH-WEST','SHIP-2001');
        INSERT OR IGNORE INTO wms_inventory VALUES
          ('acme-air','WH-EAST','TURB-001',18,5,'2026-11-09T12:00:00Z'),
          ('acme-air','WH-EAST','COMP-221',4,2,'2026-11-09T12:00:00Z'),
          ('sky-jet','WH-WEST','TURB-001',6,1,'2026-11-09T12:00:00Z');
        INSERT OR IGNORE INTO tms_shipments VALUES
          ('SHIP-1001','acme-air','SO-1001','DemoCarrier','TRACK-1001','In transit','2026-11-20',NULL,'Weather disruption','2026-11-15T09:00:00Z'),
          ('SHIP-1002','acme-air','SO-1002','DemoCarrier','TRACK-1002','Label created','2026-12-04',NULL,'Awaiting pickup','2026-11-15T09:00:00Z'),
          ('SHIP-2001','sky-jet','SO-2001','DemoCarrier','TRACK-2001','Delivered','2026-11-12','2026-11-12','Delivered to dock','2026-11-12T17:00:00Z');
        """)

def _identity(x_demo_tenant):
    # Explicitly synthetic tenant header. Not suitable for real customer authentication.
    return _tenant(x_demo_tenant)

def _rows(sql, params):
    with _connect() as db:
        return [dict(row) for row in db.execute(sql, params).fetchall()]

def _order(order_id, tenant_id):
    rows = _rows("SELECT * FROM erp_orders WHERE order_id=? AND tenant_id=?",
                 (order_id, tenant_id))
    if not rows:
        raise HTTPException(status_code=404, detail="Order not found")
    return rows[0]

def _snapshot(order, tenant_id, today):
    stock = _rows("""SELECT warehouse_id,sku,on_hand,reserved,updated_at
                     FROM wms_inventory WHERE tenant_id=? AND warehouse_id=? AND sku=?""",
                  (tenant_id,order["warehouse_id"],order["sku"]))
    shipment = _rows("""SELECT shipment_id,order_id,carrier,tracking_number,shipment_status,
                      estimated_delivery,delivered_at,last_event,updated_at
                      FROM tms_shipments WHERE tenant_id=? AND shipment_id=? AND order_id=?""",
                     (tenant_id,order["shipment_id"],order["order_id"]))
    inv = stock[0] if stock else None
    ship = shipment[0] if shipment else None
    available = max(inv["on_hand"] - inv["reserved"],0) if inv else None
    promised = date.fromisoformat(order["promised_date"])
    delivered = date.fromisoformat(ship["delivered_at"]) if ship and ship["delivered_at"] else None
    estimated = date.fromisoformat(ship["estimated_delivery"]) if ship and ship["estimated_delivery"] else None
    if not ship:
        reason = "SHIPMENT_DATA_MISSING"
    elif delivered:
        reason = "DELIVERED_LATE" if delivered > promised else None
    elif estimated and estimated > promised:
        reason = "ETA_AFTER_PROMISE"
    elif today > promised:
        reason = "PAST_DUE_NOT_DELIVERED"
    else:
        reason = None
    return {
      "order": {k:order[k] for k in ("order_id","customer","sku","quantity","order_status","promised_date","warehouse_id")},
      "inventory": {**inv,"available":available} if inv else None,
      "shipment":ship,
      "late_delivery": {"is_late_or_at_risk":reason is not None,"reason_code":reason,
                        "promised_date":order["promised_date"],
                        "estimated_delivery":ship["estimated_delivery"] if ship else None,
                        "delivered_at":ship["delivered_at"] if ship else None},
      "source_systems": {"order":"ERP simulator","inventory":"WMS simulator","shipment":"TMS simulator"},
      "as_of_date":today.isoformat(),
      "data_mode":"synthetic",
    }

@router.get("/orders/{order_id}")
def order_visibility(order_id: str, x_demo_tenant: str | None = Header(default=None)):
    who = _identity(x_demo_tenant)
    return _snapshot(_order(order_id,who),who,date.today())

@router.get("/inventory/{sku}")
def inventory(sku: str, x_demo_tenant: str | None = Header(default=None)):
    who = _identity(x_demo_tenant)
    return {"sku":sku,"locations":[{**r,"available":max(r["on_hand"]-r["reserved"],0)}
             for r in _rows("""SELECT warehouse_id,sku,on_hand,reserved,updated_at
                                FROM wms_inventory WHERE tenant_id=? AND sku=? ORDER BY warehouse_id""",
                            (who,sku))],"data_mode":"synthetic"}

@router.get("/shipments/{shipment_id}")
def shipment(shipment_id: str, x_demo_tenant: str | None = Header(default=None)):
    who = _identity(x_demo_tenant)
    rows = _rows("""SELECT shipment_id,order_id,carrier,tracking_number,shipment_status,
                    estimated_delivery,delivered_at,last_event,updated_at
                    FROM tms_shipments WHERE shipment_id=? AND tenant_id=?""",
                 (shipment_id,who))
    if not rows:
        raise HTTPException(status_code=404,detail="Shipment not found")
    return {**rows[0],"data_mode":"synthetic"}

@router.get("/exceptions")
def delivery_exceptions(x_demo_tenant: str | None = Header(default=None),
                        limit: int = Query(default=50,ge=1,le=100)):
    who = _identity(x_demo_tenant)
    orders = _rows("SELECT * FROM erp_orders WHERE tenant_id=? ORDER BY order_id LIMIT 100", (who,))
    exceptions = [s for s in (_snapshot(order,who,date.today()) for order in orders)
                  if s["late_delivery"]["is_late_or_at_risk"]]
    return {"count":len(exceptions),"items":exceptions[:limit],"data_mode":"synthetic"}
