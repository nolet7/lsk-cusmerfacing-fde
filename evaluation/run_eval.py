"""Run repeatable tenant-boundary and approval tests against a running API."""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

BASE=os.getenv("BASE_URL","http://127.0.0.1:18641")
cases=json.loads((Path(__file__).parent/"pilot_cases.json").read_text())
failures=[]
for i,case in enumerate(cases,1):
    req=urllib.request.Request(BASE+"/api/v1/inquiries",
       data=json.dumps({"order_id":case["order_id"],"question":case["question"]}).encode(),
       headers={"Content-Type":"application/json","X-Demo-Tenant":case["tenant"]},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=5) as res:
            status=res.status; body=json.load(res)
    except urllib.error.HTTPError as e:
        status=e.code;body={}
    passed=status==case["expected_status"]
    if passed and status==200:
        passed=body["approval_required"]==case["approval_required"]
    print(f"case={i} expected={case['expected_status']} actual={status} pass={passed}")
    if not passed:failures.append(i)
assert not failures, f"Failed cases: {failures}"
print(f"Passed {len(cases)} synthetic pilot smoke tests; this is not a full model evaluation.")
