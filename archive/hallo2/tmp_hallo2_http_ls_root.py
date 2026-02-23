import os, requests
base=os.environ['JUPYTER_BASE'].rstrip('/')
token=os.environ['JUPYTER_TOKEN']
s=requests.Session(); s.trust_env=False
r=s.get(f"{base}/api/contents?content=1", headers={'Authorization': f'token {token}'}, timeout=60)
print('status', r.status_code)
r.raise_for_status()
j=r.json()
print('cwd', j.get('path'), 'type', j.get('type'))
for it in j.get('content',[])[:50]:
    print(it.get('type'), it.get('name'))