#!/usr/bin/env python3
"""Run from host after: docker compose -f deploy/compose.yaml up --build -d."""
import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:18641"
def call(method,path,tenant="acme-air",payload=None):
    headers={"X-Demo-Tenant":tenant} if tenant else {}
    data=json.dumps(payload).encode() if payload is not None else None
    if data:
        headers["Content-Type"]="application/json"
    request=urllib.request.Request(BASE+path,headers=headers,data=data,method=method)
    try:
        with urllib.request.urlopen(request,timeout=15) as response:
            return response.status,json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code,json.loads(error.read())

def run():
    status,order=call("GET","/api/v2/logistics/orders/SO-1001")
    assert status==200,(status,order)
    assert order["order"]["order_id"]=="SO-1001"
    assert order["inventory"]["available"]==13
    assert order["shipment"]["shipment_id"]=="SHIP-1001"
    assert order["late_delivery"]["reason_code"]=="ETA_AFTER_PROMISE"
    assert order["data_mode"]=="synthetic-http-integration"

    status,other=call("GET","/api/v2/logistics/orders/SO-2001")
    assert status==404,(status,other)
    status,none=call("GET","/api/v2/logistics/orders/SO-1001",tenant=None)
    assert status==401,(status,none)

    status,exceptions=call("GET","/api/v2/logistics/exceptions")
    assert status==200,(status,exceptions)
    assert any(item["order"]["order_id"]=="SO-1001" for item in exceptions["items"])

    status,created=call("POST","/api/v2/logistics/investigations",payload={
        "order_id":"SO-1001","note":"Review carrier disruption; human owner to follow up."
    })
    assert status==201,(status,created)
    assert created["status"]=="OPEN"
    status,cases=call("GET","/api/v2/logistics/investigations")
    assert status==200,(status,cases)
    assert any(item["investigation_id"]==created["investigation_id"] for item in cases["items"])
    status,other_cases=call("GET","/api/v2/logistics/investigations",tenant="sky-jet")
    assert status==200 and all(x["order_id"]!="SO-1001" for x in other_cases["items"])
    print("PASS: networked ERP/WMS/TMS lookup, exception, investigation and demo tenant isolation")

if __name__=="__main__":
    run()
