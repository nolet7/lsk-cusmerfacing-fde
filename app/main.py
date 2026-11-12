"""Fictional aerospace customer-services legacy API and AI draft POC."""
import os
import sqlite3
import time
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

DB = Path(os.getenv("DEMO_DB", "/tmp/lsk_aerospace_demo.sqlite3"))
app = FastAPI(title="LSK Aerospace Customer Experience POC", version="0.1.0")

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def initialize():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
          order_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, customer TEXT NOT NULL,
          part_number TEXT NOT NULL, status TEXT NOT NULL, quality_hold INTEGER NOT NULL,
          promised_date TEXT, shipping_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cases (
          case_id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT NOT NULL,
          order_id TEXT NOT NULL, question TEXT NOT NULL, draft TEXT NOT NULL,
          approval_required INTEGER NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        INSERT OR IGNORE INTO orders VALUES
          ('WO-1001','acme-air','Acme Air','TURB-001','Inspection',0,'2026-12-02','Not shipped'),
          ('WO-2001','sky-jet','Sky Jet','COMP-221','Quality review',1,NULL,'Not shipped');
        """)

@app.on_event("startup")
def startup():
    initialize()

class Inquiry(BaseModel):
    order_id: str = Field(min_length=3,max_length=64)
    question: str = Field(min_length=3,max_length=1000)

def scoped_order(order_id: str, tenant_id: str):
    with connect() as con:
        row=con.execute("SELECT * FROM orders WHERE order_id=? AND tenant_id=?", (order_id, tenant_id)).fetchone()
    if not row:
        raise HTTPException(404,"Order not found for customer")
    return dict(row)

def tenant(value: str | None):
    # DEMO-ONLY shared header. Replace with validated OIDC token + RBAC before any pilot with real users.
    if not value or value not in {"acme-air","sky-jet"}:
        raise HTTPException(401,"Demo tenant header required")
    return value

@app.get("/health")
def health():
    return {"status":"ok","mode":"synthetic-demo"}

@app.get("/api/v1/orders/{order_id}")
def get_order(order_id:str, x_demo_tenant: str | None = Header(default=None)):
    return scoped_order(order_id,tenant(x_demo_tenant))

@app.post("/api/v1/inquiries")
def ask(inquiry:Inquiry,x_demo_tenant:str | None=Header(default=None)):
    started=time.perf_counter()
    who=tenant(x_demo_tenant)
    order=scoped_order(inquiry.order_id,who)
    # Explicit deterministic fallback, NOT represented as actual LLM inference.
    draft=(f"Order {order['order_id']} for {order['customer']}: status is {order['status']}; "
           f"shipping: {order['shipping_status']}. "
           + (f"Recorded target date: {order['promised_date']}. " if order['promised_date'] else "No target date is recorded. ")
           + ("Quality hold is active; consult your account manager. " if order['quality_hold'] else "")
           + "Source: ERP simulated order record. This is a draft, not a commercial or airworthiness commitment.")
    requires=any(t in inquiry.question.lower() for t in ("price","quote","guarantee","release","certif","commit","expedite","eta"))
    with connect() as con:
        cur=con.execute("INSERT INTO cases(tenant_id,order_id,question,draft,approval_required) VALUES (?,?,?,?,?)",
                        (who, inquiry.order_id,inquiry.question,draft,int(requires)))
        case_id=cur.lastrowid
    return {"case_id":case_id,"order_id":order["order_id"],"draft":draft,
            "source_ids":[order["order_id"]],"approval_required":requires,
            "ai_mode":"deterministic-fallback","elapsed_ms":round((time.perf_counter()-started)*1000,2)}

@app.get("/api/v1/cases")
def cases(x_demo_tenant:str | None=Header(default=None)):
    who=tenant(x_demo_tenant)
    with connect() as con:
        rows=con.execute("SELECT * FROM cases WHERE tenant_id=? ORDER BY case_id DESC LIMIT 100",(who,)).fetchall()
    return [dict(row) for row in rows]
