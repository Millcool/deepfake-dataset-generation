import os, requests
for key in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(key, None)
base='https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token='409845ba5f1b4338af7c20cef0d6505e'
url=f"{base}/api/contents/musetalk/results/preview/v15/preview_000_audio0.mp4?content=1&format=base64"
s=requests.Session(); s.trust_env=False
r=s.get(url,headers={'Authorization':f'token {token}'},timeout=300)
print('status', r.status_code)
print('len_raw', len(r.content))
j=r.json()
print('type', j.get('type'), 'format', j.get('format'))
print('content_len', len(j.get('content','')))