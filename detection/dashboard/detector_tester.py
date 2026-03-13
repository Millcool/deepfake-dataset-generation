"""
Smoke-тест внешнего детектора: последовательные проверки формата ответа.
"""

import json
import os
import requests

_TEST_VIDEOS_DIR = None
_MANIFEST = None


def init(test_videos_dir):
    """Загрузить manifest.json с тестовыми видео."""
    global _TEST_VIDEOS_DIR, _MANIFEST
    _TEST_VIDEOS_DIR = test_videos_dir
    manifest_path = os.path.join(test_videos_dir, "manifest.json")
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            _MANIFEST = json.load(f)
    else:
        _MANIFEST = {}


def _pick_test_video():
    """Выбрать первое доступное тестовое видео из манифеста."""
    if not _MANIFEST or not _TEST_VIDEOS_DIR:
        return None, None
    for filename, label in _MANIFEST.items():
        path = os.path.join(_TEST_VIDEOS_DIR, filename)
        if os.path.isfile(path):
            return path, label
    return None, None


def run_smoke_test(api_url):
    """
    Прогнать smoke-тест детектора по URL.
    Возвращает dict: {checks, all_passed, response_data, video_used, video_label}
    """
    checks = []
    response_data = None
    video_path, video_label = _pick_test_video()

    # Check 1: тестовое видео существует
    check1 = {"name": "Test video exists", "passed": False, "detail": ""}
    if video_path and os.path.isfile(video_path):
        check1["passed"] = True
        check1["detail"] = os.path.basename(video_path)
    else:
        check1["detail"] = "No test videos found in manifest"
        checks.append(check1)
        return _result(checks, response_data, video_path, video_label)
    checks.append(check1)

    # Check 2: HTTP-ответ получен
    check2 = {"name": "HTTP response received", "passed": False, "detail": ""}
    try:
        with open(video_path, "rb") as f:
            resp = requests.post(
                api_url,
                files={"file": (os.path.basename(video_path), f, "video/mp4")},
                timeout=120,
            )
        check2["passed"] = True
        check2["detail"] = f"Status {resp.status_code}"
    except requests.ConnectionError:
        check2["detail"] = f"Connection refused: {api_url}"
        checks.append(check2)
        return _result(checks, response_data, video_path, video_label)
    except requests.Timeout:
        check2["detail"] = "Request timed out (30s)"
        checks.append(check2)
        return _result(checks, response_data, video_path, video_label)
    except Exception as e:
        check2["detail"] = str(e)
        checks.append(check2)
        return _result(checks, response_data, video_path, video_label)
    checks.append(check2)

    # Check 3: HTTP 200 OK
    check3 = {"name": "HTTP 200 OK", "passed": False, "detail": ""}
    if resp.status_code == 200:
        check3["passed"] = True
        check3["detail"] = "OK"
    else:
        check3["detail"] = f"Got status {resp.status_code}: {resp.text[:200]}"
        checks.append(check3)
        return _result(checks, response_data, video_path, video_label)
    checks.append(check3)

    # Check 4: валидный JSON
    check4 = {"name": "Valid JSON response", "passed": False, "detail": ""}
    try:
        response_data = resp.json()
        check4["passed"] = True
        check4["detail"] = "Parsed OK"
    except (json.JSONDecodeError, ValueError) as e:
        check4["detail"] = f"Invalid JSON: {e}. Raw: {resp.text[:200]}"
        checks.append(check4)
        return _result(checks, response_data, video_path, video_label)
    checks.append(check4)

    # Check 5: поле score присутствует
    check5 = {"name": "Field 'score' present", "passed": False, "detail": ""}
    if "score" in response_data:
        check5["passed"] = True
        check5["detail"] = f"score = {response_data['score']}"
    else:
        check5["detail"] = f"Missing 'score'. Keys: {list(response_data.keys())}"
        checks.append(check5)
        return _result(checks, response_data, video_path, video_label)
    checks.append(check5)

    # Check 6: score — float в [0, 1]
    check6 = {"name": "Score is float in [0, 1]", "passed": False, "detail": ""}
    score = response_data["score"]
    try:
        score_f = float(score)
        if 0.0 <= score_f <= 1.0:
            check6["passed"] = True
            check6["detail"] = f"{score_f:.4f}"
        else:
            check6["detail"] = f"Score {score_f} is out of range [0, 1]"
    except (TypeError, ValueError):
        check6["detail"] = f"Cannot convert to float: {score!r}"
    checks.append(check6)

    return _result(checks, response_data, video_path, video_label)


def _result(checks, response_data, video_path, video_label):
    return {
        "checks": checks,
        "all_passed": all(c["passed"] for c in checks),
        "response_data": response_data,
        "video_used": os.path.basename(video_path) if video_path else None,
        "video_label": video_label,
    }
