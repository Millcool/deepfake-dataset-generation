import datetime
import os
import subprocess
from pathlib import Path


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv = ".venv_videoretalking_20260215_210503"
run = "preview_" + datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S") + "_vret"

male_i = 94
female_i = 5

ffpp = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Gender_divided"
vox = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac"

prep_sh = f"{repo}/preview_runs/{run}/run_previews.sh"
prep_log = f"{repo}/logs/preview_prep_{run}.log"
prep_pid = f"{repo}/logs/preview_prep_{run}.pid"

Path(f"{repo}/preview_runs/{run}").mkdir(parents=True, exist_ok=True)
Path(f"{repo}/logs").mkdir(parents=True, exist_ok=True)

script = f"""#!/usr/bin/env bash
set -euo pipefail

REPO="{repo}"
VENV="{venv}"
RUN="{run}"
FFPP="{ffpp}"
VOX="{vox}"
MALE_I="{male_i}"
FEMALE_I="{female_i}"

echo PREP_START $(date -Is)
cd "$REPO"
mkdir -p "preview_runs/$RUN/inputs/videos" "preview_runs/$RUN/inputs/audios" "preview_runs/$RUN/outputs"

cp -f "$FFPP/male/094.mp4" "preview_runs/$RUN/inputs/videos/094.mp4"
cp -f "$FFPP/female/005.mp4" "preview_runs/$RUN/inputs/videos/005.mp4"

ffmpeg -y -v warning -t 4 -i "preview_runs/$RUN/inputs/videos/094.mp4" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k "preview_runs/$RUN/inputs/videos/094_4s.mp4"
ffmpeg -y -v warning -t 4 -i "preview_runs/$RUN/inputs/videos/005.mp4" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k "preview_runs/$RUN/inputs/videos/005_4s.mp4"

python3 - <<PY
import json, os
vox = "$VOX"
def pick_audio(i: int):
    persons = sorted(d for d in os.listdir(vox) if d.startswith("id") and os.path.isdir(os.path.join(vox, d)))
    person = persons[i // 20]
    person_path = os.path.join(vox, person)
    clips = sorted(d for d in os.listdir(person_path) if os.path.isdir(os.path.join(person_path, d)))
    current_clip = clips[(i % 20) // 5]
    clip_dir = os.path.join(person_path, current_clip)
    files = sorted(f for f in os.listdir(clip_dir) if f.lower().endswith(".m4a"))
    audio_file = files[0]
    clip_path = os.path.join(clip_dir, audio_file)
    clip_name = f"{{person}}_{{current_clip}}_{{os.path.splitext(audio_file)[0]}}"
    return clip_path, clip_name
male_i = int("$MALE_I")
female_i = int("$FEMALE_I")
male_src, male_name = pick_audio(male_i)
female_src, female_name = pick_audio(female_i)
meta = {{
  "male": {{"i": male_i, "audio_src": male_src, "clip_name": male_name}},
  "female": {{"i": female_i, "audio_src": female_src, "clip_name": female_name}},
}}
with open(f"preview_runs/{run}/inputs/audio_meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)
print("MALE_AUDIO_SRC", male_src)
print("FEMALE_AUDIO_SRC", female_src)
PY

MALE_SRC=$(python3 -c "import json; print(json.load(open('preview_runs/$RUN/inputs/audio_meta.json'))['male']['audio_src'])")
FEMALE_SRC=$(python3 -c "import json; print(json.load(open('preview_runs/$RUN/inputs/audio_meta.json'))['female']['audio_src'])")

cp -f "$MALE_SRC" "preview_runs/$RUN/inputs/audios/094.m4a"
cp -f "$FEMALE_SRC" "preview_runs/$RUN/inputs/audios/005.m4a"

ffmpeg -y -v warning -t 4 -i "preview_runs/$RUN/inputs/audios/094.m4a" -ar 16000 -ac 1 "preview_runs/$RUN/inputs/audios/094.wav"
ffmpeg -y -v warning -t 4 -i "preview_runs/$RUN/inputs/audios/005.m4a" -ar 16000 -ac 1 "preview_runs/$RUN/inputs/audios/005.wav"

echo PREP_DONE $(date -Is)
echo RUN "$RUN"

# Launch previews. Use venv python directly; avoid `source` to keep this script simple.

env CUDA_VISIBLE_DEVICES=2 MPLBACKEND=Agg GPEN_ENABLE_JIT_EXT=0 \\
  "$REPO/$VENV/bin/python" "$REPO/inference.py" \\
    --face "$REPO/preview_runs/$RUN/inputs/videos/094_4s.mp4" \\
    --audio "$REPO/preview_runs/$RUN/inputs/audios/094.wav" \\
    --outfile "$REPO/preview_runs/$RUN/outputs/male_094.mp4" \\
    --tmp_dir "${{RUN}}_male" \\
  > "$REPO/logs/preview_male_${{RUN}}.log" 2>&1 < /dev/null &
echo $! > "$REPO/logs/preview_male_${{RUN}}.pid"

env CUDA_VISIBLE_DEVICES=3 MPLBACKEND=Agg GPEN_ENABLE_JIT_EXT=0 \\
  "$REPO/$VENV/bin/python" "$REPO/inference.py" \\
    --face "$REPO/preview_runs/$RUN/inputs/videos/005_4s.mp4" \\
    --audio "$REPO/preview_runs/$RUN/inputs/audios/005.wav" \\
    --outfile "$REPO/preview_runs/$RUN/outputs/female_005.mp4" \\
    --tmp_dir "${{RUN}}_female" \\
  > "$REPO/logs/preview_female_${{RUN}}.log" 2>&1 < /dev/null &
echo $! > "$REPO/logs/preview_female_${{RUN}}.pid"

echo MALE_PID $(cat "$REPO/logs/preview_male_${{RUN}}.pid")
echo FEMALE_PID $(cat "$REPO/logs/preview_female_${{RUN}}.pid")
echo PREVIEW_LAUNCHED $(date -Is)
"""

Path(prep_sh).write_text(script, encoding="utf-8")
os.chmod(prep_sh, 0o755)

subprocess.run(
    [
        "bash",
        "-lc",
        f"cd {repo} && nohup bash {prep_sh} > {prep_log} 2>&1 < /dev/null & echo $! > {prep_pid}",
    ],
    check=True,
)

print("RUN", run)
print("PREP_SH", prep_sh)
print("PREP_LOG", prep_log)
print("PREP_PIDFILE", prep_pid)

