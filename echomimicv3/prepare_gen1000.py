#!/usr/bin/env python3
"""
EchoMimic V3 — prepare_gen1000.py
Prepares all inputs for 1000-video generation:
  1. Creates workspace directory structure
  2. Copies V1 manifest, adds frame_640x480 column
  3. Resizes all 1000 frames to 640x480 (PIL LANCZOS)
  4. Creates symlinks for audio wav files (already 16kHz mono from V1)
  5. Saves new manifest as metadata/manifest_1000.csv

Runs quickly (no GPU needed). Execute on the remote server.
"""
import os
import sys
import csv
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_V1 = Path('/var/lib/ilanmironov@edu.hse.ru/echomimic/workspace/datasets/EchoMimic_FFpp_vox2')
BASE_V3 = Path('/var/lib/ilanmironov@edu.hse.ru/echomimic_v3')
WS      = BASE_V3 / 'workspace' / 'datasets' / 'EchoMimicV3_FFpp_vox2'

V1_MANIFEST  = BASE_V1 / 'metadata' / 'manifest_1000.csv'
V1_FRAMES    = BASE_V1 / 'inputs' / 'frames'
V1_AUDIO_WAV = BASE_V1 / 'inputs' / 'audio_wav'

FRAMES_DIR   = WS / 'inputs' / 'frames_640x480'
AUDIO_DIR    = WS / 'inputs' / 'audio_wav'
META_DIR     = WS / 'metadata'
OUTPUT_DIR   = WS / 'outputs'
LOGS_DIR     = WS / 'logs'

TARGET_WIDTH  = 640
TARGET_HEIGHT = 480

# ---------------------------------------------------------------------------
# Step 0: create directory tree
# ---------------------------------------------------------------------------
print("=" * 60)
print("EchoMimic V3  —  prepare_gen1000.py")
print("=" * 60)
t_start = time.time()

for d in [FRAMES_DIR, AUDIO_DIR, META_DIR, OUTPUT_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
    print(f"  dir: {d}")

# ---------------------------------------------------------------------------
# Step 1: read V1 manifest
# ---------------------------------------------------------------------------
print(f"\nSTEP 1/4  Reading V1 manifest: {V1_MANIFEST}")
if not V1_MANIFEST.exists():
    print(f"ERROR: V1 manifest not found: {V1_MANIFEST}")
    sys.exit(1)

with open(V1_MANIFEST, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    v1_rows = list(reader)

print(f"  V1 manifest: {len(v1_rows)} rows")
print(f"  Columns: {list(v1_rows[0].keys())}")

if len(v1_rows) != 1000:
    print(f"WARNING: Expected 1000 rows, got {len(v1_rows)}")

# ---------------------------------------------------------------------------
# Step 2: resize frames to 640x480
# ---------------------------------------------------------------------------
print(f"\nSTEP 2/4  Resizing {len(v1_rows)} frames to {TARGET_WIDTH}x{TARGET_HEIGHT}")

# Import PIL here (after printing header so user sees progress even if PIL is missing)
try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

resized_count = 0
skipped_count = 0

for i, row in enumerate(v1_rows):
    idx = int(row['idx'])
    src_frame = Path(row['target_frame'])
    dst_name = f"{idx:03d}_first_640x480.jpg"
    dst_frame = FRAMES_DIR / dst_name

    if dst_frame.exists() and dst_frame.stat().st_size > 1000:
        skipped_count += 1
    else:
        if not src_frame.exists():
            print(f"  ERROR: source frame missing: {src_frame}")
            sys.exit(1)

        img = Image.open(src_frame).convert('RGB')
        img_resized = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
        img_resized.save(str(dst_frame), quality=95)
        resized_count += 1

    if (i + 1) % 100 == 0:
        print(f"  frames processed: {i + 1}/1000 (resized={resized_count}, skipped={skipped_count})")

print(f"  Done: resized={resized_count}, skipped={skipped_count}")

# ---------------------------------------------------------------------------
# Step 3: create audio symlinks
# ---------------------------------------------------------------------------
print(f"\nSTEP 3/4  Creating audio symlinks")

link_count = 0
link_skipped = 0

for row in v1_rows:
    wav_src = Path(row['audio_wav'])
    wav_name = wav_src.name
    wav_dst = AUDIO_DIR / wav_name

    if wav_dst.exists() or wav_dst.is_symlink():
        link_skipped += 1
    else:
        if not wav_src.exists():
            print(f"  ERROR: audio source missing: {wav_src}")
            sys.exit(1)
        os.symlink(wav_src, wav_dst)
        link_count += 1

print(f"  Done: created={link_count}, skipped={link_skipped}")

# ---------------------------------------------------------------------------
# Step 4: build new manifest with frame_640x480 column
# ---------------------------------------------------------------------------
print(f"\nSTEP 4/4  Building V3 manifest")

v3_rows = []
for row in v1_rows:
    idx = int(row['idx'])
    new_row = dict(row)  # copy all V1 columns
    new_row['frame_640x480'] = str(FRAMES_DIR / f"{idx:03d}_first_640x480.jpg")
    # Update audio_wav to point to V3 symlink (for self-contained workspace)
    wav_name = Path(row['audio_wav']).name
    new_row['audio_wav'] = str(AUDIO_DIR / wav_name)
    v3_rows.append(new_row)

# Column order: keep V1 columns, append new one at end
fieldnames = list(v1_rows[0].keys()) + ['frame_640x480']

manifest_path = META_DIR / 'manifest_1000.csv'
with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(v3_rows)

print(f"  Manifest saved: {manifest_path}")
print(f"  Columns: {fieldnames}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
elapsed = time.time() - t_start
n_frames = len(list(FRAMES_DIR.glob('*.jpg')))
n_audio  = len(list(AUDIO_DIR.glob('*.wav')))

print(f"\n{'=' * 60}")
print(f"PREPARATION COMPLETE in {elapsed:.1f}s")
print(f"{'=' * 60}")
print(f"  Workspace:    {WS}")
print(f"  Frames:       {n_frames} files in {FRAMES_DIR}")
print(f"  Audio:        {n_audio} files in {AUDIO_DIR}")
print(f"  Manifest:     {manifest_path} ({len(v3_rows)} rows)")
print(f"  Outputs dir:  {OUTPUT_DIR}")
print(f"  Logs dir:     {LOGS_DIR}")
print(f"")
print(f"Sample row (idx=0):")
for k, v in v3_rows[0].items():
    print(f"  {k}: {v}")
print(f"\nSample row (idx=999):")
for k, v in v3_rows[-1].items():
    print(f"  {k}: {v}")
print(f"\nNext step: run batch_generate_v3.py via launch_gen1000.sh")
