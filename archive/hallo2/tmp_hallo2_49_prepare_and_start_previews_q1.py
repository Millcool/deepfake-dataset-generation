import json
import os
import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    if p.returncode != 0:
        raise SystemExit(p.returncode)

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
venv = ".venv_hallo2_20260215_133957"
run = "preview_20260215_174900_q1"

ffpp = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Gender_divided"
vox = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac"

# Same i as earlier for comparison
male_i = 94
female_i = 5

def pick_audio(i: int):
    persons = sorted(
        d for d in os.listdir(vox) if d.startswith("id") and os.path.isdir(os.path.join(vox, d))
    )
    person = persons[i // 20]
    person_path = os.path.join(vox, person)
    clips = sorted([d for d in os.listdir(person_path) if os.path.isdir(os.path.join(person_path, d))])
    current_clip = clips[(i % 20) // 5]
    clip_dir = os.path.join(person_path, current_clip)
    files = sorted([f for f in os.listdir(clip_dir) if f.lower().endswith(".m4a")])
    audio_file = files[0]
    clip_path = os.path.join(clip_dir, audio_file)
    clip_name = f"{person}_{current_clip}_{os.path.splitext(audio_file)[0]}"
    return clip_path, clip_name

male_audio_src, male_clip = pick_audio(male_i)
female_audio_src, female_clip = pick_audio(female_i)

meta = {
    "male": {"i": male_i, "audio_src": male_audio_src, "clip_name": male_clip},
    "female": {"i": female_i, "audio_src": female_audio_src, "clip_name": female_clip},
}

script = f"""
set -euo pipefail
cd {repo}

mkdir -p preview_runs/{run}/inputs/videos preview_runs/{run}/inputs/images preview_runs/{run}/inputs/audios
mkdir -p preview_runs/{run}/configs preview_runs/{run}/outputs/male preview_runs/{run}/outputs/female
mkdir -p logs

# Copy target videos into repo-local workspace
cp -f {ffpp}/male/094.mp4 preview_runs/{run}/inputs/videos/094.mp4
cp -f {ffpp}/female/005.mp4 preview_runs/{run}/inputs/videos/005.mp4

# Extract full first frame (no center crop); pipeline will handle face region internally
ffmpeg -y -v warning -i preview_runs/{run}/inputs/videos/094.mp4 -vf "select=eq(n\\,0)" -frames:v 1 -q:v 2 preview_runs/{run}/inputs/images/094.jpg
ffmpeg -y -v warning -i preview_runs/{run}/inputs/videos/005.mp4 -vf "select=eq(n\\,0)" -frames:v 1 -q:v 2 preview_runs/{run}/inputs/images/005.jpg

# Copy + convert audio (convert only copies); keep 4 seconds like previous run for fast iteration
cp -f {male_audio_src} preview_runs/{run}/inputs/audios/094.m4a
cp -f {female_audio_src} preview_runs/{run}/inputs/audios/005.m4a

ffmpeg -y -v warning -t 4 -i preview_runs/{run}/inputs/audios/094.m4a -ar 16000 -ac 1 preview_runs/{run}/inputs/audios/094.wav
ffmpeg -y -v warning -t 4 -i preview_runs/{run}/inputs/audios/005.m4a -ar 16000 -ac 1 preview_runs/{run}/inputs/audios/005.wav

cat > preview_runs/{run}/inputs/audio_meta.json << 'JSON'
{json.dumps(meta, indent=2)}
JSON

# Create configs from upstream long.yaml; restore full quality steps
cp configs/inference/long.yaml preview_runs/{run}/configs/male.yaml
cp configs/inference/long.yaml preview_runs/{run}/configs/female.yaml

sed -i "s|^source_image: .*|source_image: ./preview_runs/{run}/inputs/images/094.jpg|" preview_runs/{run}/configs/male.yaml
sed -i "s|^driving_audio: .*|driving_audio: ./preview_runs/{run}/inputs/audios/094.wav|" preview_runs/{run}/configs/male.yaml
sed -i "s|^save_path: .*|save_path: ./preview_runs/{run}/outputs/male/|" preview_runs/{run}/configs/male.yaml

sed -i "s|^source_image: .*|source_image: ./preview_runs/{run}/inputs/images/005.jpg|" preview_runs/{run}/configs/female.yaml
sed -i "s|^driving_audio: .*|driving_audio: ./preview_runs/{run}/inputs/audios/005.wav|" preview_runs/{run}/configs/female.yaml
sed -i "s|^save_path: .*|save_path: ./preview_runs/{run}/outputs/female/|" preview_runs/{run}/configs/female.yaml

# Start both runs: increase face/lip weights and expand face region to improve expression transfer
nohup bash -lc 'set -euo pipefail; \
  echo START $(date -Is); \
  export CUDA_VISIBLE_DEVICES=2; export MPLBACKEND=Agg; export PYTHONUNBUFFERED=1; \
  ./{venv}/bin/python scripts/inference_long.py \
    --config preview_runs/{run}/configs/male.yaml \
    --audio_ckpt_dir pretrained_models/hallo2 \
    --pose_weight 1.0 --face_weight 1.3 --lip_weight 1.7 \
    --face_expand_ratio 1.3 \
    ; \
  echo DONE $(date -Is)' > logs/preview_male_{run}.log 2>&1 < /dev/null &
echo $! > logs/preview_male_{run}.pid

nohup bash -lc 'set -euo pipefail; \
  echo START $(date -Is); \
  export CUDA_VISIBLE_DEVICES=3; export MPLBACKEND=Agg; export PYTHONUNBUFFERED=1; \
  ./{venv}/bin/python scripts/inference_long.py \
    --config preview_runs/{run}/configs/female.yaml \
    --audio_ckpt_dir pretrained_models/hallo2 \
    --pose_weight 1.0 --face_weight 1.3 --lip_weight 1.7 \
    --face_expand_ratio 1.3 \
    ; \
  echo DONE $(date -Is)' > logs/preview_female_{run}.log 2>&1 < /dev/null &
echo $! > logs/preview_female_{run}.pid

echo RUN {run}
echo MALE_PID $(cat logs/preview_male_{run}.pid)
echo FEMALE_PID $(cat logs/preview_female_{run}.pid)
"""

sh(script)

