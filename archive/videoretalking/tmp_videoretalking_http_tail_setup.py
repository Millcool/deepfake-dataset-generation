import os
import re
from datetime import datetime

import requests


base = os.environ["JUPYTER_BASE"].rstrip("/")
token = os.environ["JUPYTER_TOKEN"]

logs_path = "video-retalking/logs"
url = f"{base}/api/contents/{logs_path}?content=1"
s = requests.Session()
s.trust_env = False

r = s.get(url, headers={"Authorization": f"token {token}"}, timeout=60)
r.raise_for_status()
j = r.json()
items = j.get("content", [])

logs = [it for it in items if it.get("type") == "file" and re.match(r"^setup_.*\.log$", it.get("name", ""))]
if not logs:
    print("no setup_*.log found in", logs_path)
    raise SystemExit(0)


def parse_ts(x):
    lm = x.get("last_modified")
    if not lm:
        return datetime.min
    try:
        return datetime.fromisoformat(lm.replace("Z", "+00:00"))
    except Exception:
        return datetime.min


logs.sort(key=parse_ts)
latest = logs[-1]
name = latest["name"]
path = f"{logs_path}/{name}"
print("latest_log", path, "size", latest.get("size"))

file_api = f"{base}/api/contents/{path}?content=1"
rf = s.get(file_api, headers={"Authorization": f"token {token}"}, timeout=180)
print("status", rf.status_code, "len_raw", len(rf.content))
rf.raise_for_status()
jf = rf.json()
text = jf.get("content", "")

if len(text) > 200_000:
    text = text[-200_000:]

text = text.replace("\x1b", "<ESC>")
lines = text.splitlines()[-160:]
print("--- tail ---")
for ln in lines:
    print(ln)
