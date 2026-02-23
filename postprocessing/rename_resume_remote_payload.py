import csv
import os
import signal
import subprocess
import time
from datetime import datetime

REPO = "/var/lib/ilanmironov@edu.hse.ru/musetalk"
ROOT = f"{REPO}/workspace/datasets/MuseTalk_FFpp_vox2"
OUTDIR = f"{ROOT}/outputs/results/v15"
MANIFEST = f"{ROOT}/metadata/manifest_1000.csv"
MANIFEST_NAMED = f"{ROOT}/metadata/manifest_1000_named.csv"
YAML_REMAIN = f"{ROOT}/metadata/inference_1000_named_remaining.yaml"
REPORT = f"{ROOT}/metadata/rename_resume_report.txt"

PIDFILE_OLD = f"{ROOT}/.gen_1000.pid"
PIDFILE_NEW = f"{ROOT}/.gen_1000_named.pid"
LOG_NEW = f"{ROOT}/logs/gen_1000_named.log"


def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def stop_old_generation() -> tuple[bool, str]:
    if not os.path.exists(PIDFILE_OLD):
        return True, "no_old_pidfile"
    try:
        with open(PIDFILE_OLD, "r", encoding="utf-8", errors="replace") as f:
            s = f.read().strip()
        pid = int(s)
    except Exception as e:
        return False, f"bad_old_pidfile: {e}"

    if not is_running(pid):
        return True, f"old_pid_not_running:{pid}"

    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not is_running(pid):
            return True, f"old_pid_stopped:{pid}"
        time.sleep(1)

    # Do not SIGKILL without explicit user approval.
    return False, f"old_pid_still_running:{pid}"


def clip_name_from_rel(rel: str) -> str:
    rel = rel.replace("\\", "/")
    parts = [p for p in rel.split("/") if p]
    if len(parts) >= 3:
        person = parts[0]
        yt = parts[1]
        clipfile = parts[-1]
        clip_id = os.path.splitext(clipfile)[0]
        return f"{person}_{yt}_{clip_id}"
    return os.path.splitext(os.path.basename(rel))[0]


def main() -> int:
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)

    ok, stop_msg = stop_old_generation()
    if not ok:
        with open(REPORT, "w", encoding="utf-8") as f:
            f.write(datetime.utcnow().isoformat() + "Z\n")
            f.write("STOP_FAILED " + stop_msg + "\n")
        print("STOP_FAILED", stop_msg)
        return 2

    with open(MANIFEST, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    renamed = 0
    already_named = 0
    conflicts = 0

    for row in rows:
        idx = int(row["idx"])
        video_name = os.path.splitext(row["video_file"])[0]
        clip_name = clip_name_from_rel(row["audio_src_rel"])
        new_name = f"{video_name}_{clip_name}.mp4"
        row["result_name"] = new_name

        src = os.path.join(OUTDIR, f"fake_{idx:04d}.mp4")
        dst = os.path.join(OUTDIR, new_name)

        if os.path.exists(dst):
            already_named += 1
            if os.path.exists(src):
                conflicts += 1
            continue

        if os.path.exists(src):
            os.rename(src, dst)
            renamed += 1

    with open(MANIFEST_NAMED, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    remain = []
    for row in rows:
        idx = int(row["idx"])
        out_name = row["result_name"]
        out_path = os.path.join(OUTDIR, out_name)
        if os.path.exists(out_path):
            continue

        video_path = os.path.join(ROOT, "inputs", "videos", row["video_file"])
        audio_path = row["audio_wav"]
        remain.append((idx, video_path, audio_path, out_name))

    with open(YAML_REMAIN, "w", encoding="utf-8") as f:
        for idx, video_path, audio_path, out_name in remain:
            f.write(f"task_{idx:04d}:\n")
            f.write(f"  video_path: \"{video_path}\"\n")
            f.write(f"  audio_path: \"{audio_path}\"\n")
            f.write(f"  result_name: \"{out_name}\"\n\n")

    # Relaunch remaining tasks in background.
    if remain:
        cmd = (
            "set -e; "
            "export CUDA_VISIBLE_DEVICES=1; export MPLBACKEND=Agg; "
            "source /var/lib/ilanmironov@edu.hse.ru/venvs/musetalk/bin/activate; "
            f"cd {REPO}; "
            "nohup bash -lc \""
            f"python -m scripts.inference "
            f"--inference_config {YAML_REMAIN} "
            f"--result_dir {ROOT}/outputs/results "
            "--unet_model_path models/musetalkV15/unet.pth "
            "--unet_config models/musetalkV15/musetalk.json "
            "--version v15 --gpu_id 0 --use_float16 --batch_size 8 --use_saved_coord --saved_coord"
            f"\" > {LOG_NEW} 2>&1 & echo $! > {PIDFILE_NEW}; cat {PIDFILE_NEW}"
        )
        p = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
        new_pid = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
    else:
        new_pid = ""

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(datetime.utcnow().isoformat() + "Z\n")
        f.write(f"STOP_OK {stop_msg}\n")
        f.write(f"RENAMED {renamed}\n")
        f.write(f"ALREADY_NAMED {already_named}\n")
        f.write(f"CONFLICTS {conflicts}\n")
        f.write(f"REMAIN_TASKS {len(remain)}\n")
        if new_pid:
            f.write(f"NEW_PID {new_pid}\n")
            f.write(f"NEW_LOG {LOG_NEW}\n")

    print("STOP_OK", stop_msg)
    print("RENAMED", renamed)
    print("ALREADY_NAMED", already_named)
    print("CONFLICTS", conflicts)
    print("REMAIN_TASKS", len(remain))
    if new_pid:
        print("NEW_PID", new_pid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())