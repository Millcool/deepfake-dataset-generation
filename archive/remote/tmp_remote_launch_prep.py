import os
import subprocess
import textwrap

REPO = "/var/lib/ilanmironov@edu.hse.ru/musetalk"
DATASET = "MuseTalk_FFpp_vox2"
ROOT = f"{REPO}/workspace/datasets/{DATASET}"
SCRIPT = f"{ROOT}/prepare_1000.py"
LOGDIR = f"{ROOT}/logs"
LOG = f"{LOGDIR}/prepare_1000.log"
PIDFILE = f"{ROOT}/.prepare_1000.pid"
DONE = f"{ROOT}/.prepare_1000.done"

prep_code = r'''
import csv
import glob
import os
import shutil
import subprocess
import sys
from datetime import datetime

REPO = "/var/lib/ilanmironov@edu.hse.ru/musetalk"
DATASET = "MuseTalk_FFpp_vox2"
ROOT = f"{REPO}/workspace/datasets/{DATASET}"

VID_SYM = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_videos"
AUD_SYM = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/Wav2Lip_FFpp_vox2/real_audio"

def realpath(p: str) -> str:
    return subprocess.check_output(["bash", "-lc", f"readlink -f {p!s}"]).decode().strip()

def ensure_dirs():
    for p in [
        ROOT,
        f"{ROOT}/inputs/videos",
        f"{ROOT}/inputs/audio_m4a",
        f"{ROOT}/inputs/audio_wav",
        f"{ROOT}/outputs",
        f"{ROOT}/metadata",
        f"{ROOT}/logs",
    ]:
        os.makedirs(p, exist_ok=True)

def list_videos(vid_root: str):
    vids = sorted(glob.glob(os.path.join(vid_root, "*.mp4")))
    if len(vids) < 1000:
        raise RuntimeError(f"Need >=1000 videos, found {len(vids)} in {vid_root}")
    return vids[:1000]

def pick_audios_round_robin(aud_root: str, n: int = 1000):
    speakers = sorted(glob.glob(os.path.join(aud_root, "id*")))
    per_sp = []
    for sp in speakers:
        files = sorted(glob.glob(os.path.join(sp, "*", "*.m4a")))
        if files:
            per_sp.append(files)
    iters = [iter(lst) for lst in per_sp]
    out = []
    while len(out) < n and iters:
        next_iters = []
        for it in iters:
            try:
                out.append(next(it))
                next_iters.append(it)
                if len(out) >= n:
                    break
            except StopIteration:
                continue
        iters = next_iters
    if len(out) < n:
        raise RuntimeError(f"Need {n} audios, got {len(out)}")
    return out

def copy_if_missing(src: str, dst: str):
    if os.path.exists(dst):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst, follow_symlinks=True)
    return True

def ffmpeg_to_wav(src_m4a: str, dst_wav: str):
    if os.path.exists(dst_wav) and os.path.getsize(dst_wav) > 0:
        return False
    os.makedirs(os.path.dirname(dst_wav), exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-v", "warning",
        "-i", src_m4a,
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        dst_wav,
    ]
    subprocess.check_call(cmd)
    return True

def main():
    ensure_dirs()

    vid_root = realpath(VID_SYM)
    aud_root = realpath(AUD_SYM)

    videos = list_videos(vid_root)
    audios = pick_audios_round_robin(aud_root, 1000)

    video_dst_paths = []
    for src in videos:
        dst = os.path.join(ROOT, "inputs/videos", os.path.basename(src))
        copy_if_missing(src, dst)
        video_dst_paths.append(dst)

    audio_rel_paths = []
    audio_src_paths = []
    audio_m4a_dst_paths = []
    audio_wav_dst_paths = []

    for i, src in enumerate(audios):
        rel = os.path.relpath(src, aud_root)
        dst_m4a = os.path.join(ROOT, "inputs/audio_m4a", rel)
        copy_if_missing(src, dst_m4a)
        dst_wav = os.path.join(ROOT, "inputs/audio_wav", f"audio_{i:04d}.wav")
        ffmpeg_to_wav(dst_m4a, dst_wav)

        audio_rel_paths.append(rel)
        audio_src_paths.append(src)
        audio_m4a_dst_paths.append(dst_m4a)
        audio_wav_dst_paths.append(dst_wav)

        if (i + 1) % 50 == 0:
            print(f"audio_prepared {i+1}/1000")
            sys.stdout.flush()

    # Write inference YAML (1000 tasks)
    yml_path = os.path.join(ROOT, "metadata", "inference_1000.yaml")
    with open(yml_path, "w", encoding="utf-8") as f:
        for i in range(1000):
            f.write(f"task_{i:04d}:\n")
            f.write(f"  video_path: \"{video_dst_paths[i]}\"\n")
            f.write(f"  audio_path: \"{audio_wav_dst_paths[i]}\"\n")
            f.write(f"  result_name: \"fake_{i:04d}.mp4\"\n\n")

    # Write manifest CSV
    csv_path = os.path.join(ROOT, "metadata", "manifest_1000.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "idx",
            "video_file",
            "audio_src_rel",
            "audio_src_abs",
            "audio_m4a_copy",
            "audio_wav",
            "result_name",
        ])
        for i in range(1000):
            w.writerow([
                i,
                os.path.basename(video_dst_paths[i]),
                audio_rel_paths[i],
                audio_src_paths[i],
                audio_m4a_dst_paths[i],
                audio_wav_dst_paths[i],
                f"fake_{i:04d}.mp4",
            ])

    with open(os.path.join(ROOT, "metadata", "PREPARED_AT.txt"), "w", encoding="utf-8") as f:
        f.write(datetime.utcnow().isoformat() + "Z\n")
        f.write(f"vid_root={vid_root}\n")
        f.write(f"aud_root={aud_root}\n")

    print("PREP_DONE")

if __name__ == "__main__":
    main()
'''

launcher = f"""
set -e
REPO='{REPO}'
ROOT='{ROOT}'
SCRIPT='{SCRIPT}'
LOGDIR='{LOGDIR}'
LOG='{LOG}'
PIDFILE='{PIDFILE}'
DONE='{DONE}'

mkdir -p "$LOGDIR"
python3 - <<'PY'
import os
os.makedirs(os.path.dirname(r"{SCRIPT}"), exist_ok=True)
with open(r"{SCRIPT}", 'w', encoding='utf-8') as f:
    f.write({prep_code!r})
print('WROTE', r"{SCRIPT}")
PY

if [ -f "$DONE" ]; then
  echo "ALREADY_DONE"
  exit 0
fi

# Run in background so the Jupyter request returns quickly.
nohup bash -lc "set -e; source /var/lib/ilanmironov@edu.hse.ru/venvs/musetalk/bin/activate; python3 '$SCRIPT'; echo 0 > '$DONE'" > "$LOG" 2>&1 &
echo $! > "$PIDFILE"
echo "STARTED_PID=$(cat $PIDFILE)"
echo "LOG=$LOG"
"""

p = subprocess.run(["bash", "-lc", launcher], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print('exit', p.returncode)