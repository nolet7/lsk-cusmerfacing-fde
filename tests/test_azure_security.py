import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_enterprise_identity_fail_closed_without_bearer(monkeypatch):
    monkeypatch.setenv("FDE_ENV","production")
    monkeypatch.setenv("FDE_CASE_STORE","postgres")
    monkeypatch.setenv("DATABASE_URL","postgresql://placeholder:placeholder@localhost:5432/placeholder")
    monkeypatch.setenv("FDE_IDENTITY_MODE","entra")
    monkeypatch.setenv("ENTRA_TENANT_ID","00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_API_AUDIENCE","api://lsk-logistics")
    with TestClient(app) as client:
        response=client.get("/api/v2/logistics/orders/SO-1001",headers={"X-Demo-Tenant":"acme-air"})
        assert response.status_code==401

def test_invalid_bearer_rejected(monkeypatch):
    monkeypatch.setenv("FDE_ENV","production")
    monkeypatch.setenv("FDE_CASE_STORE","postgres")
    monkeypatch.setenv("DATABASE_URL","postgresql://placeholder:placeholder@localhost:5432/placeholder")
    monkeypatch.setenv("FDE_IDENTITY_MODE","entra")
    monkeypatch.setenv("ENTRA_TENANT_ID","00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_API_AUDIENCE","api://lsk-logistics")
    with TestClient(app) as client:
        response=client.get("/api/v2/logistics/orders/SO-1001",headers={"Authorization":"Bearer not-a-jwt"})
        assert response.status_code==401

def test_demo_mode_forbidden_outside_local(monkeypatch):
    monkeypatch.setenv("FDE_ENV","production")
    monkeypatch.setenv("FDE_CASE_STORE","postgres")
    monkeypatch.setenv("DATABASE_URL","postgresql://placeholder:placeholder@localhost:5432/placeholder")
    monkeypatch.setenv("FDE_IDENTITY_MODE","demo")
    monkeypatch.setenv("FDE_CASE_STORE","sqlite")
    with pytest.raises(RuntimeError, match="Deployed environments require"):
        with TestClient(app):
            pass

def test_read_role_cannot_create_investigation(monkeypatch):
    from unittest.mock import patch, MagicMock
    from fastapi import HTTPException
    from app.identity import _resolve_tenant
    monkeypatch.setenv("FDE_ENV","production")
    monkeypatch.setenv("FDE_IDENTITY_MODE","entra")
    monkeypatch.setenv("ENTRA_TENANT_ID","00000000-0000-0000-0000-000000000001")
    monkeypatch.setenv("ENTRA_API_AUDIENCE","api://lsk-logistics")
    read_claims={"tid":"00000000-0000-0000-0000-000000000001",
                 "roles":["Logistics.Read"],"customer_tenant_id":"acme-air"}
    with patch("app.identity.jwks_client") as jwks, patch("app.identity.jwt.decode",return_value=read_claims):
        jwks.return_value.get_signing_key_from_jwt.return_value.key="mock-key"
        assert _resolve_tenant(None,"Bearer test-token","Logistics.Read")=="acme-air"
        with pytest.raises(HTTPException) as exc:
            _resolve_tenant(None,"Bearer test-token","Logistics.Write")
        assert exc.value.status_code==403
