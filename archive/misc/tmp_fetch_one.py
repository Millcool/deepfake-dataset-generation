import argparse
import os

import requests

parser = argparse.ArgumentParser()
parser.add_argument("--path", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--retries", type=int, default=6)
parser.add_argument("--chunk-size", type=int, default=262144)  # 256 KiB
args = parser.parse_args()
for k in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ.pop(k, None)
base = "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru"
token = "409845ba5f1b4338af7c20cef0d6505e"
url = f"{base}/files/{args.path}"

headers = {"Authorization": f"token {token}"}
s = requests.Session()
s.trust_env = False

expected = None
try:
    meta = s.get(
        f"{base}/api/contents/{args.path}?content=0",
        headers=headers,
        timeout=60,
    )
    if meta.ok:
        expected = meta.json().get("size")
except Exception:
    pass

tmp_path = args.out + ".part"
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

for attempt in range(1, args.retries + 1):
    # If we already downloaded expected size, stop.
    if expected is not None and os.path.exists(args.out) and os.path.getsize(args.out) == expected:
        print("already complete", args.out, "bytes", expected)
        raise SystemExit(0)

    start = os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0
    try:
        r = s.get(
            url,
            headers={**headers, "Range": f"bytes={start}-"} if start else headers,
            stream=True,
            timeout=(20, 180),
        )
        if r.status_code not in (200, 206):
            print("status", r.status_code, "attempt", attempt)
            r.raise_for_status()

        if expected is None:
            # Best-effort estimate from headers if API meta isn't available.
            try:
                expected = int(r.headers.get("content-length") or 0) + start or None
            except Exception:
                expected = None

        mode = "ab" if start else "wb"
        n = start
        with open(tmp_path, mode) as f:
            for ch in r.iter_content(args.chunk_size):
                if ch:
                    f.write(ch)
                    n += len(ch)
        r.close()

        if expected is None or n == expected:
            os.replace(tmp_path, args.out)
            print("wrote", n, "to", args.out)
            raise SystemExit(0)
        else:
            print("partial", n, "expected", expected, "attempt", attempt)
    except Exception as e:
        print("retry", attempt, "error", type(e).__name__, str(e)[:200])

print("failed to download after retries:", args.out)
raise SystemExit(1)
