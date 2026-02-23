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

# Preserve the current (bad) HTML stub, don't delete anything.
if os.path.exists(OUT_PATH) and os.path.getsize(OUT_PATH) < 100_000:
    bad_path = OUT_PATH + ".bad_" + str(int(time.time()))
    os.replace(OUT_PATH, bad_path)
    print("renamed_bad", bad_path)

s = requests.Session()
s.trust_env = False
headers = {"Authorization": f"token {TOKEN}", "Accept-Encoding": "identity", "Connection": "close"}

# Get expected size from Jupyter Contents API.
meta = s.get(f"{BASE}/api/contents/{REMOTE_PATH}?content=0", headers=headers, timeout=60)
meta.raise_for_status()
expected = int(meta.json()["size"])
print("expected", expected)

url = f"{BASE}/files/{REMOTE_PATH}"
chunk = 256 * 1024

have = os.path.getsize(PART_PATH) if os.path.exists(PART_PATH) else 0
if have > expected:
    # Something weird; keep it and start fresh in a new part file.
    alt = PART_PATH + ".bad_" + str(int(time.time()))
    os.replace(PART_PATH, alt)
    have = 0
    print("renamed_part_bad", alt)

mode = "ab" if have else "wb"
with open(PART_PATH, mode) as f:
    offset = have
    while offset < expected:
        end = min(expected - 1, offset + chunk - 1)
        ok = False
        for attempt in range(1, 11):
            try:
                r = s.get(
                    url,
                    headers={**headers, "Range": f"bytes={offset}-{end}"},
                    stream=True,
                    timeout=(20, 90),
                )
                if r.status_code not in (200, 206):
                    raise RuntimeError(f"status {r.status_code}")
                data = r.content
                r.close()
                if len(data) != (end - offset + 1):
                    raise RuntimeError(f"short read {len(data)} expected {end - offset + 1}")
                f.write(data)
                offset += len(data)
                print("got", offset, "/", expected)
                ok = True
                break
            except Exception as e:
                print("retry", attempt, "range", offset, end, "err", type(e).__name__)
                time.sleep(min(5, attempt))
        if not ok:
            raise SystemExit(1)

os.replace(PART_PATH, OUT_PATH)
print("done", OUT_PATH, os.path.getsize(OUT_PATH))