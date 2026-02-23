#!/usr/bin/env python3
"""
Batch LivePortrait generation: builds tasks, splits across 4 GPUs, launches gpu_worker.py per GPU.
Each worker loads the model ONCE and processes all its tasks.
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path

home = os.path.expanduser("~")
PYTHON = os.path.join(home, "venvs", "liveportrait", "bin", "python")
GPU_WORKER = os.path.join(home, "liveportrait", "gpu_worker.py")
DATASET_REAL = os.path.join(home, "Imaginaire", "dataset", "real")
DATASET_FAKE = os.path.join(home, "Imaginaire", "dataset", "fake_liveportrait")
LOG_FILE = os.path.join(home, "liveportrait", "batch_log.txt")
NUM_GPUS = 4
BLOCK_SIZE = 20


def log(s):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {s}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def build_task_list():
    all_tasks = []
    for gender in ["female", "male"]:
        real_dir = os.path.join(DATASET_REAL, gender)
        fake_dir = os.path.join(DATASET_FAKE, gender)
        os.makedirs(fake_dir, exist_ok=True)

        videos = sorted([f for f in os.listdir(real_dir) if f.endswith(".mp4")])
        n = len(videos)
        log(f"{gender}: {n} videos found")

        source_idx = n - 1
        block_start = 0

        while block_start < n and source_idx >= 0:
            source_file = videos[source_idx]
            source_path = os.path.join(real_dir, source_file)
            source_num = Path(source_file).stem

            block_end = min(block_start + BLOCK_SIZE, n)
            for i in range(block_start, block_end):
                driving_file = videos[i]
                driving_num = Path(driving_file).stem
                output_name = f"{source_num}_{driving_num}.mp4"
                output_path = os.path.join(fake_dir, output_name)
                all_tasks.append({
                    "source": source_path,
                    "driving": os.path.join(real_dir, driving_file),
                    "output": output_path
                })

            block_start = block_end
            source_idx -= 1

    return all_tasks


if __name__ == "__main__":
    log("=" * 60)
    log("LivePortrait batch generation (optimized) started")
    log("=" * 60)

    start_time = time.time()
    all_tasks = build_task_list()
    log(f"Total tasks: {len(all_tasks)}")

    # Split tasks across GPUs
    gpu_tasks = [[] for _ in range(NUM_GPUS)]
    for i, task in enumerate(all_tasks):
        gpu_tasks[i % NUM_GPUS].append(task)

    # Write task files
    task_files = []
    for g in range(NUM_GPUS):
        tf = os.path.join(home, "liveportrait", f"tasks_gpu{g}.json")
        with open(tf, "w") as f:
            json.dump(gpu_tasks[g], f)
        task_files.append(tf)
        log(f"GPU {g}: {len(gpu_tasks[g])} tasks -> {tf}")

    processes = []
    for g in range(NUM_GPUS):
        p = subprocess.Popen(
            [PYTHON, "-u", GPU_WORKER, str(g), task_files[g]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(p)
        log(f"GPU {g}: launched PID {p.pid}")

    # Wait for all to finish
    for g, p in enumerate(processes):
        p.wait()
        log(f"GPU {g}: finished with code {p.returncode}")

    elapsed = time.time() - start_time
    log("=" * 60)
    log(f"ALL FINISHED in {elapsed/3600:.1f} hours ({elapsed:.0f}s)")

    total = 0
    for gender in ["female", "male"]:
        fake_dir = os.path.join(DATASET_FAKE, gender)
        if os.path.isdir(fake_dir):
            files = [f for f in os.listdir(fake_dir) if f.endswith(".mp4")]
            log(f"{gender} fake: {len(files)} files")
            total += len(files)
    log(f"Total generated: {total} / {len(all_tasks)}")
    log("=" * 60)
