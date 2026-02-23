import os
import csv
import io
import urllib.parse
import requests

BASE='https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
TOKEN='409845ba5f1b4338af7c20cef0d6505e'
MAN='musetalk/workspace/datasets/MuseTalk_FFpp_vox2/metadata/manifest_1000_named.csv'
OUTDIR='musetalk/workspace/datasets/MuseTalk_FFpp_vox2/outputs/results/v15'

for k in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
  os.environ.pop(k, None)

s=requests.Session(); s.trust_env=False
headers={'Authorization':f'token {TOKEN}', 'Range':'bytes=0-4095', 'Accept-Encoding':'identity'}
url=f"{BASE}/files/{MAN}"
r=s.get(url, headers=headers, timeout=(20,60))
r.raise_for_status()
chunk=r.content
text=chunk.decode('utf-8', errors='replace')

# Parse header + first 1-2 rows from partial CSV.
lines = [ln for ln in text.splitlines() if ln.strip()]
header = lines[0]
first = None
for ln in lines[1:]:
  if ln.count(',') >= header.count(','):
    first = ln
    break

if not first:
  raise SystemExit('could not parse first row')

buf = io.StringIO(header+'\n'+first+'\n')
row = next(csv.DictReader(buf))
idx = int(row['idx'])
name = row['result_name']

print('sample_idx', idx)
print('sample_name', name)

# Check existence
path = f"{OUTDIR}/{name}"
api=f"{BASE}/api/contents/{urllib.parse.quote(path)}?content=0"
r2=s.get(api, headers={'Authorization':f'token {TOKEN}'}, timeout=(20,60))
print('exists_status', r2.status_code)
if r2.status_code==200:
  j=r2.json(); print('size', j.get('size'), 'last_modified', j.get('last_modified'))
else:
  print(r2.text[:200])