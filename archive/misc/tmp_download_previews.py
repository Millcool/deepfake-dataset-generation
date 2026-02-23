import os
import requests

base = 'https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token = '409845ba5f1b4338af7c20cef0d6505e'
files = [
    'musetalk/results/preview/v15/preview_000_audio0.mp4',
    'musetalk/results/preview/v15/preview_001_audio1.mp4',
]
out_dir = 'MyStalkExamples'
os.makedirs(out_dir, exist_ok=True)

s = requests.Session()
s.trust_env = False
for key in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(key, None)

for p in files:
    url = f"{base}/files/{p}?token={token}"
    r = s.get(url, timeout=120)
    r.raise_for_status()
    name = os.path.basename(p)
    out_path = os.path.join(out_dir, name)
    with open(out_path, 'wb') as f:
        f.write(r.content)
    print('DOWNLOADED', p, '->', out_path, 'bytes', len(r.content))