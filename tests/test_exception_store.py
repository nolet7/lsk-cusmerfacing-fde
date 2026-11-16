from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.exception_store import list_exceptions

def test_enterprise_read_model_requires_postgres(monkeypatch):
    monkeypatch.setenv("FDE_CASE_STORE","sqlite")
    with pytest.raises(HTTPException) as exc:
        list_exceptions("acme-air",10,0)
    assert exc.value.status_code==503

def test_exception_read_model_invalid_freshness_config(monkeypatch):
    monkeypatch.setenv("FDE_CASE_STORE","postgres")
    monkeypatch.setenv("EXCEPTION_MAX_AGE_SECONDS","1")
    with pytest.raises(HTTPException) as exc:
        list_exceptions("acme-air",10,0)
    assert exc.value.status_code==503
