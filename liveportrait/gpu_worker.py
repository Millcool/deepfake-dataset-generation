#!/usr/bin/env python3
"""
GPU worker for LivePortrait batch generation.
Usage: gpu_worker.py <gpu_id> <tasks_json_file>

Loads the model ONCE, then processes all tasks in sequence.
"""
import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
from pathlib import Path

gpu_id = int(sys.argv[1])
tasks_file = sys.argv[2]

os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

home = os.path.expanduser("~")
repo = os.path.join(home, "liveportrait")
log_file = os.path.join(home, "liveportrait", "batch_log.txt")

# Add repo to path
sys.path.insert(0, repo)
os.chdir(repo)

def log(s):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [GPU {gpu_id}] {s}"
    with open(log_file, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)

log("Loading LivePortrait model...")
load_start = time.time()

from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.live_portrait_pipeline import LivePortraitPipeline
from src.config.argument_config import ArgumentConfig

inference_cfg = InferenceConfig(
    flag_use_half_precision=True,
    device_id=0  # always 0 since CUDA_VISIBLE_DEVICES is set
)
crop_cfg = CropConfig()
pipeline = LivePortraitPipeline(inference_cfg=inference_cfg, crop_cfg=crop_cfg)

log(f"Model loaded in {time.time() - load_start:.1f}s")

# Load tasks
with open(tasks_file) as f:
    tasks = json.load(f)

log(f"Processing {len(tasks)} tasks")
done = 0
fail = 0
skip = 0

for i, task in enumerate(tasks):
    source_video = task["source"]
    driving_video = task["driving"]
    output_path = task["output"]

    # Skip if already exists
    if os.path.isfile(output_path) and os.path.getsize(output_path) > 10000:
        skip += 1
        continue

    try:
        start = time.time()
        tmp_dir = tempfile.mkdtemp(prefix="lp_")

        # Extract first frame from source video
        frame_path = os.path.join(tmp_dir, "source_frame.png")
        subprocess.run(
            ["ffmpeg", "-y", "-i", source_video, "-vf", "select=eq(n\\,0)", "-frames:v", "1", frame_path],
            capture_output=True, timeout=30
        )

        if not os.path.isfile(frame_path):
            fail += 1
            log(f"FAIL extract frame: {os.path.basename(source_video)}")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            continue

        # Create args for pipeline
        source_num = Path(source_video).stem
        driving_num = Path(driving_video).stem

        args = ArgumentConfig()
        args.source = frame_path
        args.driving = driving_video
        args.output_dir = tmp_dir
        args.flag_crop_driving_video = True
        args.device_id = 0
        args.flag_relative_motion = True
        args.flag_pasteback = True
        args.flag_do_crop = True

        # Run pipeline
        pipeline.execute(args)

        # Find output and move
        out_name = f"{Path(frame_path).stem}--{driving_num}.mp4"
        out_path = os.path.join(tmp_dir, out_name)

        if not os.path.isfile(out_path):
            # Search for any mp4 with --
            candidates = [f for f in os.listdir(tmp_dir) if f.endswith(".mp4") and "--" in f]
            if candidates:
                out_path = os.path.join(tmp_dir, candidates[0])
            else:
                fail += 1
                log(f"FAIL no output: {source_num}_{driving_num}")
                shutil.rmtree(tmp_dir, ignore_errors=True)
                continue

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.move(out_path, output_path)
        done += 1
        elapsed = time.time() - start

        if done % 5 == 0:
            log(f"Progress: done={done} fail={fail} skip={skip} / {len(tasks)} ({elapsed:.1f}s last)")

        shutil.rmtree(tmp_dir, ignore_errors=True)

    except Exception as e:
        fail += 1
        log(f"ERROR: {os.path.basename(output_path)} {str(e)[:200]}")
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except:
            pass

log(f"DONE: done={done} fail={fail} skip={skip} / {len(tasks)}")
