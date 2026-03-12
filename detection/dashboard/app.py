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
from datetime import datetime

from flask import Flask, render_template, jsonify, request, send_file, abort, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user

# Добавить текущую директорию в path для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data_loader
import remote_sync
import catalog
import detector_registry
import detector_tester
import evaluation_runner
from models import db, User, Detector, TestSet, Evaluation, EvaluationScore
from auth import login_manager, admin_required

app = Flask(__name__)

# Secret key for sessions
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Database
DATABASE_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.db"),
)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"check_same_thread": False},
}

# Init extensions
db.init_app(app)
login_manager.init_app(app)

# Локальный кэш runs — рядом с проектом
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCAL_RUNS_DIR = os.environ.get("RUNS_DIR", os.path.join(PROJECT_ROOT, "detection_eval", "runs"))

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


def _create_default_admin():
    """Create default admin user if none exists."""
    if not User.query.filter_by(username="dfadmin").first():
        admin = User(username="dfadmin", role="admin")
        admin.set_password("Df$detect!2026_adm")
        db.session.add(admin)
        db.session.commit()


# Create tables and default admin on first startup
with app.app_context():
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    try:
        db.create_all()
    except Exception:
        pass  # Tables already exist (e.g. persistent volume)
    _create_default_admin()


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


# ── Auth routes ────────────────────────────────────────────────


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        error = "Неверный логин или пароль"
    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(username) < 3:
            error = "Логин должен содержать минимум 3 символа"
        elif len(password) < 8:
            error = "Пароль должен содержать минимум 8 символов"
        elif password != confirm:
            error = "Пароли не совпадают"
        elif User.query.filter_by(username=username).first():
            error = "Пользователь с таким логином уже существует"
        else:
            user = User(username=username, role="user")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("user_dashboard"))
    return render_template("signup.html", error=error)


# ── Existing pages (now with @login_required) ─────────────────


@app.route("/")
@login_required
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
@login_required
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
@login_required
def rankings():
    """Агрегированные рейтинги детекторов и датасетов."""
    by_detector = data_loader.aggregate_by_detector()
    by_dataset = data_loader.aggregate_by_dataset()
    all_runs = data_loader.scan_runs()

    # Merge published user evaluations into rankings
    published_runs = _get_published_runs()
    all_runs_with_user = all_runs + published_runs

    return render_template("rankings.html",
                           by_detector=by_detector,
                           by_dataset=by_dataset,
                           detector_catalog=catalog.DETECTORS,
                           algorithm_catalog=catalog.ALGORITHMS,
                           all_runs_json=json.dumps(all_runs_with_user),
                           detector_catalog_json=json.dumps(catalog.DETECTORS),
                           algorithm_catalog_json=json.dumps(catalog.ALGORITHMS),
                           published_runs=published_runs)


@app.route("/detector/<detector_key>")
@login_required
def detector_detail(detector_key):
    """Страница детектора: описание + все прогоны."""
    info = catalog.DETECTORS.get(detector_key)
    runs = data_loader.scan_runs()
    det_runs = sorted([r for r in runs if r["detector"] == detector_key],
                      key=lambda r: -(r["auc"] or 0))
    if not info and not det_runs:
        abort(404)
    return render_template("detector_detail.html",
                           key=detector_key, info=info, runs=det_runs,
                           runs_json=json.dumps(det_runs),
                           algorithm_catalog_json=json.dumps(catalog.ALGORITHMS))


@app.route("/dataset/<dataset_key>")
@login_required
def dataset_detail(dataset_key):
    """Страница датасета: описание + все прогоны."""
    info = catalog.ALGORITHMS.get(dataset_key)
    runs = data_loader.scan_runs()
    ds_runs = sorted([r for r in runs if r["dataset"] == dataset_key],
                     key=lambda r: -(r["auc"] or 0))
    if not info and not ds_runs:
        abort(404)
    return render_template("dataset_detail.html",
                           key=dataset_key, info=info, runs=ds_runs,
                           runs_json=json.dumps(ds_runs),
                           detector_catalog_json=json.dumps(catalog.DETECTORS))


@app.route("/compare")
@login_required
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
@login_required
def register_detector_page():
    """Страница регистрации нового детектора."""
    return render_template("register.html")


@app.route("/detectors")
@login_required
def detectors_list():
    """Список зарегистрированных детекторов."""
    if current_user.is_admin:
        user_detectors = Detector.query.all()
    else:
        user_detectors = Detector.query.filter_by(user_id=current_user.id).all()
    return render_template("detectors.html", detectors=user_detectors)


# ── User Dashboard ────────────────────────────────────────────


@app.route("/dashboard")
@login_required
def user_dashboard():
    """Личный кабинет пользователя."""
    detectors = Detector.query.filter_by(user_id=current_user.id).all()
    evaluations = Evaluation.query.filter_by(user_id=current_user.id)\
        .order_by(Evaluation.id.desc()).all()
    test_sets = TestSet.query.filter_by(is_archived=0).all()
    return render_template(
        "user_dashboard.html",
        detectors=detectors,
        evaluations=evaluations,
        test_sets=test_sets,
    )


@app.route("/evaluation/<int:eval_id>")
@login_required
def evaluation_detail(eval_id):
    """Детальная страница прогона."""
    ev = Evaluation.query.get_or_404(eval_id)
    if ev.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    recent_scores = EvaluationScore.query.filter_by(evaluation_id=eval_id)\
        .order_by(EvaluationScore.id.desc()).limit(50).all()
    recent_scores.reverse()
    return render_template(
        "evaluation_detail.html",
        evaluation=ev,
        recent_scores=recent_scores,
    )


# ── Admin: Test Sets ──────────────────────────────────────────


@app.route("/admin/test-sets")
@login_required
@admin_required
def admin_test_sets():
    """Управление тестовыми наборами (admin only)."""
    test_sets = TestSet.query.order_by(TestSet.id.desc()).all()
    # Gather unique years from algorithms catalog
    years = sorted(set(v.get("year") for v in catalog.ALGORITHMS.values() if v.get("year")))
    return render_template(
        "admin_test_sets.html",
        test_sets=test_sets,
        algorithms=catalog.ALGORITHMS,
        years=years,
    )


# ── API endpoints (existing, now with @login_required) ────────


@app.route("/api/runs")
@login_required
def api_runs():
    """JSON всех прогонов."""
    runs = data_loader.scan_runs()
    return jsonify(runs)


@app.route("/api/run/<run_id>/metrics")
@login_required
def api_run_metrics(run_id):
    """Полный metrics.json."""
    metrics = data_loader.get_run(run_id)
    if not metrics:
        abort(404)
    return jsonify(metrics)


@app.route("/api/run/<run_id>/roc")
@login_required
def api_run_roc(run_id):
    """ROC данные: {fpr, tpr, auc}."""
    roc = data_loader.compute_roc_data(run_id)
    if not roc:
        abort(404)
    return jsonify(roc)


@app.route("/api/run/<run_id>/figures/<name>")
@login_required
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
@login_required
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
@login_required
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
@login_required
def api_video_analysis():
    """Кросс-прогонный анализ видео (lazy load)."""
    analysis = data_loader.compute_video_analysis()
    if not analysis:
        abort(404)
    return jsonify(analysis)


@app.route("/api/sync")
@login_required
@admin_required
def api_sync():
    """Синхронизировать с сервером и сбросить кэш (admin only)."""
    result = _do_sync()
    data_loader.invalidate_cache()
    return jsonify(result)


@app.route("/api/sync/status")
@login_required
def api_sync_status():
    """Статус последней синхронизации."""
    return jsonify(remote_sync.get_status())


# ── User Detectors API ───────────────────────────────────────


@app.route("/api/user/detectors", methods=["GET"])
@login_required
def api_user_detectors_list():
    """List current user's detectors."""
    detectors = Detector.query.filter_by(user_id=current_user.id).all()
    return jsonify([d.to_dict() for d in detectors])


@app.route("/api/user/detectors", methods=["POST"])
@login_required
def api_user_detectors_create():
    """Register a new detector for current user."""
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    api_url = (data.get("api_url") or "").strip()
    if not name or not api_url:
        return jsonify({"error": "Fields 'name' and 'api_url' are required"}), 400

    det = Detector(
        user_id=current_user.id,
        name=name,
        api_url=api_url,
        description=data.get("description", ""),
        author=data.get("author", ""),
        paper_url=data.get("paper_url", ""),
        github_url=data.get("github_url", ""),
    )
    db.session.add(det)
    db.session.commit()
    return jsonify(det.to_dict()), 201


@app.route("/api/user/detectors/<int:det_id>/test", methods=["POST"])
@login_required
def api_user_detectors_test(det_id):
    """Smoke-test a user's detector."""
    det = Detector.query.get_or_404(det_id)
    if det.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    result = detector_tester.run_smoke_test(det.api_url)
    det.status = "verified" if result["all_passed"] else "error"
    det.last_test = datetime.utcnow()
    det.test_details = json.dumps(result)
    db.session.commit()
    return jsonify(result)


@app.route("/api/user/detectors/<int:det_id>", methods=["DELETE"])
@login_required
def api_user_detectors_delete(det_id):
    """Delete a user's detector."""
    det = Detector.query.get_or_404(det_id)
    if det.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(det)
    db.session.commit()
    return jsonify({"ok": True})


# ── Legacy Detector Registry API (kept for backward compat) ──


@app.route("/api/detectors", methods=["GET"])
@login_required
def api_detectors_list():
    """JSON список зарегистрированных детекторов (legacy + DB)."""
    legacy = detector_registry.list_detectors()
    db_detectors = [d.to_dict() for d in Detector.query.all()]
    return jsonify(legacy + db_detectors)


@app.route("/api/detectors", methods=["POST"])
@login_required
def api_detectors_register():
    """Зарегистрировать новый детектор (saves to DB now)."""
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    api_url = (data.get("api_url") or "").strip()
    if not name or not api_url:
        return jsonify({"error": "Fields 'name' and 'api_url' are required"}), 400
    det = Detector(
        user_id=current_user.id,
        name=name,
        api_url=api_url,
        description=data.get("description", ""),
        author=data.get("author", ""),
        paper_url=data.get("paper_url", ""),
        github_url=data.get("github_url", ""),
    )
    db.session.add(det)
    db.session.commit()
    return jsonify(det.to_dict()), 201


@app.route("/api/detectors/<detector_id>/test", methods=["POST"])
@login_required
def api_detectors_test(detector_id):
    """Smoke-тест детектора (legacy or DB)."""
    # Try DB first
    try:
        det_id = int(detector_id)
        det = Detector.query.get(det_id)
        if det:
            result = detector_tester.run_smoke_test(det.api_url)
            det.status = "verified" if result["all_passed"] else "error"
            det.last_test = datetime.utcnow()
            det.test_details = json.dumps(result)
            db.session.commit()
            return jsonify(result)
    except (ValueError, TypeError):
        pass

    # Fallback to legacy registry
    det = detector_registry.get_detector(detector_id)
    if not det:
        return jsonify({"error": "Detector not found"}), 404
    result = detector_tester.run_smoke_test(det["api_url"])
    detector_registry.update_test_result(detector_id, result["all_passed"], result)
    return jsonify(result)


@app.route("/api/detectors/<detector_id>", methods=["DELETE"])
@login_required
def api_detectors_delete(detector_id):
    """Удалить детектор (legacy or DB)."""
    # Try DB first
    try:
        det_id = int(detector_id)
        det = Detector.query.get(det_id)
        if det:
            if det.user_id != current_user.id and not current_user.is_admin:
                return jsonify({"error": "Forbidden"}), 403
            db.session.delete(det)
            db.session.commit()
            return jsonify({"ok": True})
    except (ValueError, TypeError):
        pass

    # Fallback to legacy registry
    det = detector_registry.get_detector(detector_id)
    if not det:
        return jsonify({"error": "Detector not found"}), 404
    detector_registry.delete_detector(detector_id)
    return jsonify({"ok": True})


# ── Test Sets API ─────────────────────────────────────────────


@app.route("/api/test-sets", methods=["GET"])
@login_required
def api_test_sets_list():
    """List all active test sets."""
    sets = TestSet.query.filter_by(is_archived=0).all()
    return jsonify([ts.to_dict() for ts in sets])


@app.route("/api/test-sets", methods=["POST"])
@login_required
@admin_required
def api_test_sets_create():
    """Create a new test set (admin only)."""
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    dataset_keys = data.get("dataset_keys", [])
    if not name or not dataset_keys:
        return jsonify({"error": "name and dataset_keys are required"}), 400

    # Count total videos from existing runs
    total_videos = _count_videos_for_datasets(dataset_keys)

    ts = TestSet(
        name=name,
        description=data.get("description", ""),
        total_videos=total_videos,
        created_by=current_user.id,
    )
    ts.set_dataset_keys(dataset_keys)
    db.session.add(ts)
    db.session.commit()
    return jsonify(ts.to_dict()), 201


@app.route("/api/test-sets/<int:ts_id>/archive", methods=["POST"])
@login_required
@admin_required
def api_test_sets_archive(ts_id):
    """Archive or unarchive a test set."""
    ts = TestSet.query.get_or_404(ts_id)
    data = request.get_json(force=True)
    ts.is_archived = 1 if data.get("archive", True) else 0
    db.session.commit()
    return jsonify(ts.to_dict())


# ── Evaluations API ──────────────────────────────────────────


@app.route("/api/evaluations", methods=["POST"])
@login_required
def api_evaluations_create():
    """Start a new evaluation."""
    data = request.get_json(force=True)
    detector_id = data.get("detector_id")
    test_set_id = data.get("test_set_id")

    if not detector_id or not test_set_id:
        return jsonify({"error": "detector_id and test_set_id are required"}), 400

    det = Detector.query.get(detector_id)
    if not det or (det.user_id != current_user.id and not current_user.is_admin):
        return jsonify({"error": "Detector not found or access denied"}), 404

    ts = TestSet.query.get(test_set_id)
    if not ts:
        return jsonify({"error": "Test set not found"}), 404

    # Check limit: 1 running evaluation per user
    running = Evaluation.query.filter_by(
        user_id=current_user.id, status="running"
    ).first()
    if running:
        return jsonify({"error": "У вас уже есть запущенный прогон. Дождитесь завершения."}), 400

    ev = Evaluation(
        detector_id=detector_id,
        test_set_id=test_set_id,
        user_id=current_user.id,
        status="pending",
        total_videos=ts.total_videos,
    )
    db.session.add(ev)
    db.session.commit()

    # Start background thread
    evaluation_runner.start_evaluation(ev.id, app)

    return jsonify(ev.to_dict()), 201


@app.route("/api/evaluations/<int:eval_id>", methods=["GET"])
@login_required
def api_evaluations_status(eval_id):
    """Get evaluation status/progress."""
    ev = Evaluation.query.get_or_404(eval_id)
    if ev.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return jsonify(ev.to_dict())


@app.route("/api/evaluations/<int:eval_id>/cancel", methods=["POST"])
@login_required
def api_evaluations_cancel(eval_id):
    """Cancel a running evaluation."""
    ev = Evaluation.query.get_or_404(eval_id)
    if ev.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    if ev.status != "running":
        return jsonify({"error": "Evaluation is not running"}), 400
    evaluation_runner.cancel_evaluation(eval_id)
    return jsonify({"ok": True})


@app.route("/api/evaluations/<int:eval_id>/publish", methods=["POST"])
@login_required
def api_evaluations_publish(eval_id):
    """Publish or unpublish evaluation results."""
    ev = Evaluation.query.get_or_404(eval_id)
    if ev.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    if ev.status != "completed":
        return jsonify({"error": "Only completed evaluations can be published"}), 400
    data = request.get_json(force=True)
    ev.is_published = 1 if data.get("publish", True) else 0
    db.session.commit()
    return jsonify(ev.to_dict())


# ── Mock Detector ─────────────────────────────────────────────


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


# ── Helpers ──────────────────────────────────────────────────


def _count_videos_for_datasets(dataset_keys):
    """Count total unique videos across existing runs for given datasets."""
    manifest = evaluation_runner.build_video_manifest(set(dataset_keys), LOCAL_RUNS_DIR)
    return len(manifest)


def _get_published_runs():
    """Get published user evaluations as run-like dicts for rankings merge."""
    published = Evaluation.query.filter_by(status="completed", is_published=1).all()
    runs = []
    for ev in published:
        m = ev.get_metrics()
        if not m:
            continue
        # Create a run-like dict compatible with allRuns JS
        ts = TestSet.query.get(ev.test_set_id)
        det = Detector.query.get(ev.detector_id)
        if not ts or not det:
            continue
        for dk in ts.get_dataset_keys():
            runs.append({
                "id": f"user_eval_{ev.id}_{dk}",
                "detector": f"user:{det.name}",
                "dataset": dk,
                "date": ev.completed_at.strftime("%Y-%m-%d") if ev.completed_at else "",
                "total_videos": ev.total_videos,
                "auc": m.get("auc"),
                "accuracy": m.get("accuracy"),
                "eer": m.get("eer"),
                "ap": m.get("ap"),
                "precision": m.get("precision"),
                "recall": m.get("recall"),
                "f1": m.get("f1"),
                "fake_count": 0,
                "real_count": 0,
                "threshold": 0.5,
                "source": "user",
                "user_detector_name": det.name,
                "user_detector_author": det.author,
            })
    return runs


if __name__ == "__main__":
    print(f"Local runs directory: {LOCAL_RUNS_DIR}")
    print(f"Database: {DATABASE_PATH}")
    print(f"Starting dashboard on http://localhost:5050")
    app.run(host="127.0.0.1", port=5050, debug=True, use_reloader=False)
