"""Contract and cross-tenant regression tests for synthetic logistics APIs."""
import os
import tempfile
from pathlib import Path
os.environ["DEMO_DB"] = str(Path(tempfile.gettempdir()) / "lsk_logistics_test.sqlite3")
from fastapi.testclient import TestClient
from app.main import app

def test_unified_visibility_and_delay_detection():
    with TestClient(app) as client:
        h={"X-Demo-Tenant":"acme-air"}
        res=client.get("/api/v1/logistics/orders/SO-1001",headers=h)
        assert res.status_code == 200
        data=res.json()
        assert data["order"]["order_status"] == "Fulfilled"
        assert data["inventory"]["available"] == 13
        assert data["shipment"]["tracking_number"] == "TRACK-1001"
        assert data["late_delivery"]["reason_code"] == "ETA_AFTER_PROMISE"
        assert data["source_systems"]["shipment"] == "TMS simulator"

def test_inventory_tracking_and_exception_api():
    with TestClient(app) as client:
        h={"X-Demo-Tenant":"acme-air"}
        stock=client.get("/api/v1/logistics/inventory/COMP-221",headers=h)
        assert stock.status_code == 200
        assert stock.json()["locations"][0]["available"] == 2
        ship=client.get("/api/v1/logistics/shipments/SHIP-1001",headers=h)
        assert ship.status_code == 200
        assert ship.json()["last_event"] == "Weather disruption"
        exceptions=client.get("/api/v1/logistics/exceptions",headers=h)
        assert exceptions.status_code == 200
        assert "SO-1001" in [v["order"]["order_id"] for v in exceptions.json()["items"]]

def test_cross_tenant_and_missing_identity_are_blocked():
    with TestClient(app) as client:
        a={"X-Demo-Tenant":"acme-air"}
        b={"X-Demo-Tenant":"sky-jet"}
        assert client.get("/api/v1/logistics/orders/SO-2001",headers=a).status_code == 404
        assert client.get("/api/v1/logistics/shipments/SHIP-2001",headers=a).status_code == 404
        assert client.get("/api/v1/logistics/inventory/TURB-001",headers=a).json()["locations"][0]["warehouse_id"] == "WH-EAST"
        assert client.get("/api/v1/logistics/orders/SO-2001",headers=b).status_code == 200
        assert client.get("/api/v1/logistics/exceptions").status_code == 401
        assert client.get("/api/v1/logistics/orders/SO-1001").status_code == 401
        assert client.get("/api/v1/logistics/shipments/SHIP-1001").status_code == 401

def test_invalid_limits_rejected():
    with TestClient(app) as client:
        assert client.get("/api/v1/logistics/exceptions?limit=0",headers={"X-Demo-Tenant":"acme-air"}).status_code == 422
