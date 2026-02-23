import os
import time
import requests

BASE = "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru"
TOKEN = "409845ba5f1b4338af7c20cef0d6505e"
REMOTE_PATH = "musetalk/results/preview/v15/preview_001_audio1.mp4"
OUT_PATH = os.path.join("MyStalkExamples", "preview_001_audio1.mp4")
PART_PATH = OUT_PATH + ".part"

for k in ["HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy"]:
    os.environ.pop(k, None)

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

s = requests.Session()
s.trust_env = False
headers = {"Authorization": f"token {TOKEN}", "Accept-Encoding": "identity", "Connection": "close"}

meta = s.get(f"{BASE}/api/contents/{REMOTE_PATH}?content=0", headers=headers, timeout=60)
meta.raise_for_status()
expected = int(meta.json()["size"])
print("expected", expected)

url = f"{BASE}/files/{REMOTE_PATH}"
chunk = 32 * 1024

offset = 0
with open(PART_PATH, "wb") as f:
    while offset < expected:
        end = min(expected - 1, offset + chunk - 1)
        for attempt in range(1, 31):
            try:
                r = s.get(
                    url,
                    headers={**headers, "Range": f"bytes={offset}-{end}"},
                    timeout=(20, 60),
                )
                if r.status_code not in (200, 206):
                    raise RuntimeError(f"status {r.status_code}")
                data = r.content
                r.close()
                need = end - offset + 1
                if len(data) != need:
                    raise RuntimeError(f"short {len(data)} need {need}")
                f.write(data)
                offset += len(data)
                if offset % (256*1024) == 0 or offset == expected:
                    print("got", offset, "/", expected)
                break
            except Exception as e:
                if attempt == 30:
                    raise
                time.sleep(1)

os.replace(PART_PATH, OUT_PATH)
print("done", OUT_PATH, os.path.getsize(OUT_PATH))