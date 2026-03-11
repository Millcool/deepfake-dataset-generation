"""
CRUD для реестра зарегистрированных внешних детекторов.
Хранение: registered_detectors.json рядом с дашбордом.
"""

import json
import os
import uuid
from datetime import datetime

_JSON_PATH = None


def init(dashboard_dir):
    """Задать путь к JSON-файлу реестра."""
    global _JSON_PATH
    _JSON_PATH = os.path.join(dashboard_dir, "registered_detectors.json")


def _load():
    if not _JSON_PATH or not os.path.isfile(_JSON_PATH):
        return []
    with open(_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(detectors):
    with open(_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(detectors, f, indent=2, ensure_ascii=False)


def list_detectors():
    """Список всех зарегистрированных детекторов."""
    return _load()


def get_detector(detector_id):
    """Получить детектор по ID."""
    for d in _load():
        if d["id"] == detector_id:
            return d
    return None


def register_detector(name, api_url, description="", author="", paper_url="", github_url=""):
    """Зарегистрировать новый детектор. Возвращает созданную запись."""
    detectors = _load()
    entry = {
        "id": str(uuid.uuid4()),
        "name": name,
        "api_url": api_url,
        "description": description,
        "author": author,
        "paper_url": paper_url,
        "github_url": github_url,
        "status": "pending",
        "registered_at": datetime.now().isoformat(),
        "last_test": None,
        "test_details": None,
    }
    detectors.append(entry)
    _save(detectors)
    return entry


def update_test_result(detector_id, success, details):
    """Обновить результат smoke-теста."""
    detectors = _load()
    for d in detectors:
        if d["id"] == detector_id:
            d["status"] = "verified" if success else "error"
            d["last_test"] = datetime.now().isoformat()
            d["test_details"] = details
            break
    _save(detectors)


def delete_detector(detector_id):
    """Удалить детектор по ID."""
    detectors = _load()
    detectors = [d for d in detectors if d["id"] != detector_id]
    _save(detectors)
