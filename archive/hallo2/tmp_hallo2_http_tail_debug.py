import os, requests
base=os.environ['JUPYTER_BASE'].rstrip('/')
token=os.environ['JUPYTER_TOKEN']
logs_path='hallo2/logs'
url=f"{base}/api/contents/{logs_path}?content=1"
s=requests.Session(); s.trust_env=False
r=s.get(url, headers={'Authorization': f'token {token}'}, timeout=60)
print('status', r.status_code)
print(r.text[:300])
j=r.json()
for it in j.get('content',[]):
    print(it.get('type'), repr(it.get('name')))