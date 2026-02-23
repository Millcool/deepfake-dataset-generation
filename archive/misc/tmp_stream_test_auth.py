import os, requests
for key in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(key, None)
base='https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token='409845ba5f1b4338af7c20cef0d6505e'
path='musetalk/results/preview/v15/preview_000_audio0.mp4'
url=f"{base}/files/{path}"
s=requests.Session(); s.trust_env=False
r=s.get(url,headers={'Authorization':f'token {token}'},stream=True,timeout=(20,120),allow_redirects=False)
print('status', r.status_code)
print('ctype', r.headers.get('content-type'))
print('loc', r.headers.get('location'))
print('clen', r.headers.get('content-length'))
try:
    chunk = next(r.iter_content(chunk_size=8192))
    print('chunk_len', len(chunk), 'head', chunk[:16])
except StopIteration:
    print('no chunk')
r.close()