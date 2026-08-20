#!/usr/bin/env python3
"""Busca en AISA (gpt-5-search-api) y devuelve texto + URLs de fuente.
Uso: python3 aisa_search.py "tu consulta"
"""
import urllib.request, json, re, subprocess, sys, os

home = os.path.expanduser("~")
cfg = open(os.path.join(home, ".hermes", "config.yaml")).read()

# extraer bloque custom_aisa
m = re.search(r'custom_aisa:.*?(?=\n\S)', cfg, re.S)
block = m.group(0) if m else cfg
base = re.search(r'base_url:\s*(\S+)', block)
key = re.search(r'api_key:\s*(\S+)', block)
BASE = base.group(1) if base else "https://api.aisa.one/v1"
KEY = key.group(1) if key else ""

query = sys.argv[1] if len(sys.argv) > 1 else ""

payload = {"model": "gpt-5-search-api",
           "messages": [{"role": "user", "content": query}]}
req = urllib.request.Request(BASE + "/chat/completions",
    data=json.dumps(payload).encode(),
    headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=240) as r:
    d = json.loads(r.read().decode())

msg = d["choices"][0]["message"]
print(msg.get("content", ""))
print("\n===== FUENTES (URLs) =====")
for a in msg.get("annotations", []):
    if a.get("type") == "url_citation":
        print(a["url_citation"]["url"])
