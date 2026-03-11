"""
Загрузчик данных из detection_eval/runs/.
Сканирует директории прогонов, парсит metrics.json, кэширует на 60 секунд.
"""

import os
import json
import time
import csv
import numpy as np
from pathlib import Path
from functools import lru_cache


# Базовый путь к runs/ — определяется при старте приложения
RUNS_DIR = None

# Кэш
_cache = {}
_cache_ts = 0
CACHE_TTL = 60  # секунд


def init(runs_dir):
    """Инициализация: задать путь к runs/."""
    global RUNS_DIR
    RUNS_DIR = runs_dir


def _scan_uncached():
    """Сканирует runs/, парсит metrics.json из каждого прогона."""
    if not RUNS_DIR or not os.path.isdir(RUNS_DIR):
        return []

    runs = []
    for entry in sorted(os.listdir(RUNS_DIR)):
        run_path = os.path.join(RUNS_DIR, entry)
        if not os.path.isdir(run_path):
            continue

        metrics_path = os.path.join(run_path, "metrics.json")
        if not os.path.isfile(metrics_path):
            continue

        try:
            with open(metrics_path) as f:
                metrics = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        # Извлечь дату из имени директории (YYYYMMDD_... или YYYYMMDD_HHMMSS_...)
        parts = entry.split("_")
        date_str = ""
        if len(parts) >= 2 and len(parts[0]) == 8 and parts[0].isdigit():
            date_str = f"{parts[0][:4]}-{parts[0][4:6]}-{parts[0][6:8]}"
            if len(parts[1]) >= 6 and parts[1][:6].isdigit():
                date_str += f" {parts[1][:2]}:{parts[1][2:4]}:{parts[1][4:6]}"

        # Поддержка двух форматов metrics.json:
        # GenConViT: метрики в metrics.{auc,...}, CM в confusion_matrix.overall.{TP,...}
        # CLIP:      метрики на верхнем уровне {auc,...}, CM как [[TN,FP],[FN,TP]]
        m = metrics.get("metrics", {})
        cm_raw = metrics.get("confusion_matrix", {})
        cm = cm_raw.get("overall", {}) if isinstance(cm_raw, dict) else {}

        run_info = {
            "id": entry,
            "path": run_path,
            "detector": metrics.get("detector", ""),
            "dataset": metrics.get("dataset", "") or _extract_dataset_from_run_id(entry),
            "date": date_str,
            "total_videos": metrics.get("total_videos", 0),
            "fake_count": metrics.get("fake_count", metrics.get("fake_videos", 0)),
            "real_count": metrics.get("real_count", metrics.get("real_videos", 0)),
            "auc": m.get("auc") or metrics.get("auc"),
            "accuracy": m.get("accuracy") or metrics.get("accuracy"),
            "eer": m.get("eer") or metrics.get("eer"),
            "ap": m.get("ap") or metrics.get("ap"),
            "precision": cm.get("precision") or metrics.get("precision"),
            "recall": cm.get("recall") or metrics.get("recall"),
            "f1": cm.get("f1") or metrics.get("f1"),
            "threshold": metrics.get("threshold") or metrics.get("eer_threshold"),
        }
        runs.append(run_info)

    return runs


def scan_runs():
    """Возвращает список прогонов (кэш 60 сек)."""
    global _cache, _cache_ts
    now = time.time()
    if "runs" in _cache and (now - _cache_ts) < CACHE_TTL:
        return _cache["runs"]

    runs = _scan_uncached()
    _cache["runs"] = runs
    _cache_ts = now
    return runs


def invalidate_cache():
    """Принудительно сбросить кэш."""
    global _cache, _cache_ts
    _cache = {}
    _cache_ts = 0


def _extract_dataset_from_run_id(run_id):
    """Извлечь имя датасета из run_id (напр. 20260305_112548_BlendSwap_FFpp_clip_dfdet)."""
    parts = run_id.split("_")
    # Пропускаем timestamp-части (цифровые), собираем до имени детектора
    name_parts = []
    for p in parts:
        if p.isdigit() and len(p) >= 6:
            continue
        name_parts.append(p)
    # Последние 1-2 части — детектор (genconvit, clip_dfdet и т.п.)
    # Пробуем убрать известные суффиксы
    name = "_".join(name_parts)
    known = ["_clip_dfdet", "_altfreezing", "_genconvit", "_cvit", "_sbi", "_npr", "_clip"]
    for suffix in known:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


def _normalize_metrics(metrics, run_id):
    """Нормализовать CLIP-формат metrics.json к общему формату дашборда."""
    # Если уже нормализован (GenConViT) — пропускаем
    if "metrics" in metrics and isinstance(metrics["metrics"], dict):
        # Дополнить отсутствующие поля
        if not metrics.get("dataset"):
            metrics["dataset"] = _extract_dataset_from_run_id(run_id)
        return metrics

    # CLIP-формат: метрики на верхнем уровне, нужно преобразовать
    if not metrics.get("dataset"):
        metrics["dataset"] = _extract_dataset_from_run_id(run_id)

    metrics.setdefault("threshold", metrics.get("eer_threshold", 0))
    metrics.setdefault("fake_count", metrics.get("fake_videos", 0))
    metrics.setdefault("real_count", metrics.get("real_videos", 0))

    # Создать вложенный metrics если нет
    metrics["metrics"] = {
        "auc": metrics.get("auc", 0),
        "accuracy": metrics.get("accuracy", 0),
        "eer": metrics.get("eer", 0),
        "ap": metrics.get("ap", 0),
        "eer_threshold": metrics.get("eer_threshold", 0),
    }

    # Нормализовать confusion_matrix
    cm_raw = metrics.get("confusion_matrix")
    if isinstance(cm_raw, list) and len(cm_raw) == 2:
        tn, fp = cm_raw[0][0], cm_raw[0][1]
        fn, tp = cm_raw[1][0], cm_raw[1][1]
        total = tn + fp + fn + tp
        prec = metrics.get("precision", round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0)
        rec = metrics.get("recall", round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0)
        f1 = metrics.get("f1", round(2 * tp / (2 * tp + fp + fn), 4) if (2 * tp + fp + fn) > 0 else 0)
        metrics["confusion_matrix"] = {
            "overall": {
                "TP": tp, "FP": fp, "TN": tn, "FN": fn,
                "precision": prec, "recall": rec, "f1": f1,
                "accuracy": metrics.get("accuracy", 0), "total": total,
            }
        }

    # Нормализовать score_stats
    ss = metrics.get("score_stats", {})
    if "fake" not in ss and "real_mean" in ss:
        metrics["score_stats"] = {
            "fake": {
                "mean": ss.get("fake_mean", 0), "std": ss.get("fake_std", 0),
                "min": 0, "max": 1, "median": ss.get("fake_mean", 0),
            },
            "real": {
                "mean": ss.get("real_mean", 0), "std": ss.get("real_std", 0),
                "min": 0, "max": 1, "median": ss.get("real_mean", 0),
            },
        }

    # Пустые заглушки для отсутствующих секций
    metrics.setdefault("histogram", {
        "bucket_width": 0.05, "num_buckets": 20, "buckets": [],
    })
    metrics.setdefault("demographic_metrics", {})

    return metrics


def get_run(run_id):
    """Получить полный metrics.json для одного прогона."""
    if not RUNS_DIR:
        return None

    run_path = os.path.join(RUNS_DIR, run_id)
    metrics_path = os.path.join(run_path, "metrics.json")
    if not os.path.isfile(metrics_path):
        return None

    with open(metrics_path) as f:
        metrics = json.load(f)

    metrics = _normalize_metrics(metrics, run_id)
    metrics["_run_id"] = run_id
    metrics["_run_path"] = run_path
    return metrics


def get_scores_df(run_id):
    """Загрузить scores.csv как список словарей (lazy — только по запросу)."""
    if not RUNS_DIR:
        return None

    scores_path = os.path.join(RUNS_DIR, run_id, "scores.csv")
    if not os.path.isfile(scores_path):
        return None

    rows = []
    with open(scores_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["score"] = float(row["score"])
            except (ValueError, KeyError):
                row["score"] = -1
            rows.append(row)
    return rows


def get_scores_array(run_id):
    """Компактный массив [score, is_fake] для клиентского пересчёта CM."""
    rows = get_scores_df(run_id)
    if not rows:
        return None
    result = []
    for r in rows:
        if r["score"] < 0:
            continue
        is_fake = 1 if r.get("label") == "fake" else 0
        result.append([round(r["score"], 6), is_fake])
    return result


def compute_roc_data(run_id):
    """Вычисляет FPR, TPR для ROC-кривой из scores.csv."""
    rows = get_scores_df(run_id)
    if not rows:
        return None

    y_true = []
    y_score = []
    for r in rows:
        if r["score"] < 0:
            continue
        y_true.append(1 if r.get("label") == "fake" else 0)
        y_score.append(r["score"])

    if len(set(y_true)) < 2:
        return None

    y_true = np.array(y_true)
    y_score = np.array(y_score)

    from sklearn.metrics import roc_curve, roc_auc_score

    fpr, tpr, thresholds = roc_curve(y_true, y_score, pos_label=1)
    auc = float(roc_auc_score(y_true, y_score))

    # Прореживание для JSON (макс 200 точек)
    if len(fpr) > 200:
        indices = np.linspace(0, len(fpr) - 1, 200, dtype=int)
        fpr = fpr[indices]
        tpr = tpr[indices]

    return {
        "fpr": [round(float(x), 6) for x in fpr],
        "tpr": [round(float(x), 6) for x in tpr],
        "auc": round(auc, 4),
    }


def list_figures(run_id):
    """Список PNG-файлов в figures/."""
    if not RUNS_DIR:
        return []

    figures_dir = os.path.join(RUNS_DIR, run_id, "figures")
    if not os.path.isdir(figures_dir):
        return []

    return sorted(f for f in os.listdir(figures_dir) if f.endswith(".png"))


def get_examples(run_id):
    """Загрузить examples_manifest.json для прогона (или None)."""
    if not RUNS_DIR:
        return None

    manifest_path = os.path.join(RUNS_DIR, run_id, "examples_manifest.json")
    if not os.path.isfile(manifest_path):
        return None

    try:
        with open(manifest_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def get_unique_datasets():
    """Уникальные датасеты из всех прогонов."""
    runs = scan_runs()
    return sorted(set(r["dataset"] for r in runs if r["dataset"]))


def get_unique_detectors():
    """Уникальные детекторы из всех прогонов."""
    runs = scan_runs()
    return sorted(set(r["detector"] for r in runs if r["detector"]))


def _aggregate_metrics(runs_list):
    """Средние метрики по списку прогонов."""
    metrics_keys = ["auc", "accuracy", "eer", "ap", "precision", "recall", "f1"]
    agg = {}
    for key in metrics_keys:
        values = [r[key] for r in runs_list if r.get(key) is not None]
        agg[key] = round(sum(values) / len(values), 4) if values else None
    agg["total_videos"] = sum(r.get("total_videos", 0) for r in runs_list)
    return agg


def aggregate_by_detector():
    """Рейтинг детекторов: средние метрики по всем датасетам."""
    runs = scan_runs()
    groups = {}
    for r in runs:
        det = r.get("detector")
        if not det:
            continue
        groups.setdefault(det, []).append(r)

    result = []
    for det, det_runs in groups.items():
        agg = _aggregate_metrics(det_runs)
        agg["name"] = det
        agg["n_datasets"] = len(set(r["dataset"] for r in det_runs))
        agg["n_runs"] = len(det_runs)
        agg["runs"] = sorted(det_runs, key=lambda r: r.get("auc") or 0, reverse=True)
        result.append(agg)

    result.sort(key=lambda x: x["auc"] or 0, reverse=True)
    for i, item in enumerate(result):
        item["rank"] = i + 1
    return result


def _build_thumbnail_index():
    """Сканирует ВСЕ runs/*/thumbnails/, строит {basename: [run_id, ...]}."""
    if not RUNS_DIR or not os.path.isdir(RUNS_DIR):
        return {}

    index = {}  # norm_basename -> [(run_id, original_filename), ...]
    for entry in os.listdir(RUNS_DIR):
        thumb_dir = os.path.join(RUNS_DIR, entry, "thumbnails")
        if not os.path.isdir(thumb_dir):
            continue
        for fname in os.listdir(thumb_dir):
            if fname.endswith(".jpg"):
                basename = os.path.splitext(fname)[0]
                # Normalize numeric basenames to match scores normalization
                norm_basename = basename
                if basename.isdigit() and len(basename) > 3:
                    norm_basename = basename.lstrip("0").zfill(3)
                index.setdefault(norm_basename, []).append((entry, fname))
    return index


def compute_video_analysis():
    """Кросс-прогонный анализ: какие видео чаще ошибочно классифицируются."""
    global _cache, _cache_ts
    now = time.time()
    if "video_analysis" in _cache and (now - _cache_ts) < CACHE_TTL:
        return _cache["video_analysis"]

    runs = scan_runs()
    thumb_index = _build_thumbnail_index()

    real_videos = {}   # basename -> list of results
    fake_videos = {}   # "dataset/basename" -> list of results

    for run in runs:
        rows = get_scores_df(run["id"])
        if not rows:
            continue
        threshold = run.get("threshold") or 0.5

        for row in rows:
            if row["score"] < 0:
                continue
            basename = os.path.splitext(os.path.basename(row["video_path"]))[0]
            # Normalize numeric basenames (e.g. "0009" -> "009") for cross-run matching
            if basename.isdigit() and len(basename) > 3:
                basename = basename.lstrip("0").zfill(3)
            predicted_fake = row["score"] >= threshold
            is_fake = row["label"] == "fake"
            correct = is_fake == predicted_fake

            entry = {
                "run_id": run["id"],
                "detector": run["detector"],
                "dataset": run["dataset"],
                "score": round(row["score"], 4),
                "threshold": round(threshold, 4),
                "correct": correct,
            }

            if row["label"] == "real":
                real_videos.setdefault(basename, []).append(entry)
            else:
                key = run["dataset"] + "/" + basename
                fake_videos.setdefault(key, []).append(entry)

    def aggregate(videos_dict, label):
        result = []
        for key, results in videos_dict.items():
            n_total = len(results)
            n_errors = sum(1 for r in results if not r["correct"])
            basename = key.split("/")[-1] if "/" in key else key
            dataset = key.split("/")[0] if "/" in key else None
            thumb_entries = thumb_index.get(basename, [])
            thumb_info = None
            if thumb_entries:
                run_id, orig_fname = thumb_entries[0]
                thumb_info = {"run_id": run_id, "filename": orig_fname}
            result.append({
                "basename": basename,
                "label": label,
                "dataset": dataset,
                "error_rate": round(n_errors / n_total, 4) if n_total else 0,
                "error_count": n_errors,
                "total_runs": n_total,
                "thumbnail": thumb_info,
                "results": sorted(results, key=lambda r: r["score"], reverse=True),
            })
        return result

    fp_list = aggregate(real_videos, "real")
    fn_list = aggregate(fake_videos, "fake")

    # Sort: most problematic first
    fp_list.sort(key=lambda x: (-x["error_rate"], -x["error_count"]))
    fn_list.sort(key=lambda x: (-x["error_rate"], -x["error_count"]))

    # Group FN by dataset
    fn_by_dataset = {}
    for item in fn_list:
        ds = item["dataset"] or "unknown"
        fn_by_dataset.setdefault(ds, []).append(item)

    # Always-correct counts (from full data, before truncation)
    always_correct_real = sum(1 for x in fp_list if x["error_rate"] == 0)
    always_correct_fake = {}
    for item in fn_list:
        ds = item["dataset"] or "unknown"
        if item["error_rate"] == 0:
            always_correct_fake[ds] = always_correct_fake.get(ds, 0) + 1

    # Total fake counts per dataset
    total_fake_by_dataset = {}
    for item in fn_list:
        ds = item["dataset"] or "unknown"
        total_fake_by_dataset[ds] = total_fake_by_dataset.get(ds, 0) + 1

    # Truncate FN to top-20 per dataset
    fn_by_dataset_trimmed = {}
    for ds in fn_by_dataset:
        fn_by_dataset_trimmed[ds] = fn_by_dataset[ds][:20]

    result = {
        "false_positives": fp_list[:50],
        "false_negatives_by_dataset": fn_by_dataset_trimmed,
        "always_correct": {
            "real_count": always_correct_real,
            "fake_by_dataset": always_correct_fake,
            "total_real": len(real_videos),
            "total_fake_by_dataset": total_fake_by_dataset,
        },
        "summary": {
            "total_runs": len(runs),
            "total_real_videos": len(real_videos),
            "fp_videos_count": sum(1 for x in fp_list if x["error_rate"] > 0),
        },
    }

    _cache["video_analysis"] = result
    return result


def aggregate_by_dataset():
    """Рейтинг датасетов: средние метрики по всем детекторам."""
    runs = scan_runs()
    groups = {}
    for r in runs:
        ds = r.get("dataset")
        if not ds:
            continue
        groups.setdefault(ds, []).append(r)

    result = []
    for ds, ds_runs in groups.items():
        agg = _aggregate_metrics(ds_runs)
        agg["name"] = ds
        agg["n_detectors"] = len(set(r["detector"] for r in ds_runs))
        agg["n_runs"] = len(ds_runs)
        agg["runs"] = sorted(ds_runs, key=lambda r: r.get("auc") or 0, reverse=True)
        result.append(agg)

    # Ниже AUC = deepfake труднее обнаружить = лучший алгоритм
    result.sort(key=lambda x: x["auc"] or 0, reverse=False)
    for i, item in enumerate(result):
        item["rank"] = i + 1
    return result
