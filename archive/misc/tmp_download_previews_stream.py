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

for key in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(key, None)

s = requests.Session()
s.trust_env = False
headers = {'Authorization': f'token {token}'}

for p in files:
    url = f"{base}/files/{p}"
    out_path = os.path.join(out_dir, os.path.basename(p))
    with s.get(url, headers=headers, stream=True, timeout=(20, 180)) as r:
        r.raise_for_status()
        total = 0
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*128):
                if chunk:
                    f.write(chunk)
                    total += len(chunk)
    print('DOWNLOADED', p, '->', out_path, 'bytes', total)