"""
Asynchronous evaluation runner: sends videos to user's detector API, collects scores,
computes metrics. Runs in a background thread, updates DB as it goes.
"""

import csv
import os
import time
import threading
from datetime import datetime

import requests
import numpy as np
from sklearn.metrics import (
    roc_auc_score, accuracy_score, average_precision_score,
    precision_score, recall_score, f1_score, roc_curve,
)

# Active evaluations: eval_id -> threading.Event (for cancellation)
_cancel_events = {}
_lock = threading.Lock()


def start_evaluation(eval_id, app):
    """Launch a background thread for the given evaluation."""
    cancel_event = threading.Event()
    with _lock:
        _cancel_events[eval_id] = cancel_event

    t = threading.Thread(
        target=_run_evaluation,
        args=(eval_id, cancel_event, app),
        daemon=True,
    )
    t.start()
    return True


def cancel_evaluation(eval_id):
    """Signal cancellation for a running evaluation."""
    with _lock:
        event = _cancel_events.get(eval_id)
    if event:
        event.set()
        return True
    return False


def build_video_manifest(dataset_keys, runs_dir):
    """
    Build a list of videos from existing pre-loaded runs' scores.csv files.
    Returns list of dicts: {video_path, label, dataset_key}
    """
    manifest = []
    seen = set()

    if not os.path.isdir(runs_dir):
        return manifest

    for run_dir in sorted(os.listdir(runs_dir)):
        scores_path = os.path.join(runs_dir, run_dir, "scores.csv")
        if not os.path.isfile(scores_path):
            continue

        # Extract dataset from run_id
        dataset_key = _extract_dataset(run_dir)
        if not dataset_key or dataset_key not in dataset_keys:
            continue

        try:
            with open(scores_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    vp = row.get("video_path", "").strip()
                    label = row.get("label", "").strip()
                    if not vp or not label:
                        continue
                    key = (vp, dataset_key)
                    if key not in seen:
                        seen.add(key)
                        manifest.append({
                            "video_path": vp,
                            "label": label,
                            "dataset_key": dataset_key,
                        })
        except Exception:
            continue

    return manifest


# Known detector prefixes (same as data_loader.py)
_KNOWN_DETECTORS = ["clip_dfdet", "altfreezing", "genconvit", "cvit", "sbi", "npr", "clip"]


def _extract_dataset(run_id):
    """Extract dataset key from run_id like '20250515_123456_LivePortrait_FFpp_genconvit'."""
    # Remove date prefix (YYYYMMDD_HHMMSS_)
    parts = run_id.split("_", 2)
    if len(parts) < 3:
        return None
    remainder = parts[2]

    # Try to strip known detector suffixes
    for det in sorted(_KNOWN_DETECTORS, key=len, reverse=True):
        if remainder.endswith("_" + det):
            return remainder[: -(len(det) + 1)]
    return None


def _run_evaluation(eval_id, cancel_event, app):
    """Main evaluation loop. Runs in background thread."""
    with app.app_context():
        from models import db, Evaluation, EvaluationScore, Detector, TestSet

        evaluation = Evaluation.query.get(eval_id)
        if not evaluation:
            return

        detector = Detector.query.get(evaluation.detector_id)
        test_set = TestSet.query.get(evaluation.test_set_id)
        if not detector or not test_set:
            evaluation.status = "failed"
            evaluation.error_message = "Detector or test set not found"
            db.session.commit()
            return

        # Get runs dir
        runs_dir = os.environ.get("RUNS_DIR", "")
        if not runs_dir:
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            runs_dir = os.path.join(project_root, "detection_eval", "runs")

        # Build manifest
        dataset_keys = set(test_set.get_dataset_keys())
        manifest = build_video_manifest(dataset_keys, runs_dir)

        if not manifest:
            evaluation.status = "failed"
            evaluation.error_message = "No videos found for selected datasets"
            db.session.commit()
            return

        evaluation.status = "running"
        evaluation.total_videos = len(manifest)
        evaluation.started_at = datetime.utcnow()
        db.session.commit()

        api_url = detector.api_url
        video_cache_dir = os.environ.get(
            "VIDEO_CACHE_DIR",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_cache"),
        )
        os.makedirs(video_cache_dir, exist_ok=True)

        start_time = time.time()
        errors_count = 0

        for i, item in enumerate(manifest):
            if cancel_event.is_set():
                evaluation.status = "cancelled"
                evaluation.completed_at = datetime.utcnow()
                db.session.commit()
                _cleanup(eval_id)
                return

            video_path = item["video_path"]
            label = item["label"]
            dataset_key = item["dataset_key"]

            score_val = None
            predicted_label = None
            error_msg = None

            try:
                # Try to find the video in runs directory (scores.csv has relative paths)
                video_file = _find_video_file(video_path, runs_dir, video_cache_dir)

                if video_file and os.path.isfile(video_file):
                    with open(video_file, "rb") as f:
                        resp = requests.post(
                            api_url,
                            files={"file": (os.path.basename(video_path), f, "video/mp4")},
                            timeout=120,
                        )
                    if resp.status_code == 200:
                        data = resp.json()
                        score_val = float(data.get("score", 0))
                        predicted_label = "fake" if score_val > 0.5 else "real"
                    else:
                        error_msg = f"HTTP {resp.status_code}"
                        errors_count += 1
                else:
                    # No local file; skip with error
                    error_msg = "Video file not found locally"
                    errors_count += 1

            except requests.Timeout:
                error_msg = "Timeout (120s)"
                errors_count += 1
            except requests.ConnectionError:
                error_msg = "Connection refused"
                errors_count += 1
            except Exception as e:
                error_msg = str(e)[:200]
                errors_count += 1

            # First video error -> fail fast
            if i == 0 and error_msg:
                evaluation.status = "failed"
                evaluation.error_message = f"First video failed: {error_msg}"
                evaluation.errors_count = errors_count
                evaluation.completed_at = datetime.utcnow()
                db.session.commit()
                _cleanup(eval_id)
                return

            # Save score
            ev_score = EvaluationScore(
                evaluation_id=eval_id,
                video_path=video_path,
                label=label,
                dataset_key=dataset_key,
                score=score_val,
                predicted_label=predicted_label,
                error=error_msg,
                processed_at=datetime.utcnow(),
            )
            db.session.add(ev_score)

            # Update progress
            evaluation.videos_done = i + 1
            evaluation.errors_count = errors_count
            elapsed = time.time() - start_time
            evaluation.avg_time_per_video = elapsed / (i + 1)
            db.session.commit()

        # Compute metrics
        metrics = _compute_metrics(eval_id, db, EvaluationScore)

        evaluation.status = "completed"
        evaluation.completed_at = datetime.utcnow()
        if metrics:
            evaluation.set_metrics(metrics)
        db.session.commit()
        _cleanup(eval_id)


def _find_video_file(video_path, runs_dir, cache_dir):
    """Try to locate a video file locally. Returns path or None."""
    # video_path from scores.csv is typically like:
    # /path/to/dataset/fake/video_001.mp4 or real/video_001.mp4
    # Check if it exists as absolute path
    if os.path.isfile(video_path):
        return video_path

    # Check in video cache
    basename = os.path.basename(video_path)
    cached = os.path.join(cache_dir, basename)
    if os.path.isfile(cached):
        return cached

    # Scan runs directory for the file
    for run_name in os.listdir(runs_dir):
        # Check if video exists inside run's data
        candidate = os.path.join(runs_dir, run_name, "videos", basename)
        if os.path.isfile(candidate):
            return candidate

    return None


def _compute_metrics(eval_id, db, EvaluationScore):
    """Compute AUC, accuracy, EER, AP, precision, recall, F1 from scores."""
    scores = EvaluationScore.query.filter_by(evaluation_id=eval_id).all()

    y_true = []
    y_scores = []
    y_pred = []

    for s in scores:
        if s.score is None:
            continue
        y_true.append(1 if s.label == "fake" else 0)
        y_scores.append(s.score)
        y_pred.append(1 if s.predicted_label == "fake" else 0)

    if len(y_true) < 2:
        return None

    y_true = np.array(y_true)
    y_scores = np.array(y_scores)
    y_pred = np.array(y_pred)

    # Need both classes
    if len(set(y_true)) < 2:
        return {
            "auc": None,
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "eer": None,
            "ap": None,
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        }

    try:
        auc = float(roc_auc_score(y_true, y_scores))
    except Exception:
        auc = None

    try:
        ap = float(average_precision_score(y_true, y_scores))
    except Exception:
        ap = None

    # EER
    eer = None
    try:
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)
        fnr = 1 - tpr
        idx = np.nanargmin(np.abs(fpr - fnr))
        eer = float((fpr[idx] + fnr[idx]) / 2)
    except Exception:
        pass

    return {
        "auc": auc,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "eer": eer,
        "ap": ap,
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def _cleanup(eval_id):
    """Remove cancel event after evaluation finishes."""
    with _lock:
        _cancel_events.pop(eval_id, None)
