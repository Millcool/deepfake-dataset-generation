"""
Синхронизация runs с удалённого сервера MIEM через Jupyter Contents API.

Стратегия:
- sync() — БЫСТРАЯ: скачать только metrics.json для новых runs (~1 сек на run)
  → runs мгновенно появляются в дашборде
- sync_extras() — ФОНОВАЯ: скачать scores.csv и figures (может быть медленно)
  → ROC кривые и галерея появляются позже
"""

import os
import time
import base64
import threading
import requests

# Конфигурация
REMOTE_BASE = "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru"
REMOTE_RUNS_PATH = "detection_eval/runs"

# Состояние
_sync_lock = threading.Lock()
_last_sync = 0
_sync_status = {"last_sync": None, "runs_synced": 0, "error": None, "in_progress": False}
_extras_running = False

MIN_SYNC_INTERVAL = 15

# Таймауты
TIMEOUT_LIST = 10
TIMEOUT_SMALL = 20
TIMEOUT_LARGE = 60


def _get_session(token):
    for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
        os.environ.pop(k, None)
    s = requests.Session()
    s.trust_env = False
    s.headers["Authorization"] = f"token {token}"
    return s


def _api_get(session, path, timeout=TIMEOUT_SMALL):
    url = f"{REMOTE_BASE}/api/contents/{path}"
    try:
        r = session.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except (requests.Timeout, requests.ConnectionError):
        pass
    return None


def _download_text(session, remote_path, timeout=TIMEOUT_SMALL):
    data = _api_get(session, remote_path, timeout=timeout)
    if data and data.get("type") == "file":
        content = data.get("content", "")
        if data.get("format") == "base64":
            return base64.b64decode(content).decode("utf-8", errors="replace")
        return content
    return None


def _download_binary(session, remote_path, timeout=TIMEOUT_LARGE):
    url = f"{REMOTE_BASE}/api/contents/{remote_path}"
    try:
        r = session.get(url, params={"format": "base64"}, timeout=timeout)
        if r.status_code == 200:
            return base64.b64decode(r.json().get("content", ""))
    except (requests.Timeout, requests.ConnectionError):
        pass
    return None


def sync(token, local_runs_dir):
    """
    БЫСТРАЯ синхронизация: скачивает только metrics.json для новых runs.
    Возвращается за секунды, не минуты.
    """
    global _last_sync, _sync_status

    now = time.time()
    if now - _last_sync < MIN_SYNC_INTERVAL and _sync_status.get("last_sync"):
        return _sync_status

    if not _sync_lock.acquire(blocking=False):
        return {**_sync_status, "note": "sync already in progress"}

    try:
        _sync_status["in_progress"] = True
        _sync_status["error"] = None

        session = _get_session(token)
        os.makedirs(local_runs_dir, exist_ok=True)

        # Получить список remote runs
        data = _api_get(session, REMOTE_RUNS_PATH, timeout=TIMEOUT_LIST)
        if not data or data.get("type") != "directory":
            _sync_status["error"] = "Cannot list remote runs"
            return _sync_status

        remote_runs = [item["name"] for item in data.get("content", [])
                       if item.get("type") == "directory"]

        # Какие runs уже есть локально?
        local_runs = set()
        if os.path.isdir(local_runs_dir):
            for d in os.listdir(local_runs_dir):
                if os.path.isfile(os.path.join(local_runs_dir, d, "metrics.json")):
                    local_runs.add(d)

        # Скачать metrics.json для новых runs
        new_synced = 0
        for run_name in remote_runs:
            if run_name in local_runs:
                continue

            # Скачать metrics.json
            content = _download_text(
                session,
                f"{REMOTE_RUNS_PATH}/{run_name}/metrics.json",
                timeout=TIMEOUT_SMALL)

            if content is not None:
                local_dir = os.path.join(local_runs_dir, run_name)
                os.makedirs(local_dir, exist_ok=True)
                with open(os.path.join(local_dir, "metrics.json"), "w") as f:
                    f.write(content)
                new_synced += 1
                local_runs.add(run_name)
                print(f"  Synced: {run_name}")

        _last_sync = time.time()
        _sync_status = {
            "last_sync": time.strftime("%Y-%m-%d %H:%M:%S"),
            "remote_runs": len(remote_runs),
            "local_runs": len(local_runs),
            "runs_synced": new_synced,
            "error": None,
            "in_progress": False,
        }

        # Запустить фоновую докачку extras
        if local_runs:
            _start_extras_sync(token, local_runs_dir, remote_runs, local_runs)

        return _sync_status

    except Exception as e:
        _sync_status["error"] = str(e)[:200]
        _sync_status["in_progress"] = False
        return _sync_status

    finally:
        _sync_lock.release()


def _start_extras_sync(token, local_runs_dir, remote_runs, local_runs):
    """Запустить фоновый поток для скачивания scores.csv и figures."""
    global _extras_running
    if _extras_running:
        return

    def _bg():
        global _extras_running
        _extras_running = True
        try:
            session = _get_session(token)
            for run_name in remote_runs:
                if run_name not in local_runs:
                    continue
                run_dir = os.path.join(local_runs_dir, run_name)

                # scores.csv
                scores_path = os.path.join(run_dir, "scores.csv")
                if not (os.path.isfile(scores_path) and os.path.getsize(scores_path) > 0):
                    content = _download_text(
                        session,
                        f"{REMOTE_RUNS_PATH}/{run_name}/scores.csv",
                        timeout=TIMEOUT_LARGE)
                    if content:
                        with open(scores_path, "w") as f:
                            f.write(content)
                        print(f"  [bg] scores.csv: {run_name}")

                # examples_manifest.json + thumbnails/
                manifest_path = os.path.join(run_dir, "examples_manifest.json")
                if not os.path.isfile(manifest_path):
                    content = _download_text(
                        session,
                        f"{REMOTE_RUNS_PATH}/{run_name}/examples_manifest.json",
                        timeout=TIMEOUT_SMALL)
                    if content:
                        with open(manifest_path, "w") as f:
                            f.write(content)
                        print(f"  [bg] examples_manifest.json: {run_name}")

                        # Скачать thumbnails
                        thumbs_dir = os.path.join(run_dir, "thumbnails")
                        os.makedirs(thumbs_dir, exist_ok=True)
                        listing = _api_get(session,
                                           f"{REMOTE_RUNS_PATH}/{run_name}/thumbnails",
                                           timeout=TIMEOUT_LIST)
                        if listing and listing.get("type") == "directory":
                            for item in listing.get("content", []):
                                if not item["name"].endswith(".jpg"):
                                    continue
                                thumb_local = os.path.join(thumbs_dir, item["name"])
                                if os.path.isfile(thumb_local):
                                    continue
                                binary = _download_binary(
                                    session,
                                    f"{REMOTE_RUNS_PATH}/{run_name}/thumbnails/{item['name']}",
                                    timeout=TIMEOUT_SMALL)
                                if binary:
                                    with open(thumb_local, "wb") as f:
                                        f.write(binary)
                            print(f"  [bg] thumbnails: {run_name}")

                # figures/
                fig_dir = os.path.join(run_dir, "figures")
                os.makedirs(fig_dir, exist_ok=True)
                has_figs = any(f.endswith(".png") for f in os.listdir(fig_dir))
                if not has_figs:
                    listing = _api_get(session,
                                       f"{REMOTE_RUNS_PATH}/{run_name}/figures",
                                       timeout=TIMEOUT_LIST)
                    if listing and listing.get("type") == "directory":
                        for item in listing.get("content", []):
                            if not item["name"].endswith(".png"):
                                continue
                            binary = _download_binary(
                                session,
                                f"{REMOTE_RUNS_PATH}/{run_name}/figures/{item['name']}")
                            if binary:
                                with open(os.path.join(fig_dir, item["name"]), "wb") as f:
                                    f.write(binary)
                                print(f"  [bg] figure: {run_name}/{item['name']}")
        except Exception as e:
            print(f"  [bg] extras error: {e}")
        finally:
            _extras_running = False

    threading.Thread(target=_bg, daemon=True).start()


def get_status():
    """Текущий статус синхронизации."""
    return {**_sync_status, "extras_in_progress": _extras_running}
