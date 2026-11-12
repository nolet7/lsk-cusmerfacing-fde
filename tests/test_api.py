import os
import tempfile
from pathlib import Path
os.environ["DEMO_DB"]=str(Path(tempfile.gettempdir())/"lsk_poc_test.sqlite3")
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as client:
        assert client.get("/health").status_code==200

def test_scope_and_approval():
    with TestClient(app) as client:
        good=client.get("/api/v1/orders/WO-1001",headers={"X-Demo-Tenant":"acme-air"})
        assert good.status_code==200
        assert client.get("/api/v1/orders/WO-2001",headers={"X-Demo-Tenant":"acme-air"}).status_code==404
        result=client.post("/api/v1/inquiries",headers={"X-Demo-Tenant":"acme-air"},
                         json={"order_id":"WO-1001","question":"Can you guarantee a quote?"})
        assert result.status_code==200
        assert result.json()["approval_required"] is True
        assert result.json()["ai_mode"]=="deterministic-fallback"
