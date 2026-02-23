import os
import subprocess
from pathlib import Path


repo = "/var/lib/ilanmironov@edu.hse.ru/video-retalking"
venv = ".venv_videoretalking_20260215_210503"
run = "preview_20260215_221353_vret2"

male_i = 94
female_i = 5

vox = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac"

script_path = f"{repo}/preview_runs/{run}/launch_previews.sh"
launch_log = f"{repo}/logs/preview_launch_{run}.log"
launch_pid = f"{repo}/logs/preview_launch_{run}.pid"

Path(f"{repo}/preview_runs/{run}").mkdir(parents=True, exist_ok=True)
Path(f"{repo}/logs").mkdir(parents=True, exist_ok=True)

script = f"""#!/usr/bin/env bash
set -euo pipefail
set -x

REPO="{repo}"
VENV="{venv}"
RUN="{run}"
VOX="{vox}"
MALE_I="{male_i}"
FEMALE_I="{female_i}"

cd "$REPO"
mkdir -p "preview_runs/$RUN/inputs/audios" "preview_runs/$RUN/outputs" logs

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

ffmpeg -y -v error -t 4 -i "preview_runs/$RUN/inputs/audios/094.m4a" -ar 16000 -ac 1 "preview_runs/$RUN/inputs/audios/094.wav"
ffmpeg -y -v error -t 4 -i "preview_runs/$RUN/inputs/audios/005.m4a" -ar 16000 -ac 1 "preview_runs/$RUN/inputs/audios/005.wav"

# Launch previews (separate temp dirs to avoid collisions)
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
"""

Path(script_path).write_text(script, encoding="utf-8")
os.chmod(script_path, 0o755)

subprocess.run(
    [
        "bash",
        "-lc",
        f"cd {repo} && nohup bash {script_path} > {launch_log} 2>&1 < /dev/null & echo $! > {launch_pid}",
    ],
    check=True,
)

print("RUN", run)
print("LAUNCH_LOG", launch_log)
print("LAUNCH_PIDFILE", launch_pid)

