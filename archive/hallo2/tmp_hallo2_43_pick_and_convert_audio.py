import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)
    return p.returncode

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"
vox = "/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac"
run = "preview_20260215_141828"
male_i = 94
female_i = 5

cmd = r"""
set -euo pipefail
cd __REPO__

python3 - <<'PY'
import os, json
vox = '__VOX__'
run = '__RUN__'
male_i = int('__MALE_I__')
female_i = int('__FEMALE_I__')

def pick_audio(i: int):
    persons = sorted([d for d in os.listdir(vox) if os.path.isdir(os.path.join(vox, d))])[:50]
    person = persons[i // 20]
    person_path = os.path.join(vox, person)

    clips = sorted([d for d in os.listdir(person_path) if os.path.isdir(os.path.join(person_path, d))])
    current_clip = clips[(i % 20) // 5]
    clip_dir = os.path.join(person_path, current_clip)

    files = sorted([f for f in os.listdir(clip_dir) if os.path.isfile(os.path.join(clip_dir, f))])
    audio_file = files[0]

    clip_path = os.path.join(clip_dir, audio_file)
    clip_name = f"{person}_{current_clip}_{os.path.splitext(audio_file)[0]}"
    return clip_path, clip_name

meta = {}
for i in [male_i, female_i]:
    p, name = pick_audio(i)
    meta[str(i)] = dict(audio_src=p, clip_name=name)

out_path = f"preview_runs/{run}/inputs/audio_meta.json"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
open(out_path, 'w').write(json.dumps(meta, indent=2))
print(json.dumps(meta, indent=2))
PY

male_src=$(python3 -c "import json;print(json.load(open('preview_runs/__RUN__/inputs/audio_meta.json'))['__MALE_I__']['audio_src'])")
female_src=$(python3 -c "import json;print(json.load(open('preview_runs/__RUN__/inputs/audio_meta.json'))['__FEMALE_I__']['audio_src'])")

cp -n "$male_src" preview_runs/__RUN__/inputs/audios/__MALE_I_PAD__.m4a
cp -n "$female_src" preview_runs/__RUN__/inputs/audios/__FEMALE_I_PAD__.m4a

ffmpeg -hide_banner -loglevel error -y -i preview_runs/__RUN__/inputs/audios/__MALE_I_PAD__.m4a -t 4 -ac 1 -ar 16000 preview_runs/__RUN__/inputs/audios/__MALE_I_PAD__.wav
ffmpeg -hide_banner -loglevel error -y -i preview_runs/__RUN__/inputs/audios/__FEMALE_I_PAD__.m4a -t 4 -ac 1 -ar 16000 preview_runs/__RUN__/inputs/audios/__FEMALE_I_PAD__.wav

ls -la preview_runs/__RUN__/inputs/audios
"""

cmd = (cmd.replace("__REPO__", repo)
          .replace("__VOX__", vox)
          .replace("__RUN__", run)
          .replace("__MALE_I__", str(male_i))
          .replace("__FEMALE_I__", str(female_i))
          .replace("__MALE_I_PAD__", f"{male_i:03d}")
          .replace("__FEMALE_I_PAD__", f"{female_i:03d}"))

sh(cmd)