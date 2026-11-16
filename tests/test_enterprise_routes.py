from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app

def test_enterprise_exception_api_paginates_without_fanout(monkeypatch):
    monkeypatch.setenv("FDE_ENV","production")
    monkeypatch.setenv("FDE_IDENTITY_MODE","entra")
    monkeypatch.setenv("FDE_CASE_STORE","postgres")
    monkeypatch.setenv("ENTRA_TENANT_ID","00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_API_AUDIENCE","api://lsk-logistics")
    monkeypatch.setenv("DATABASE_URL","postgresql://example.invalid/db")
    with patch("app.identity.authorized_tenant",return_value="acme-air"):
        # Dependency overrides affect the original dependency callable.
        from app.identity import authorized_tenant
        app.dependency_overrides[authorized_tenant] = lambda: "acme-air"
        try:
            with patch("app.exception_store.list_exceptions",return_value={"items":[],"limit":25,"offset":5}) as store:
                # Startup is mocked to avoid hitting external PG during route unit test.
                with patch("app.main.initialize"), patch("app.fde_integration.initialize"):
                    with TestClient(app) as client:
                        res=client.get("/api/v2/logistics/exceptions?limit=25&offset=5")
                        assert res.status_code==200, res.text
                        store.assert_called_once_with("acme-air",limit=25,offset=5)
        finally:
            app.dependency_overrides.clear()

def test_enterprise_insecure_source_rejected(monkeypatch):
    from app.fde_integration import config
    monkeypatch.setenv("FDE_ENV","production")
    monkeypatch.setenv("ERP_BASE_URL","http://erp.internal")
    monkeypatch.setenv("WMS_BASE_URL","https://wms.internal")
    monkeypatch.setenv("TMS_BASE_URL","https://tms.internal")
    monkeypatch.setenv("DEMO_CONNECTOR_TOKEN","demo")
    try:
        config()
        assert False,"Expected HTTPException for insecure upstream"
    except HTTPException as exc:
        assert exc.status_code==503
