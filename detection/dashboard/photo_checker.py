"""
Photo deepfake checker: upload image to MIEM, run 6 detectors, return results.

Architecture:
  1. Upload image + worker scripts to MIEM via Jupyter Contents API
  2. Run each detector as a separate Jupyter WebSocket execution
  3. Update DB progressively as each detector completes
  4. Cleanup temp files on MIEM
"""

import base64
import json
import os
import ssl
import threading
import time
import uuid as uuid_mod
from datetime import datetime

import requests
import websocket

# Remote server config
REMOTE_BASE = "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru"
UPLOAD_DIR = "photo_uploads"
WORKERS_DIR = "photo_check_workers"

# Global lock: only one photo check at a time on MIEM
_miem_lock = threading.Lock()

# Detector definitions
DETECTORS = [
    # (name, venv_relative_path, needs_face, vram_mb_needed)
    ("npr", "NPR-DeepfakeDetection/.venv", False, 1500),
    ("clip_dfdet", "deepfake-detection/.venv", False, 2000),
    ("genconvit", "CViT/.venv", True, 4000),
    ("sbi", "SelfBlendedImages/.venv", True, 3000),
    ("laanet", "LAA-Net/.venv", True, 10000),
]

WORKER_NAMES = ["face_detect"] + [d[0] for d in DETECTORS]


def start_photo_check(check_id, app):
    """Launch a background thread for photo check."""
    cancel_event = threading.Event()
    t = threading.Thread(
        target=_run_photo_check,
        args=(check_id, cancel_event, app),
        daemon=True,
    )
    t.start()
    return True


# ─── Jupyter API helpers ────────────────────────────────────────

def _get_session(token):
    for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
        os.environ.pop(k, None)
    s = requests.Session()
    s.trust_env = False
    s.headers["Authorization"] = f"token {token}"
    return s


def _upload_file_to_miem(session, remote_path, content_bytes, is_text=False):
    url = f"{REMOTE_BASE}/api/contents/{remote_path}"
    if is_text:
        payload = {
            "type": "file", "format": "text",
            "content": content_bytes.decode("utf-8") if isinstance(content_bytes, bytes) else content_bytes,
        }
    else:
        payload = {
            "type": "file", "format": "base64",
            "content": base64.b64encode(content_bytes).decode(),
        }
    r = session.put(url, json=payload, timeout=60)
    return r.status_code in (200, 201)


def _delete_file_on_miem(session, remote_path):
    url = f"{REMOTE_BASE}/api/contents/{remote_path}"
    try:
        session.delete(url, timeout=10)
    except Exception:
        pass


def _ensure_dir_on_miem(session, remote_dir):
    url = f"{REMOTE_BASE}/api/contents/{remote_dir}"
    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            return True
    except Exception:
        pass
    try:
        r = session.put(url, json={"type": "directory"}, timeout=10)
        return r.status_code in (200, 201)
    except Exception:
        return False


def _read_worker_file(name):
    workers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photo_workers")
    path = os.path.join(workers_dir, f"{name}.py")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _upload_workers_to_miem(session, check_uuid):
    _ensure_dir_on_miem(session, WORKERS_DIR)
    for name in WORKER_NAMES:
        code = _read_worker_file(name)
        remote_path = f"{WORKERS_DIR}/{name}_{check_uuid}.py"
        if not _upload_file_to_miem(session, remote_path, code, is_text=True):
            return False
    return True


def _cleanup_workers_on_miem(session, check_uuid):
    for name in WORKER_NAMES:
        _delete_file_on_miem(session, f"{WORKERS_DIR}/{name}_{check_uuid}.py")


# ─── Single-command Jupyter execution ───────────────────────────

def _execute_on_miem(token, code, timeout=120):
    """Execute Python code on MIEM via Jupyter WebSocket.
    Returns (success, output_lines, error_msg).
    Each call creates a fresh kernel session (no state leaking).
    """
    for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"]:
        os.environ.pop(k, None)

    s = requests.Session()
    s.trust_env = False
    headers = {"Authorization": f"token {token}"}

    session_name = f"photo_{uuid_mod.uuid4().hex[:8]}.ipynb"
    payload = {
        "kernel": {"name": "python3"},
        "name": session_name,
        "path": session_name,
        "type": "notebook",
    }
    r = s.post(f"{REMOTE_BASE}/api/sessions", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    session_data = r.json()
    kernel_id = session_data["kernel"]["id"]
    session_id = session_data["id"]

    output_lines = []
    error_msg = None

    try:
        ws_url = (
            f"wss://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru/api/kernels/"
            f"{kernel_id}/channels?token={token}"
        )
        ws = websocket.create_connection(
            ws_url,
            sslopt={"cert_reqs": ssl.CERT_NONE},
            timeout=timeout,
            http_proxy_host=None,
            http_proxy_port=None,
            header=[f"Authorization: token {token}"],
            origin="https://ws.miem3.vmnet.top",
        )

        msg_id = str(uuid_mod.uuid4())
        req = {
            "header": {
                "msg_id": msg_id, "msg_type": "execute_request",
                "username": "", "session": str(uuid_mod.uuid4()), "version": "5.3",
            },
            "parent_header": {}, "metadata": {},
            "content": {
                "code": code, "silent": False, "store_history": True,
                "user_expressions": {}, "allow_stdin": False, "stop_on_error": True,
            },
            "buffers": [], "channel": "shell",
        }
        ws.send(json.dumps(req))

        while True:
            opcode, data = ws.recv_data()
            if opcode == websocket.ABNF.OPCODE_TEXT:
                msg = json.loads(data.decode("utf-8"))
            else:
                text = data.decode("utf-8", errors="ignore")
                idx = text.find("{")
                if idx < 0:
                    continue
                msg = json.loads(text[idx:])

            if msg.get("parent_header", {}).get("msg_id") != msg_id:
                continue

            msg_type = msg.get("msg_type")
            if msg_type == "stream":
                text = msg.get("content", {}).get("text", "")
                output_lines.extend(text.strip().split("\n"))
            elif msg_type == "error":
                content = msg.get("content", {})
                error_msg = f"{content.get('ename')}: {content.get('evalue')}"
            elif msg_type == "execute_reply":
                break

        ws.close()
    except websocket.WebSocketTimeoutException:
        error_msg = "WebSocket timeout"
    except Exception as e:
        error_msg = str(e)[:300]
    finally:
        try:
            s.delete(f"{REMOTE_BASE}/api/sessions/{session_id}", headers=headers, timeout=10)
        except Exception:
            pass

    return error_msg is None, output_lines, error_msg


# ─── GPU discovery (runs on MIEM) ──────────────────────────────

_GPU_SCAN_CODE = '''
import subprocess, json
r = subprocess.run(
    ["nvidia-smi", "--query-gpu=index,memory.used,memory.total",
     "--format=csv,noheader,nounits"],
    capture_output=True, text=True, timeout=10)
gpus = []
for line in r.stdout.strip().split("\\n"):
    parts = [x.strip() for x in line.split(",")]
    if len(parts) == 3:
        idx, used, total = int(parts[0]), int(parts[1]), int(parts[2])
        gpus.append({"index": idx, "used": used, "total": total, "free": total - used})
print("GPU_INFO:" + json.dumps(gpus))
'''


def _find_free_gpu(token, min_free_mb=1500):
    """Query MIEM for free GPUs. Returns (gpu_index, free_mb) or (None, 0)."""
    ok, lines, err = _execute_on_miem(token, _GPU_SCAN_CODE, timeout=30)
    for line in lines:
        if line.startswith("GPU_INFO:"):
            gpus = json.loads(line[len("GPU_INFO:"):])
            candidates = [(g["index"], g["free"]) for g in gpus if g["free"] >= min_free_mb]
            candidates.sort(key=lambda x: -x[1])
            if candidates:
                return candidates[0]
    return None, 0


# ─── Single detector execution ─────────────────────────────────

def _build_detector_code(check_uuid, detector_name, venv_rel, image_arg, gpu_index):
    """Build code to run a single detector subprocess on MIEM."""
    return f'''
import subprocess, os, json, time
HOME = os.path.expanduser("~")
env = dict(os.environ)
env["CUDA_VISIBLE_DEVICES"] = "{gpu_index}"
worker = os.path.join(HOME, "{WORKERS_DIR}/{detector_name}_{check_uuid}.py")
venv_python = os.path.join(HOME, "{venv_rel}/bin/python")
t0 = time.time()
try:
    proc = subprocess.run(
        [venv_python, worker, "{image_arg}"],
        capture_output=True, text=True, timeout=120, env=env)
    for line in proc.stdout.split("\\n"):
        if line.startswith("PHOTO_RESULT:"):
            print(line, flush=True)
            break
    else:
        err_tail = proc.stderr[-300:] if proc.stderr else "no output"
        print("PHOTO_RESULT:" + json.dumps({{
            "detector": "{detector_name}", "score": None, "label": None,
            "time": round(time.time() - t0, 2),
            "error": f"No result. RC={{proc.returncode}}. stderr: {{err_tail}}"
        }}), flush=True)
except subprocess.TimeoutExpired:
    print("PHOTO_RESULT:" + json.dumps({{
        "detector": "{detector_name}", "score": None, "label": None,
        "time": round(time.time() - t0, 2), "error": "Timeout (120s)"
    }}), flush=True)
except Exception as e:
    print("PHOTO_RESULT:" + json.dumps({{
        "detector": "{detector_name}", "score": None, "label": None,
        "time": round(time.time() - t0, 2), "error": str(e)[:200]
    }}), flush=True)
'''


def _build_face_detect_code(check_uuid, image_path, face_path, gpu_index):
    """Build code to run face detection on MIEM."""
    return f'''
import subprocess, os, json
HOME = os.path.expanduser("~")
env = dict(os.environ)
env["CUDA_VISIBLE_DEVICES"] = "{gpu_index}"
worker = os.path.join(HOME, "{WORKERS_DIR}/face_detect_{check_uuid}.py")
venv_python = os.path.join(HOME, "SelfBlendedImages/.venv/bin/python")
try:
    proc = subprocess.run(
        [venv_python, worker, "{image_path}", "{face_path}"],
        capture_output=True, text=True, timeout=120, env=env)
    for line in proc.stdout.split("\\n"):
        if line.startswith("FACE_RESULT:"):
            print(line, flush=True)
            break
    else:
        print("FACE_RESULT:" + json.dumps({{"detected": False, "error": "No output"}}), flush=True)
except subprocess.TimeoutExpired:
    print("FACE_RESULT:" + json.dumps({{"detected": False, "error": "Timeout"}}), flush=True)
except Exception as e:
    print("FACE_RESULT:" + json.dumps({{"detected": False, "error": str(e)[:200]}}), flush=True)
'''


# ─── Main pipeline ──────────────────────────────────────────────

def _run_photo_check(check_id, cancel_event, app):
    with app.app_context():
        from models import db, PhotoCheck

        check = PhotoCheck.query.get(check_id)
        if not check:
            return

        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(dashboard_dir))

        token = os.environ.get("MIEM_TOKEN", "")
        if not token:
            kod_path = os.path.join(project_root, "kod.txt")
            if os.path.isfile(kod_path):
                with open(kod_path) as f:
                    first_line = f.readline().strip()
                if "token=" in first_line:
                    token = first_line.split("token=")[-1].strip()

        if not token:
            check.status = "failed"
            check.error_message = "MIEM token not configured"
            db.session.commit()
            return

        if not _miem_lock.acquire(timeout=10):
            check.status = "failed"
            check.error_message = "Server busy with another check. Try again later."
            db.session.commit()
            return

        try:
            _do_photo_check(check, token, cancel_event, db)
        except Exception as e:
            check.status = "failed"
            check.error_message = f"Unexpected error: {str(e)[:300]}"
            db.session.commit()
        finally:
            _miem_lock.release()


def _do_photo_check(check, token, cancel_event, db):
    check_uuid = check.uuid
    home_remote = "/var/lib/ilanmironov@edu.hse.ru"

    # Read local image
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photo_uploads")
    local_image_path = os.path.join(uploads_dir, f"{check_uuid}_{check.filename}")
    if not os.path.isfile(local_image_path):
        check.status = "failed"
        check.error_message = "Uploaded image not found on server"
        db.session.commit()
        return

    with open(local_image_path, "rb") as f:
        image_bytes = f.read()

    ext = os.path.splitext(check.filename)[1] or ".png"
    session = _get_session(token)

    # Step 1: Upload image
    check.status = "uploading"
    check.current_step = "Uploading image..."
    db.session.commit()

    _ensure_dir_on_miem(session, UPLOAD_DIR)
    remote_image_path = f"{UPLOAD_DIR}/{check_uuid}{ext}"
    if not _upload_file_to_miem(session, remote_image_path, image_bytes):
        check.status = "failed"
        check.error_message = "Failed to upload image to MIEM"
        db.session.commit()
        return

    # Step 2: Upload workers
    check.current_step = "Uploading analysis scripts..."
    db.session.commit()

    if not _upload_workers_to_miem(session, check_uuid):
        check.status = "failed"
        check.error_message = "Failed to upload scripts to MIEM"
        db.session.commit()
        _cleanup_miem(session, check_uuid, ext)
        return

    if cancel_event.is_set():
        _full_cleanup(session, check_uuid, ext)
        check.status = "failed"
        check.error_message = "Cancelled"
        db.session.commit()
        return

    # Step 3: Find free GPU
    check.status = "running"
    check.current_step = "Checking GPU availability..."
    db.session.commit()

    gpu_index, gpu_free = _find_free_gpu(token, min_free_mb=1500)
    if gpu_index is None:
        check.status = "failed"
        check.error_message = "No free GPU available on MIEM server"
        db.session.commit()
        _full_cleanup(session, check_uuid, ext)
        return

    image_full_path = f"{home_remote}/{remote_image_path}"
    face_path = f"/tmp/photo_face_{check_uuid}.png"

    # Step 4: Face detection
    check.current_step = "Detecting face..."
    db.session.commit()

    face_code = _build_face_detect_code(check_uuid, image_full_path, face_path, gpu_index)
    ok, lines, err = _execute_on_miem(token, face_code, timeout=120)
    face_detected = False
    for line in lines:
        if line.startswith("FACE_RESULT:"):
            face_info = json.loads(line[len("FACE_RESULT:"):])
            face_detected = face_info.get("detected", False)
            break

    # Step 5: Run detectors one by one
    results = {}
    done_count = 0
    total_detectors = len(DETECTORS) + 1  # +1 for altfreezing (N/A)

    for det_name, venv_rel, needs_face, vram_needed in DETECTORS:
        if cancel_event.is_set():
            break

        done_count += 1
        check.current_step = f"Running {det_name} ({done_count}/{len(DETECTORS)})..."
        check.detectors_done = done_count - 1
        db.session.commit()

        # Skip if needs face but none detected
        if needs_face and not face_detected:
            results[det_name] = {
                "detector": det_name, "score": None, "label": None,
                "time": 0, "error": "No face detected",
            }
            continue

        # Re-check GPU for heavy detectors
        if vram_needed > 5000:
            gpu_index_new, gpu_free_new = _find_free_gpu(token, min_free_mb=vram_needed)
            if gpu_index_new is None:
                results[det_name] = {
                    "detector": det_name, "score": None, "label": None,
                    "time": 0, "error": f"Not enough free VRAM (need {vram_needed} MB)",
                }
                continue
            gpu_index = gpu_index_new

        # Choose input image
        img_arg = face_path if needs_face else image_full_path
        det_code = _build_detector_code(check_uuid, det_name, venv_rel, img_arg, gpu_index)

        ok, lines, err = _execute_on_miem(token, det_code, timeout=180)

        result = None
        for line in lines:
            if line.startswith("PHOTO_RESULT:"):
                try:
                    result = json.loads(line[len("PHOTO_RESULT:"):])
                except json.JSONDecodeError:
                    pass
                break

        if result:
            results[det_name] = result
        elif err:
            results[det_name] = {
                "detector": det_name, "score": None, "label": None,
                "time": 0, "error": err[:200],
            }
        else:
            results[det_name] = {
                "detector": det_name, "score": None, "label": None,
                "time": 0, "error": "No result received",
            }

    # AltFreezing: N/A for photos
    results["altfreezing"] = {
        "detector": "altfreezing", "score": None, "label": None,
        "time": 0, "error": "Requires video input (3D temporal model)",
    }

    # Compute consensus
    active_scores = [r["score"] for r in results.values() if r["score"] is not None]
    active_labels = [r["label"] for r in results.values() if r["label"] is not None]
    fake_count = sum(1 for l in active_labels if l == "fake")
    real_count = sum(1 for l in active_labels if l == "real")
    error_count = sum(1 for r in results.values() if r.get("error"))

    if active_scores:
        mean_score = sum(active_scores) / len(active_scores)
        if fake_count > real_count:
            verdict = "fake"
        elif real_count > fake_count:
            verdict = "real"
        else:
            verdict = "fake" if mean_score >= 0.5 else "real"
        total_active = fake_count + real_count
        ratio = max(fake_count, real_count) / total_active if total_active > 0 else 0
        confidence = "high" if ratio >= 0.8 else ("medium" if ratio >= 0.6 else "low")
    else:
        mean_score = None
        verdict = "unknown"
        confidence = "low"

    final_result = {
        "detectors": results,
        "consensus": {
            "fake_count": fake_count, "real_count": real_count, "error_count": error_count,
            "mean_score": round(mean_score, 6) if mean_score is not None else None,
            "verdict": verdict, "confidence": confidence,
        },
        "face_detected": face_detected,
    }

    check.status = "completed"
    check.set_results(final_result)
    check.completed_at = datetime.utcnow()
    check.detectors_done = sum(1 for d in results.values() if d.get("score") is not None)
    check.detectors_total = len(results)
    check.current_step = ""
    db.session.commit()

    # Cleanup
    _full_cleanup(session, check_uuid, ext)

    # Cleanup face crop on MIEM
    cleanup_code = f'import os\ntry:\n    os.remove("{face_path}")\nexcept: pass\nprint("OK")'
    _execute_on_miem(token, cleanup_code, timeout=15)


def _cleanup_miem(session, check_uuid, ext):
    _delete_file_on_miem(session, f"{UPLOAD_DIR}/{check_uuid}{ext}")


def _full_cleanup(session, check_uuid, ext):
    _cleanup_miem(session, check_uuid, ext)
    _cleanup_workers_on_miem(session, check_uuid)
