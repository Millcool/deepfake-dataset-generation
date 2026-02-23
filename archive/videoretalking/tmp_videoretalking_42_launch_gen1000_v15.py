import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv_py = f"{repo}/.venv_videoretalking_20260215_210503/bin/python"
ffpp_orig = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Original"
vox2_root = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac"

run_id = "gen1000_vret2_15s_" + datetime.now().strftime("%Y%m%d_%H%M%S")
run_dir = Path(repo) / "batch_runs" / run_id

(run_dir / "inputs" / "videos").mkdir(parents=True, exist_ok=True)
(run_dir / "inputs" / "audios_m4a").mkdir(parents=True, exist_ok=True)
(run_dir / "inputs" / "audios_wav").mkdir(parents=True, exist_ok=True)
(run_dir / "outputs").mkdir(parents=True, exist_ok=True)
(run_dir / "logs").mkdir(parents=True, exist_ok=True)
(run_dir / "status").mkdir(parents=True, exist_ok=True)
(run_dir / "scripts").mkdir(parents=True, exist_ok=True)

persons = sorted(
    d for d in os.listdir(vox2_root)
    if d.startswith("id") and os.path.isdir(os.path.join(vox2_root, d))
)
if len(persons) < 50:
    raise RuntimeError(f"Not enough speakers in vox2_test_aac: {len(persons)} < 50")

selected_persons = persons[:50]
tasks = []

for i in range(1000):
    video_name = f"{i:03d}.mp4"
    video_src_shared = os.path.join(ffpp_orig, video_name)
    if not os.path.isfile(video_src_shared):
        raise FileNotFoundError(video_src_shared)

    person = selected_persons[i // 20]
    person_dir = os.path.join(vox2_root, person)
    clips = sorted(
        d for d in os.listdir(person_dir)
        if os.path.isdir(os.path.join(person_dir, d))
    )
    if len(clips) < 4:
        raise RuntimeError(f"Speaker {person} has <4 clip dirs")

    current_clip = clips[(i % 20) // 5]
    clip_dir = os.path.join(person_dir, current_clip)
    m4a_files = sorted(f for f in os.listdir(clip_dir) if f.lower().endswith(".m4a"))
    if not m4a_files:
        raise RuntimeError(f"No m4a files in {clip_dir}")

    first_audio = m4a_files[0]
    audio_src_shared = os.path.join(clip_dir, first_audio)
    audio_stem = os.path.splitext(first_audio)[0]
    audio_key = f"{person}_{current_clip}_{audio_stem}"

    task = {
        "i": i,
        "video_src_shared": video_src_shared,
        "video_local": str(run_dir / "inputs" / "videos" / video_name),
        "audio_src_shared": audio_src_shared,
        "audio_local_m4a": str(run_dir / "inputs" / "audios_m4a" / f"{audio_key}.m4a"),
        "audio_local_wav": str(run_dir / "inputs" / "audios_wav" / f"{audio_key}_15s.wav"),
        "outfile": str(run_dir / "outputs" / f"fake_{i:04d}.mp4"),
        "tmp_dir": f"{run_id}_i{i:04d}",
        "person": person,
        "current_clip": current_clip,
        "audio_key": audio_key,
    }
    tasks.append(task)

manifest_path = run_dir / "manifest.jsonl"
with manifest_path.open("w", encoding="utf-8") as f:
    for t in tasks:
        f.write(json.dumps(t, ensure_ascii=True) + "\n")

meta = {
    "run_id": run_id,
    "created_at": datetime.now().isoformat(timespec="seconds"),
    "repo": repo,
    "venv_python": venv_py,
    "ffpp_orig": ffpp_orig,
    "vox2_root": vox2_root,
    "tasks": 1000,
    "max_seconds": 15,
    "mapping": {
        "person": "i // 20",
        "current_clip": "(i % 20) // 5",
        "audio_file_rule": "first .m4a in sorted order",
    },
    "workers": [
        {"worker_id": 0, "gpu": 2},
        {"worker_id": 1, "gpu": 3},
    ],
}
(run_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

prepare_py = f'''import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

RUN_DIR = Path({str(run_dir)!r})
MANIFEST = RUN_DIR / "manifest.jsonl"

with MANIFEST.open("r", encoding="utf-8") as f:
    tasks = [json.loads(line) for line in f if line.strip()]

# Stage private video copies (1000 files).
for idx, t in enumerate(tasks, 1):
    src = t["video_src_shared"]
    dst = t["video_local"]
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
    if idx % 100 == 0:
        print(f"VIDEOS_STAGED={{idx}}/{{len(tasks)}}", flush=True)

# Prepare unique audio files: copy m4a + convert to 15s wav, 16kHz mono.
seen = set()
audio_jobs = []
for t in tasks:
    key = t["audio_key"]
    if key in seen:
        continue
    seen.add(key)
    audio_jobs.append((t["audio_src_shared"], t["audio_local_m4a"], t["audio_local_wav"]))

for idx, (src_m4a, dst_m4a, dst_wav) in enumerate(audio_jobs, 1):
    Path(dst_m4a).parent.mkdir(parents=True, exist_ok=True)
    Path(dst_wav).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(dst_m4a):
        shutil.copy2(src_m4a, dst_m4a)

    if not os.path.exists(dst_wav):
        cmd = [
            "ffmpeg", "-y", "-v", "error", "-t", "15",
            "-i", dst_m4a,
            "-ar", "16000", "-ac", "1",
            dst_wav,
        ]
        subprocess.run(cmd, check=True)

    if idx % 20 == 0 or idx == len(audio_jobs):
        print(f"AUDIOS_READY={{idx}}/{{len(audio_jobs)}}", flush=True)

status = {{
    "prepared_at": datetime.now().isoformat(timespec="seconds"),
    "videos_staged": len(tasks),
    "unique_audios_ready": len(audio_jobs),
}}
(RUN_DIR / "status" / "prepare_done.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
print("PREPARE_DONE", flush=True)
'''
(run_dir / "scripts" / "prepare_inputs.py").write_text(prepare_py, encoding="utf-8")

worker_py = f'''import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--run-dir", required=True)
parser.add_argument("--repo", required=True)
parser.add_argument("--python-bin", required=True)
parser.add_argument("--worker-id", type=int, required=True)
parser.add_argument("--num-workers", type=int, required=True)
parser.add_argument("--gpu-id", required=True)
args = parser.parse_args()

run_dir = Path(args.run_dir)
manifest = run_dir / "manifest.jsonl"
status_dir = run_dir / "status"
status_dir.mkdir(parents=True, exist_ok=True)

with manifest.open("r", encoding="utf-8") as f:
    tasks = [json.loads(line) for line in f if line.strip()]

selected = [t for pos, t in enumerate(tasks) if pos % args.num_workers == args.worker_id]

done = 0
skipped = 0
failed = 0
for idx, t in enumerate(selected, 1):
    out = t["outfile"]
    if os.path.exists(out):
        skipped += 1
        print(f"SKIP i={{t['i']}} out_exists={{out}}", flush=True)
        continue

    cmd = [
        args.python_bin,
        os.path.join(args.repo, "inference.py"),
        "--face", t["video_local"],
        "--audio", t["audio_local_wav"],
        "--outfile", out,
        "--tmp_dir", t["tmp_dir"],
    ]

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)
    env["GPEN_ENABLE_JIT_EXT"] = "0"
    env["MPLBACKEND"] = "Agg"

    print(f"START i={{t['i']}} worker={{args.worker_id}} gpu={{args.gpu_id}}", flush=True)
    p = subprocess.run(cmd, env=env)
    if p.returncode == 0 and os.path.exists(out):
        done += 1
        print(f"DONE i={{t['i']}} worker={{args.worker_id}} progress={{idx}}/{{len(selected)}}", flush=True)
    else:
        failed += 1
        print(f"FAIL i={{t['i']}} worker={{args.worker_id}} rc={{p.returncode}}", flush=True)

    rec = {{
        "time": datetime.now().isoformat(timespec="seconds"),
        "i": t["i"],
        "worker_id": args.worker_id,
        "gpu_id": args.gpu_id,
        "ok": (p.returncode == 0 and os.path.exists(out)),
        "returncode": p.returncode,
        "outfile": out,
    }}
    with (status_dir / f"worker_{{args.worker_id}}.jsonl").open("a", encoding="utf-8") as wf:
        wf.write(json.dumps(rec, ensure_ascii=True) + "\\n")

summary = {{
    "time": datetime.now().isoformat(timespec="seconds"),
    "worker_id": args.worker_id,
    "gpu_id": args.gpu_id,
    "selected": len(selected),
    "done": done,
    "skipped": skipped,
    "failed": failed,
}}
(status_dir / f"worker_{{args.worker_id}}_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("WORKER_SUMMARY", json.dumps(summary), flush=True)

if failed > 0:
    sys.exit(1)
'''
(run_dir / "scripts" / "worker.py").write_text(worker_py, encoding="utf-8")

launch_sh = f'''#!/usr/bin/env bash
set -euo pipefail

REPO={repo}
RUN_DIR={str(run_dir)}
PY={venv_py}

cd "$REPO"
mkdir -p "$RUN_DIR/logs" "$RUN_DIR/status"

echo "RUN_ID={run_id}" | tee "$RUN_DIR/status/run_info.txt"
echo "START_AT=$(date -Is)" | tee -a "$RUN_DIR/status/run_info.txt"

echo "[1/2] preparing private inputs..."
"$PY" "$RUN_DIR/scripts/prepare_inputs.py" > "$RUN_DIR/logs/prepare.log" 2>&1

echo "[2/2] starting workers..."
nohup "$PY" "$RUN_DIR/scripts/worker.py" \
  --run-dir "$RUN_DIR" --repo "$REPO" --python-bin "$PY" \
  --worker-id 0 --num-workers 2 --gpu-id 2 \
  > "$RUN_DIR/logs/worker0.log" 2>&1 < /dev/null &
echo $! > "$RUN_DIR/status/worker0.pid"

nohup "$PY" "$RUN_DIR/scripts/worker.py" \
  --run-dir "$RUN_DIR" --repo "$REPO" --python-bin "$PY" \
  --worker-id 1 --num-workers 2 --gpu-id 3 \
  > "$RUN_DIR/logs/worker1.log" 2>&1 < /dev/null &
echo $! > "$RUN_DIR/status/worker1.pid"

echo "WORKER0_PID=$(cat "$RUN_DIR/status/worker0.pid")" | tee -a "$RUN_DIR/status/run_info.txt"
echo "WORKER1_PID=$(cat "$RUN_DIR/status/worker1.pid")" | tee -a "$RUN_DIR/status/run_info.txt"

echo "LAUNCHED_AT=$(date -Is)" | tee -a "$RUN_DIR/status/run_info.txt"
'''
launch_path = run_dir / "launch.sh"
launch_path.write_text(launch_sh, encoding="utf-8")
os.chmod(launch_path, 0o755)

main_log = run_dir / "logs" / "main_launch.log"
main_pid = run_dir / "status" / "main_launch.pid"

subprocess.run(
    [
        "bash", "-lc",
        f"cd {repo} && nohup bash {launch_path} > {main_log} 2>&1 < /dev/null & echo $! > {main_pid}"
    ],
    check=True,
)

print("RUN_ID", run_id)
print("RUN_DIR", str(run_dir))
print("MAIN_LAUNCH_LOG", str(main_log))
print("MAIN_LAUNCH_PIDFILE", str(main_pid))
print("MANIFEST", str(manifest_path))
print("NOTE", "Videos and selected audios are staged as private copies in this run directory. Audio wav is trimmed to <=15s.")
