import os
import re
from datetime import datetime

import requests


base = os.environ["JUPYTER_BASE"].rstrip("/")
token = os.environ["JUPYTER_TOKEN"]
headers = {"Authorization": f"token {token}"}

s = requests.Session()
s.trust_env = False

logs_path = "video-retalking/logs"
dir_api = f"{base}/api/contents/{logs_path}?content=1"
r = s.get(dir_api, headers=headers, timeout=60)
r.raise_for_status()
items = r.json().get("content", [])
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

# Try to get size via metadata (more reliable than directory listing).
meta_api = f"{base}/api/contents/{path}?content=0"
rm = s.get(meta_api, headers=headers, timeout=60)
rm.raise_for_status()
size = rm.json().get("size") or latest.get("size") or 0
size = int(size)

tail_bytes = 200_000
start = max(0, size - tail_bytes)

files_url = f"{base}/files/{path}"
rh = {"Range": f"bytes={start}-"} if size else {}
rf = s.get(files_url, headers={**headers, **rh}, timeout=(20, 180))
print("files_status", rf.status_code, "content_len", len(rf.content), "range_start", start)
rf.raise_for_status()

text = rf.content.decode("utf-8", errors="replace").replace("\x1b", "<ESC>")
lines = text.splitlines()[-160:]
print("--- tail ---")
for ln in lines:
    print(ln)

