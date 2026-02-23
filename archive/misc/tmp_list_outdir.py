import os, urllib.parse, requests
for k in ["HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy"]:
    os.environ.pop(k, None)
base='https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru'
token='409845ba5f1b4338af7c20cef0d6505e'
path='musetalk/workspace/datasets/MuseTalk_FFpp_vox2/outputs/results/v15'
url=f"{base}/api/contents/{urllib.parse.quote(path)}?content=1"
r=requests.get(url, headers={'Authorization':f'token {token}'}, timeout=(20, 600))
print('status', r.status_code)
r.raise_for_status()
j=r.json()
items=j.get('content') or []
done=sum(1 for it in items if it.get('type')=='file' and it.get('name','').startswith('fake_') and it.get('name','').endswith('.mp4'))
print('items', len(items))
print('done', done)
print('left', 1000-done)