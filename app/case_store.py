"""PostgreSQL investigation persistence for Azure; SQLite only for local demo.

Migrations are explicit: run migrations/001_investigations.sql via controlled pipeline.
Connections use TLS via DATABASE_URL parameters (sslmode=verify-full recommended).
"""
import os
from fastapi import HTTPException

def is_postgres():
    return os.getenv("FDE_CASE_STORE","sqlite").lower()=="postgres"

def _postgres():
    import psycopg
    from psycopg.rows import dict_row
    url=os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(503,"DATABASE_URL not configured")
    return psycopg.connect(url,connect_timeout=5,row_factory=dict_row)

def create_investigation(tenant_id,order_id,reason,note,local_connect):
    if is_postgres():
        with _postgres() as db:
            row=db.execute("""INSERT INTO investigations(tenant_id,order_id,reason_code,note,status)
                              VALUES (%s,%s,%s,%s,'OPEN') RETURNING investigation_id""",
                           (tenant_id,order_id,reason,note)).fetchone()
            return row["investigation_id"]
    if os.getenv("FDE_ENV","local") not in ("local","test"):
        raise HTTPException(503,"SQLite case store prohibited in deployed environments")
    with local_connect() as db:
        cursor=db.execute("INSERT INTO investigations(tenant_id,order_id,reason_code,note) VALUES (?,?,?,?)",
                          (tenant_id,order_id,reason,note))
        return cursor.lastrowid

def list_investigations(tenant_id,local_connect):
    if is_postgres():
        with _postgres() as db:
            rows=db.execute("""SELECT investigation_id,order_id,reason_code,note,status,created_at
                               FROM investigations WHERE tenant_id=%s
                               ORDER BY investigation_id DESC LIMIT 100""",(tenant_id,)).fetchall()
            return [{**r,"created_at":r["created_at"].isoformat()} for r in rows]
    if os.getenv("FDE_ENV","local") not in ("local","test"):
        raise HTTPException(503,"SQLite case store prohibited in deployed environments")
    with local_connect() as db:
        rows=db.execute("""SELECT investigation_id,order_id,reason_code,note,status,created_at
                           FROM investigations WHERE tenant_id=? ORDER BY investigation_id DESC LIMIT 100""",
                        (tenant_id,)).fetchall()
        return [dict(r) for r in rows]
