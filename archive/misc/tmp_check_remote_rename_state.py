import os, urllib.parse, requests

base='https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token='409845ba5f1b4338af7c20cef0d6505e'

paths = [
  'musetalk/workspace/datasets/MuseTalk_FFpp_vox2/metadata/rename_resume_report.txt',
  'musetalk/workspace/datasets/MuseTalk_FFpp_vox2/metadata/manifest_1000_named.csv',
  'musetalk/workspace/datasets/MuseTalk_FFpp_vox2/metadata/inference_1000_named_remaining.yaml',
  'musetalk/workspace/datasets/MuseTalk_FFpp_vox2/.gen_1000_named.pid',
  'musetalk/workspace/datasets/MuseTalk_FFpp_vox2/logs/gen_1000_named.log',
]

for k in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
  os.environ.pop(k, None)

s=requests.Session(); s.trust_env=False
headers={'Authorization':f'token {token}'}

for p in paths:
  url=f"{base}/api/contents/{urllib.parse.quote(p)}?content=0"
  try:
    r=s.get(url, headers=headers, timeout=(20,60))
    print(p, 'status', r.status_code)
    if r.status_code==200:
      j=r.json(); print('  type', j.get('type'), 'size', j.get('size'), 'last_modified', j.get('last_modified'))
  except Exception as e:
    print(p, 'ERR', type(e).__name__, str(e)[:120])