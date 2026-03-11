#!/usr/bin/env python3
"""
Flask web dashboard для просмотра результатов детекции дипфейков.
Работает локально, синхронизирует данные с удалённого сервера MIEM.

Запуск:
  cd detection/dashboard && python app.py
  Или: bash detection/dashboard/run.sh

При каждом refresh — автоматическая синхронизация с сервером.
"""

import os
import sys
import json
import random
from flask import Flask, render_template, jsonify, request, send_file, abort

# Добавить текущую директорию в path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data_loader
import remote_sync
import catalog
import detector_registry
import detector_tester

app = Flask(__name__)

# Локальный кэш runs — рядом с проектом
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL_RUNS_DIR = os.path.join(PROJECT_ROOT, "detection_eval", "runs")

# Токен — из kod.txt или env
TOKEN = os.environ.get("MIEM_TOKEN", "")

def _load_token():
    """Загрузить токен из kod.txt если не задан через env."""
    global TOKEN
    if TOKEN:
        return TOKEN
    kod_path = os.path.join(PROJECT_ROOT, "kod.txt")
    if os.path.isfile(kod_path):
        with open(kod_path) as f:
            first_line = f.readline().strip()
        # Извлечь token= из URL
        if "token=" in first_line:
            TOKEN = first_line.split("token=")[-1].strip()
    return TOKEN


def _do_sync():
    """Синхронизировать с сервером (если есть токен)."""
    token = _load_token()
    if not token:
        return {"error": "No token found. Set MIEM_TOKEN or check kod.txt"}
    return remote_sync.sync(token, LOCAL_RUNS_DIR)


@app.before_request
def init_data_loader():
    """Инициализировать data_loader при первом запросе."""
    if data_loader.RUNS_DIR is None:
        os.makedirs(LOCAL_RUNS_DIR, exist_ok=True)
        data_loader.init(LOCAL_RUNS_DIR)
        dashboard_dir = os.path.dirname(os.path.abspath(__file__))
        detector_registry.init(dashboard_dir)
        test_videos_dir = os.path.join(dashboard_dir, "static", "test_videos")
        detector_tester.init(test_videos_dir)
        # Фоновая синхронизация — не блокирует первый запрос
        import threading
        def bg_sync():
            print("Background sync with remote server...")
            result = _do_sync()
            print(f"  Sync result: {result}")
            data_loader.invalidate_cache()
        threading.Thread(target=bg_sync, daemon=True).start()


# ── Страницы ──────────────────────────────────────────────────────


@app.route("/")
def index():
    """Главная: таблица прогонов с фильтрами."""
    runs = data_loader.scan_runs()
    datasets = data_loader.get_unique_datasets()
    detectors = data_loader.get_unique_detectors()
    sync_status = remote_sync.get_status()
    return render_template(
        "index.html",
        runs=runs,
        datasets=datasets,
        detectors=detectors,
        sync_status=sync_status,
    )


@app.route("/run/<run_id>")
def run_detail(run_id):
    """Детальная страница одного прогона."""
    metrics = data_loader.get_run(run_id)
    if not metrics:
        abort(404)
    figures = data_loader.list_figures(run_id)
    examples = data_loader.get_examples(run_id)
    scores_array = data_loader.get_scores_array(run_id)
    return render_template(
        "run_detail.html",
        run_id=run_id,
        metrics=metrics,
        figures=figures,
        examples=examples,
        scores_array=scores_array,
    )


@app.route("/rankings")
def rankings():
    """Агрегированные рейтинги детекторов и датасетов."""
    by_detector = data_loader.aggregate_by_detector()
    by_dataset = data_loader.aggregate_by_dataset()
    all_runs = data_loader.scan_runs()
    return render_template("rankings.html",
                           by_detector=by_detector,
                           by_dataset=by_dataset,
                           detector_catalog=catalog.DETECTORS,
                           algorithm_catalog=catalog.ALGORITHMS,
                           all_runs_json=json.dumps(all_runs),
                           detector_catalog_json=json.dumps(catalog.DETECTORS),
                           algorithm_catalog_json=json.dumps(catalog.ALGORITHMS))


@app.route("/compare")
def compare():
    """Сравнение нескольких прогонов."""
    run_ids = request.args.get("runs", "").split(",")
    run_ids = [r.strip() for r in run_ids if r.strip()]

    runs_data = []
    for rid in run_ids:
        m = data_loader.get_run(rid)
        if m:
            runs_data.append(m)

    # Автодетект режима
    datasets = set(r.get("dataset", "") for r in runs_data)
    detectors = set(r.get("detector", "") for r in runs_data)
    if len(datasets) == 1:
        mode = "same_dataset"
    elif len(detectors) == 1:
        mode = "same_detector"
    else:
        mode = "mixed"

    return render_template(
        "compare.html",
        run_ids=run_ids,
        runs_data=runs_data,
        mode=mode,
    )


@app.route("/register")
def register_detector_page():
    """Страница регистрации нового детектора."""
    return render_template("register.html")


@app.route("/detectors")
def detectors_list():
    """Список зарегистрированных детекторов."""
    detectors = detector_registry.list_detectors()
    return render_template("detectors.html", detectors=detectors)


# ── API endpoints ─────────────────────────────────────────────────


@app.route("/api/runs")
def api_runs():
    """JSON всех прогонов."""
    runs = data_loader.scan_runs()
    return jsonify(runs)


@app.route("/api/run/<run_id>/metrics")
def api_run_metrics(run_id):
    """Полный metrics.json."""
    metrics = data_loader.get_run(run_id)
    if not metrics:
        abort(404)
    return jsonify(metrics)


@app.route("/api/run/<run_id>/roc")
def api_run_roc(run_id):
    """ROC данные: {fpr, tpr, auc}."""
    roc = data_loader.compute_roc_data(run_id)
    if not roc:
        abort(404)
    return jsonify(roc)


@app.route("/api/run/<run_id>/figures/<name>")
def api_run_figure(run_id, name):
    """PNG файл из figures/."""
    if not name.endswith(".png"):
        abort(400)
    if ".." in name or "/" in name:
        abort(400)

    fig_path = os.path.join(LOCAL_RUNS_DIR, run_id, "figures", name)
    if not os.path.isfile(fig_path):
        abort(404)
    return send_file(fig_path, mimetype="image/png")


@app.route("/api/run/<run_id>/thumbnails/<filename>")
def api_run_thumbnail(run_id, filename):
    """JPEG thumbnail из thumbnails/."""
    if not filename.endswith(".jpg"):
        abort(400)
    if ".." in filename or "/" in filename:
        abort(400)

    thumb_path = os.path.join(LOCAL_RUNS_DIR, run_id, "thumbnails", filename)
    if not os.path.isfile(thumb_path):
        abort(404)
    return send_file(thumb_path, mimetype="image/jpeg")


@app.route("/api/compare")
def api_compare():
    """Метрики нескольких прогонов."""
    run_ids = request.args.get("runs", "").split(",")
    run_ids = [r.strip() for r in run_ids if r.strip()]

    results = []
    for rid in run_ids:
        m = data_loader.get_run(rid)
        if m:
            results.append({
                "run_id": rid,
                "detector": m.get("detector", ""),
                "dataset": m.get("dataset", ""),
                "metrics": m.get("metrics", {}),
                "total_videos": m.get("total_videos", 0),
                "threshold": m.get("threshold", 0),
            })
    return jsonify(results)


@app.route("/api/video-analysis")
def api_video_analysis():
    """Кросс-прогонный анализ видео (lazy load)."""
    analysis = data_loader.compute_video_analysis()
    if not analysis:
        abort(404)
    return jsonify(analysis)


@app.route("/api/sync")
def api_sync():
    """Синхронизировать с сервером и сбросить кэш."""
    result = _do_sync()
    data_loader.invalidate_cache()
    return jsonify(result)


@app.route("/api/sync/status")
def api_sync_status():
    """Статус последней синхронизации."""
    return jsonify(remote_sync.get_status())


# ── Detector Registry API ─────────────────────────────────────────


@app.route("/api/detectors", methods=["GET"])
def api_detectors_list():
    """JSON список зарегистрированных детекторов."""
    return jsonify(detector_registry.list_detectors())


@app.route("/api/detectors", methods=["POST"])
def api_detectors_register():
    """Зарегистрировать новый детектор."""
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    api_url = (data.get("api_url") or "").strip()
    if not name or not api_url:
        return jsonify({"error": "Fields 'name' and 'api_url' are required"}), 400
    entry = detector_registry.register_detector(
        name=name,
        api_url=api_url,
        description=data.get("description", ""),
        author=data.get("author", ""),
        paper_url=data.get("paper_url", ""),
        github_url=data.get("github_url", ""),
    )
    return jsonify(entry), 201


@app.route("/api/detectors/<detector_id>/test", methods=["POST"])
def api_detectors_test(detector_id):
    """Smoke-тест детектора."""
    det = detector_registry.get_detector(detector_id)
    if not det:
        return jsonify({"error": "Detector not found"}), 404
    result = detector_tester.run_smoke_test(det["api_url"])
    detector_registry.update_test_result(detector_id, result["all_passed"], result)
    return jsonify(result)


@app.route("/api/detectors/<detector_id>", methods=["DELETE"])
def api_detectors_delete(detector_id):
    """Удалить детектор."""
    det = detector_registry.get_detector(detector_id)
    if not det:
        return jsonify({"error": "Detector not found"}), 404
    detector_registry.delete_detector(detector_id)
    return jsonify({"ok": True})


@app.route("/api/mock-detector", methods=["POST"])
def api_mock_detector():
    """Reference mock-детектор: принимает видеофайл, возвращает random score."""
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file uploaded"}), 400
    score = round(random.uniform(0.3, 0.95), 4)
    return jsonify({
        "score": score,
        "label": "fake" if score > 0.5 else "real",
        "confidence": score,
        "metadata": {"model": "mock-detector", "version": "1.0"},
    })


if __name__ == "__main__":
    print(f"Local runs directory: {LOCAL_RUNS_DIR}")
    print(f"Starting dashboard on http://localhost:5050")
    app.run(host="127.0.0.1", port=5050, debug=True)
