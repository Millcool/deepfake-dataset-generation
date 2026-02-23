import os, re, requests
from datetime import datetime

base=os.environ['JUPYTER_BASE'].rstrip('/')
token=os.environ['JUPYTER_TOKEN']

# list logs directory
logs_path='hallo2/logs'
url=f"{base}/api/contents/{logs_path}?content=1"
s=requests.Session(); s.trust_env=False
r=s.get(url, headers={'Authorization': f'token {token}'}, timeout=60)
r.raise_for_status()
j=r.json()
items=j.get('content',[])
logs=[it for it in items if it.get('type')=='file' and re.match(r'^setup_env_.*\.log$', it.get('name',''))]
if not logs:
    print('no setup_env_*.log found')
    raise SystemExit(0)

def parse_ts(x):
    lm=x.get('last_modified')
    if not lm:
        return datetime.min
    # e.g. 2026-02-15T13:39:57.123456Z
    try:
        return datetime.fromisoformat(lm.replace('Z','+00:00'))
    except Exception:
        return datetime.min

logs.sort(key=parse_ts)
latest=logs[-1]
name=latest['name']
path=f"{logs_path}/{name}"
print('latest_log', path, 'size', latest.get('size'))

# tail via Contents API (JSON, content as text)
file_api=f"{base}/api/contents/{path}?content=1"
rf=s.get(file_api, headers={'Authorization': f'token {token}'}, timeout=180)
print('status', rf.status_code, 'len_raw', len(rf.content))
rf.raise_for_status()
jf=rf.json()
text=jf.get('content','')

# If the log is huge, only keep the tail region.
if len(text) > 200_000:
    text = text[-200_000:]

# sanitize ANSI
text=text.replace('\x1b','<ESC>')
lines=text.splitlines()[-120:]
print('--- tail ---')
for ln in lines:
    print(ln)
