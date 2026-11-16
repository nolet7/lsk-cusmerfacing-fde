"""Identity boundary for customer-initiated logistics requests.

Demo mode is ONLY intended for loopback/local development.
Enterprise mode validates Microsoft Entra ID access JWTs via JWKS; application
roles must be assigned on the Entra app registration. Tenant is a verified claim.
"""
import os
from functools import lru_cache
from fastapi import Header, HTTPException
import jwt
from jwt import PyJWKClient

@lru_cache(maxsize=4)
def jwks_client(url: str):
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300, timeout=3)

def _resolve_tenant(x_demo_tenant: str | None, authorization: str | None, required_role: str):
    mode=os.getenv("FDE_IDENTITY_MODE","demo").lower()
    if mode=="demo":
        if os.getenv("FDE_ENV","local").lower() not in ("local","test"):
            raise HTTPException(503,"Demo identity prohibited in deployed environments")
        if x_demo_tenant not in ("acme-air","sky-jet"):
            raise HTTPException(401,"Demo tenant header required")
        return x_demo_tenant
    if mode != "entra":
        raise HTTPException(503,"Unsupported identity mode")
    tenant_id=os.getenv("ENTRA_TENANT_ID")
    audience=os.getenv("ENTRA_API_AUDIENCE")
    if not tenant_id or not audience:
        raise HTTPException(503,"Entra identity configuration missing")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401,"Bearer access token required")
    token=authorization.removeprefix("Bearer ").strip()
    issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0"
    try:
        key=jwks_client(f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys").get_signing_key_from_jwt(token)
        claims=jwt.decode(token,key.key,algorithms=["RS256"],
                          audience=audience,issuer=issuer,options={"require":["exp","iss","aud","iat"]},
                          leeway=30)
    except (jwt.PyJWTError,ValueError,TimeoutError):
        raise HTTPException(401,"Invalid access token") from None
    if claims.get("tid") != tenant_id:
        raise HTTPException(403,"Identity tenant mismatch")
    roles=claims.get("roles") or []
    if not isinstance(roles,list) or required_role not in roles:
        raise HTTPException(403,f"{required_role} application role required")
    # Claim must be populated by an approved Entra claims-mapping policy or issued
    # by a trusted API token exchange; do NOT accept a browser-supplied tenant ID.
    customer=claims.get("customer_tenant_id")
    if not isinstance(customer,str) or not customer or len(customer)>64:
        raise HTTPException(403,"Verified customer_tenant_id claim required")
    return customer

def authorized_tenant(
    x_demo_tenant: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    return _resolve_tenant(x_demo_tenant,authorization,"Logistics.Read")

def authorized_write_tenant(
    x_demo_tenant: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    return _resolve_tenant(x_demo_tenant,authorization,"Logistics.Write")
