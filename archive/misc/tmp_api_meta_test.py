import os, requests
for key in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(key, None)
base='https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token='409845ba5f1b4338af7c20cef0d6505e'
url=f"{base}/api/contents/musetalk/results/preview/v15/preview_000_audio0.mp4?content=0"
s=requests.Session(); s.trust_env=False
r=s.get(url,headers={'Authorization':f'token {token}'},timeout=60)
print('status', r.status_code)
print('ctype', r.headers.get('content-type'))
print(r.text[:400])