# POC implementation and demo

## Scope
Legacy-first Python/FastAPI + SQLite order repository; versioned REST/JSON, customer inquiry workflow and static browser portal. Two fictional aerospace customer accounts test account isolation. A deterministic answer composer demonstrates authorized retrieval and review routing; it is **not** an LLM.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate   # Windows Git Bash
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 18641
pytest -q
```
Open `frontend/index.html` with a local static server. Since the UI uses same-origin requests, serve it through a reverse proxy pointing `/api` to port 18641 or use curl:
```bash
curl -H 'X-Demo-Tenant: acme-air' http://127.0.0.1:18641/api/v1/orders/WO-1001
curl -H 'X-Demo-Tenant: acme-air' -H 'Content-Type: application/json' -d '{"order_id":"WO-1001","question":"Can you guarantee a quote?"}' http://127.0.0.1:18641/api/v1/inquiries
```

## Demo script
1. Show work order WO-1001 under Acme Air; ask a routine progress question.
2. Ask for a guaranteed quote; show `approval_required=true`.
3. Attempt WO-2001 as Acme Air; prove 404 tenant isolation.
4. Switch to Sky Jet and review a quality-held order; show no invented ETA.
5. Open /docs to explain contracts and integration mappings.

## Acceptance criteria
Automated tests green; repeatable setup; no external credentials; tenant negative test; deterministic outputs explicitly labeled. Real hosted LLM integration requires a security-approved provider and evaluation; not claimed to exist in this POC.
