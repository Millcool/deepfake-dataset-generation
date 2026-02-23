import os, requests
for key in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(key, None)
base='https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token='409845ba5f1b4338af7c20cef0d6505e'
path='musetalk/results/preview/v15/preview_000_audio0.mp4'
url=f"{base}/files/{path}"
s=requests.Session(); s.trust_env=False
r=s.get(url,headers={'Authorization':f'token {token}'},allow_redirects=False,timeout=60)
print('status', r.status_code)
print('ctype', r.headers.get('content-type'))
print('location', r.headers.get('location'))
print('first20', r.content[:20])

r2=s.get(url+f"?token={token}",allow_redirects=False,timeout=60)
print('status2', r2.status_code)
print('ctype2', r2.headers.get('content-type'))
print('location2', r2.headers.get('location'))
print('first20_2', r2.content[:20])