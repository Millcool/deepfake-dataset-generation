import os
import urllib.parse
import requests

BASE = "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru"
TOKEN = "409845ba5f1b4338af7c20cef0d6505e"
REMOTE_PATH = "musetalk/workspace/datasets/MuseTalk_FFpp_vox2/rename_resume.py"

for k in ["HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy"]:
    os.environ.pop(k, None)

with open("rename_resume_remote_payload.py", "r", encoding="utf-8") as f:
    content = f.read()

s = requests.Session()
s.trust_env = False
headers = {"Authorization": f"token {TOKEN}"}
url = f"{BASE}/api/contents/{urllib.parse.quote(REMOTE_PATH)}"

payload = {
    "type": "file",
    "format": "text",
    "content": content,
}

r = s.put(url, headers=headers, json=payload, timeout=(20, 120))
print('status', r.status_code)
if r.status_code >= 400:
    print(r.text[:400])
r.raise_for_status()
print('uploaded', REMOTE_PATH)