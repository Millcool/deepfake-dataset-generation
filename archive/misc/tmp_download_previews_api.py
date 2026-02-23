import os
import base64
import urllib.parse
import requests

base = 'https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token = '409845ba5f1b4338af7c20cef0d6505e'
files = [
    'musetalk/results/preview/v15/preview_000_audio0.mp4',
    'musetalk/results/preview/v15/preview_001_audio1.mp4',
]
out_dir = 'MyStalkExamples'
os.makedirs(out_dir, exist_ok=True)

for key in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(key, None)

s = requests.Session()
s.trust_env = False
headers = {'Authorization': f'token {token}'}

for p in files:
    quoted = urllib.parse.quote(p)
    url = f"{base}/api/contents/{quoted}?content=1&format=base64"
    r = s.get(url, headers=headers, timeout=120)
    r.raise_for_status()
    j = r.json()
    if j.get('type') != 'file':
        raise RuntimeError(f'Unexpected type for {p}: {j.get("type")}')
    if j.get('format') != 'base64':
        raise RuntimeError(f'Unexpected format for {p}: {j.get("format")}')
    data = base64.b64decode(j['content'])
    out_path = os.path.join(out_dir, os.path.basename(p))
    with open(out_path, 'wb') as f:
        f.write(data)
    print('DOWNLOADED', p, '->', out_path, 'bytes', len(data))