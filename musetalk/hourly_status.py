import csv
import json
import os
import time
import urllib.parse
from typing import Dict, Optional, Tuple

import requests

BASE = os.environ.get("MIEM_BASE", "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru")
TOKEN = os.environ.get("MIEM_TOKEN", "409845ba5f1b4338af7c20cef0d6505e")

ROOT = "musetalk/workspace/datasets/MuseTalk_FFpp_vox2"
OUT_DIR = f"{ROOT}/outputs/results/v15"
MANIFEST_REMOTE = f"{ROOT}/metadata/manifest_1000_named.csv"
REPORT_REMOTE = f"{ROOT}/metadata/rename_resume_report.txt"
LOG_REMOTE = f"{ROOT}/logs/gen_1000_named.log"
TOTAL = 1000

STATE_PATH = os.path.join(os.path.dirname(__file__), ".musetalk_gen1000_status.json")
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
MANIFEST_LOCAL = os.path.join(CACHE_DIR, "manifest_1000_named.csv")

for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(k, None)

s = requests.Session()
s.trust_env = False
headers = {"Authorization": f"token {TOKEN}", "Accept-Encoding": "identity", "Connection": "close"}


def api_get(path: str, **params):
    q = "&".join(
        [f"{urllib.parse.quote(str(k))}={urllib.parse.quote(str(v))}" for k, v in params.items()]
    )
    url = f"{BASE}/api/contents/{urllib.parse.quote(path)}" + (f"?{q}" if q else "")
    r = s.get(url, headers={"Authorization": headers["Authorization"]}, timeout=(20, 60))
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def files_get(path: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    url = f"{BASE}/files/{path}"
    for attempt in range(1, 6):
        try:
            with s.get(url, headers=headers, stream=True, timeout=(20, 120)) as r:
                r.raise_for_status()
                tmp = out_path + ".part"
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1024 * 128):
                        if chunk:
                            f.write(chunk)
                os.replace(tmp, out_path)
                return
        except Exception:
            time.sleep(min(5, attempt))
    raise RuntimeError(f"Failed to download {path}")


def load_state():
    if not os.path.exists(STATE_PATH):
        return {"max_idx": -1, "updated_at": 0}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"max_idx": -1, "updated_at": 0}


def save_state(st):
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=True, indent=2)
    os.replace(tmp, STATE_PATH)


def ensure_manifest_local() -> None:
    remote = api_get(MANIFEST_REMOTE, content=0)
    if remote is None:
        raise RuntimeError(f"Remote manifest not found: {MANIFEST_REMOTE}")

    remote_mtime = remote.get("last_modified") or ""
    if os.path.exists(MANIFEST_LOCAL):
        st = load_state()
        if (st.get("manifest_last_modified") or "") == remote_mtime:
            return

    files_get(MANIFEST_REMOTE, MANIFEST_LOCAL)
    st = load_state()
    st["manifest_last_modified"] = remote_mtime
    save_state(st)


def load_idx_to_name() -> Dict[int, str]:
    ensure_manifest_local()
    m: Dict[int, str] = {}
    with open(MANIFEST_LOCAL, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            m[int(row["idx"])] = row["result_name"]
    if len(m) != TOTAL:
        raise RuntimeError(f"Expected {TOTAL} rows in manifest, got {len(m)}")
    return m


def exists_output(idx: int, idx_to_name: Dict[int, str]):
    name = idx_to_name[idx]
    p = f"{OUT_DIR}/{name}"
    return api_get(p, content=0)


def find_max_existing(idx_to_name: Dict[int, str]) -> int:
    if exists_output(0, idx_to_name) is None:
        return -1
    if exists_output(TOTAL - 1, idx_to_name) is not None:
        return TOTAL - 1

    lo, hi = 0, TOTAL - 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if exists_output(mid, idx_to_name) is not None:
            lo = mid
        else:
            hi = mid
    return lo


def read_new_pid_from_report() -> Optional[str]:
    rep = api_get(REPORT_REMOTE, content=1, format="text")
    if not rep or not rep.get("content"):
        return None
    # content=1&format=text returns raw text in "content".
    text = rep["content"]
    for line in str(text).splitlines():
        if line.startswith("NEW_PID "):
            return line.split(" ", 1)[1].strip()
    return None


def main() -> int:
    idx_to_name = load_idx_to_name()

    st = load_state()
    prev = int(st.get("max_idx") or -1)

    max_idx = find_max_existing(idx_to_name)
    done_est = max_idx + 1
    left_est = max(0, TOTAL - done_est)

    newest_meta = exists_output(max_idx, idx_to_name) if max_idx >= 0 else None
    log_meta = api_get(LOG_REMOTE, content=0)
    pid = read_new_pid_from_report()

    print(f"DONE_EST={done_est}")
    print(f"LEFT_EST={left_est}")
    if prev >= 0:
        print(f"DELTA_SINCE_LAST={done_est - (prev + 1)}")
    if newest_meta:
        print(
            "NEWEST=",
            newest_meta.get("name"),
            "last_modified=",
            newest_meta.get("last_modified"),
            "size=",
            newest_meta.get("size"),
        )
    if pid:
        print(f"PID={pid}")
    if log_meta:
        print("LOG_LAST_MODIFIED=", log_meta.get("last_modified"), "LOG_SIZE=", log_meta.get("size"))

    st["max_idx"] = max_idx
    st["updated_at"] = time.time()
    save_state(st)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
