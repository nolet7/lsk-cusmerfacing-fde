"""Optional real inference via OpenAI-compatible Chat Completions endpoint.
Only allowlisted synthetic order fields are sent. Never give the model DB credentials.
"""
import json
import os
from urllib.request import Request, urlopen

def answer(order:dict, question:str):
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    model=os.getenv("OPENAI_MODEL","gpt-4.1-mini")
    url=os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1").rstrip("/") + "/chat/completions"
    facts={k:order[k] for k in ("order_id","status","quality_hold","promised_date","shipping_status")}
    policy=("Answer solely using supplied work-order facts. Do not invent ETAs, price, approvals, "
            "shipping, certifications, or release permissions. If unknown say unknown. "
            "State that this is a draft requiring human review. Return plain concise English.")
    payload={"model":model,"temperature":0,"messages":[
      {"role":"system","content":policy},
      {"role":"user","content":json.dumps({"question":question,"facts":facts})}]}
    req=Request(url,data=json.dumps(payload).encode("utf-8"),
                headers={"Authorization":"Bearer "+api_key,"Content-Type":"application/json"},
                method="POST")
    with urlopen(req, timeout=12) as resp:
        output=json.load(resp)
    draft=output["choices"][0]["message"]["content"]
    if not isinstance(draft,str) or not draft.strip():
        raise ValueError("Model did not return text")
    return draft.strip()
