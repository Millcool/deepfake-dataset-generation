#!/usr/bin/env python3
"""Run LivePortrait for one pair: source_video (face) + driving_video (motion). Output: source_num_driving_num.mp4"""
import os, sys, subprocess, tempfile
from pathlib import Path

def main():
    if len(sys.argv) < 5:
        print("Usage: run_single.py <source_video> <driving_video> <output_mp4_path> <gpu_id>")
        sys.exit(1)
    source_video = sys.argv[1]
    driving_video = sys.argv[2]
    output_mp4 = sys.argv[3]
    gpu_id = sys.argv[4]

    source_num = Path(source_video).stem
    driving_num = Path(driving_video).stem
    expected_name = f"{source_num}_{driving_num}.mp4"

    home = os.path.expanduser("~")
    python = os.path.join(home, "venvs", "liveportrait", "bin", "python")
    repo = os.path.join(home, "liveportrait")
    out_dir = tempfile.mkdtemp(prefix="lp_")

    # Extract first frame
    frame_path = os.path.join(out_dir, "source_frame.png")
    r = subprocess.run(["ffmpeg", "-y", "-i", source_video, "-vf", "select=eq(n\\,0)", "-frames:v", "1", frame_path],
                       capture_output=True, timeout=30)
    if r.returncode != 0 or not os.path.isfile(frame_path):
        print("Failed to extract frame from", source_video)
        sys.exit(1)

    env = {**os.environ, "CUDA_VISIBLE_DEVICES": gpu_id}
    cmd = [python, "inference.py", "-s", frame_path, "-d", driving_video, "-o", out_dir,
           "--flag_crop_driving_video", "--device_id", "0"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=repo, env=env)
    if r.returncode != 0:
        print("LivePortrait failed:", r.stderr[-500:])
        sys.exit(1)

    # Find output (e.g. source_frame--001.mp4) and rename/move to target
    lp_name = f"{Path(frame_path).stem}--{driving_num}.mp4"
    lp_path = os.path.join(out_dir, lp_name)
    if not os.path.isfile(lp_path):
        candidates = [f for f in os.listdir(out_dir) if f.endswith(".mp4") and "--" in f]
        if not candidates:
            print("No output mp4 found in", out_dir)
            sys.exit(1)
        lp_path = os.path.join(out_dir, candidates[0])

    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)
    if os.path.abspath(lp_path) != os.path.abspath(output_mp4):
        import shutil
        shutil.move(lp_path, output_mp4)
    print("Saved:", output_mp4)

    import shutil
    shutil.rmtree(out_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
