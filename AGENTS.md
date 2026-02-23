# Agent Rules

These rules are mandatory for all next tasks.

## Remote Working Directory

- All work must be done on the remote server.
- Do not perform task work locally on the user's computer.
- Main remote working directory: `/var/lib/ilanmironov@edu.hse.ru/` (project folders like `liveportrait`, `musetalk`, etc. live here).
- If a task can be done remotely, do it remotely in this directory.
- Do not switch to other remote directories unless the user explicitly asks for it.

## Deletion Policy

- Never delete any file or folder without the user's explicit consent.
- This includes any deletion method (`rm`, Python file APIs, Jupyter Contents API `DELETE`, overwriting that causes data loss, etc.).
- If deletion is needed, ask first and wait for a clear approval.

## Reusable Repository Workflow

- For each new repository, first read its `README.md` (or `readme.md`) and follow the same high-level flow adapted to that repo's algorithm.
- Standard flow:

1. Prepare environment and dependencies.
2. Download/check model weights.
3. Run a single inference smoke test to verify pipeline health.
4. Generate preview videos for validation: one male and one female (or 1-2 representative videos if gender split is unavailable).
5. Send preview outputs to the user and wait for explicit approval.
6. Only after user approval, launch large-scale generation (target: 1000 videos).

- Do not start 1000-video generation before explicit user confirmation.

### Detailed Operational Steps for a New Repo

**Step 0 — Determine modality.**
Read the repo's README and inference script. Key signals:
- Has `--audio` or `--driven_audio` argument → **audio-to-face** (use Audio-to-Face methodology, needs FF++ + VoxCeleb2).
- Has `--source` and `--driving` (both video/image) → **face-to-face** (use Face-to-Face methodology, needs FF++ only, gender split first).
- Some repos support both modes — ask user which mode to use.

**Step 1 — Clone and environment setup on remote server.**
```
cd /var/lib/ilanmironov@edu.hse.ru/
git clone <repo_url> <repo_name>
cd <repo_name>
python3 -m venv .venv_<repo_name>
source .venv_<repo_name>/bin/activate
pip install -r requirements.txt
```
- If the repo needs conda, create a conda env instead (check README).
- Log the venv path — it is needed for all future launches.
- Some repos need patching (e.g., `basicsr`, `pkg_resources`, custom CUDA ops). Check for build errors, apply fixes, and document them.

**Step 2 — Download model weights.**
- Most repos use `huggingface-cli download` or direct URLs.
- Check if weights directory already exists from a previous setup before re-downloading.
- Typical weight location: `<repo>/pretrained_weights/` or `<repo>/checkpoints/`.

**Step 3 — Smoke test.**
- Run the repo's example inference command with its bundled test inputs.
- Verify the output file is created and is a valid video (non-zero size, playable).
- Check GPU VRAM usage during smoke test — this determines whether to use single-process or multi-worker pattern for full generation.

**Step 4 — Prepare inputs for 1000-video generation.**
Create a workspace directory: `<repo>/workspace/datasets/<RepoName>_FFpp_vox2/` (or `_FFpp` for face-to-face).
Inside it:
```
inputs/
  videos/         # symlinks or copies of FF++ 000.mp4–999.mp4
  audio_m4a/      # (audio-to-face only) copies of selected VoxCeleb2 .m4a files
  audio_wav/      # (audio-to-face only) converted .wav versions
metadata/
  manifest_1000.csv   # mapping: idx → video_file, audio_file, output_name
outputs/
  results/            # generated fakes go here
logs/
```
- Build the manifest using `methodology__audio_name.py` logic (audio-to-face) or gender-split pairing (face-to-face).
- Convert `.m4a` → `.wav` if needed: `ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav`

**Step 5 — Preview generation.**
- Pick 1 male target (e.g., `000.mp4`) and 1 female target (e.g., `001.mp4`) with different audio sources.
- Run inference for just these 2 and show results to user.
- Wait for explicit approval before proceeding.

**Step 6 — Full 1000-video generation.**
- Write a generation script or YAML config listing all 1000 tasks.
- Wrap each task in try/except to survive individual failures.
- Launch with nohup, save PID, redirect logs.
- Monitor periodically until completion.

**Step 7 — Post-generation.**
- Count outputs, identify gaps, retry failed videos if possible.
- Copy final dataset to `shared/datasets/<RepoName>_FFpp_vox2/`.
- Write reproducibility instruction.
- Upload to GitLab after user approval.

### Algorithm Tracking

- All algorithms (completed, in progress, and planned) are tracked in `algorithm.md`.
- When starting a new algorithm, update `algorithm.md` to move it from "Planned" to "In Progress".
- When finishing an algorithm (1000 videos + shared upload + readme + GitLab), update `algorithm.md` to move it to "Completed".
- Always check `algorithm.md` before starting a new repo to avoid duplicate work.

## Dataset Methodology (Accepted)

- Apply methodology from `deepfake2025/methodology-for-datasets` for generation tasks.

### Face-to-Face

- Split dataset by gender first (use `gender_division.py` logic or equivalent).
- Generate separately within each gender group.
- Source/target pairing rule:
1. Take source videos from the end of sorted list (`...999, 998, ...`).
2. Take targets in consecutive blocks of 20 from the beginning (`000-019`, then `020-039`, ...).
3. Pair one source with its 20-target block, then move to the next source and next block.
- If model does not support video as source, use first frame of source video.

### Audio-to-Face

- Targets are dataset videos in consecutive order; each target video is used once.
- Audio sources are selected by sorted speaker IDs.
- For each speaker:
1. Use 4 different interview/video-index folders (sorted order).
2. From each folder take the first audio file (`.m4a`) in sorted order.
3. Reuse each selected audio 5 times.
- Total usage per speaker is 20 generations (4 audio x 5 repeats).
- Mapping rule from `audio_name.py` for 1000 targets: `person = i // 20`, `current_clip = (i % 20) // 5`.
- If model does not support video as target, use first frame of target video.

## Post-Generation Requirements

- After generating 1000 videos, always create a full reproducibility instruction:
1. End-to-end pipeline steps.
2. Exact data flow and naming conventions.
3. Issues encountered and how they were resolved.
4. What is required for someone else to repeat the process.
- **All reproducibility documents (readme.md) must be written in Russian.**
- Then upload the generated 1000-video dataset to `shared` on the remote server.
- The `shared` upload step must not be mentioned inside the reproducibility instruction document.
- Final step: upload the reproducibility instruction and required base files for rerun to GitLab.
- GitLab upload is allowed only after the user's explicit approval.

## Dataset Naming and Staging Rules (General)

- Do not hardcode a specific repository name in shared dataset naming.
- Shared dataset folder naming must follow task modality:
1. Video + audio pipelines: `<RepoName>_FFpp_vox2`
2. Video-only pipelines: `<RepoName>_FFpp`
3. Audio-only pipelines: `<RepoName>_vox2`
- For each repository, run all preparation and generation in its own working directory:
  - `/var/lib/ilanmironov@edu.hse.ru/<repo_name>`
- If format conversion is required (audio/video/frame), convert only files created as copies inside that repository working directory.
- Never modify original source datasets or any pre-existing files in `shared/datasets/*`.
- Copy prepared data and final generated dataset to `shared` only after repository-local preparation/generation steps are complete.

## Server Interaction Protocol

- The end-to-end server interaction and execution protocol is documented in `REMOTE_SERVER_WORKFLOW.md`.
- Future agents must follow `REMOTE_SERVER_WORKFLOW.md` when connecting to the remote server, running jobs, and publishing results.

## Practical Execution Guide

### How to Run Code Remotely

Use `remote_exec.py` — the ready-made local tool that handles Jupyter WebSocket sessions:

```bash
python remote_exec.py \
  --base "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru" \
  --token "<TOKEN_FROM_kod.txt>" \
  --code-file "<local_script.py>" \
  --timeout 60
```

Workflow pattern:
1. Write a temporary Python script locally (e.g., `_tmp_my_task.py`).
2. Execute it via `remote_exec.py` — the script runs on the remote server.
3. All `print()` output is streamed back. The last line is `EXEC_STATUS ok` or `EXEC_STATUS error`.

Token: read from `kod.txt` (URL parameter `?token=...`). Token may change between sessions — always re-read before use.

### GPU Layout (4x NVIDIA T4 16GB)

| GPU | VRAM   | Notes |
|-----|--------|-------|
| 0   | 15356 MiB | Often occupied by Jupyter kernel / large models |
| 1   | 15356 MiB | Good for single-GPU generation (MuseTalk, Hallo2) |
| 2   | 15356 MiB | Used by multi-worker setups (e.g., Video-Retalking worker 0) |
| 3   | 15356 MiB | Used by multi-worker setups (e.g., Video-Retalking worker 1) |

- Always check `nvidia-smi` before launching to avoid CUDA OOM.
- Use `CUDA_VISIBLE_DEVICES=<N>` to pin a process to a specific GPU.
- Inside inference scripts `--gpu_id 0` refers to the first *visible* device after CUDA_VISIBLE_DEVICES filtering.

### Virtual Environment Patterns

Each repo may use a different venv. Known patterns:
- **System-level venv**: `/var/lib/private/ilanmironov@edu.hse.ru/venvs/<repo_name>/`
  - Activate: `source /var/lib/private/ilanmironov@edu.hse.ru/venvs/<repo_name>/bin/activate`
  - Example: MuseTalk
- **Repo-local venv**: `/var/lib/ilanmironov@edu.hse.ru/<repo_name>/.venv_<name>/`
  - Example: Video-Retalking (`.venv_videoretalking_20260215_210503`)

When setting up a new repo, create the venv and note the path in logs for future reference.

### Source Dataset Locations

| Dataset | Path | Format |
|---------|------|--------|
| FaceForensics++ C23 (original) | `/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Original/` | `000.mp4` – `999.mp4` |
| VoxCeleb2 test (audio) | `/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac/` | `id<NNNNN>/<ytid>/<clip>.m4a` |
| VoxCeleb1 test (wav) | `/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox1_test_wav/` | `.wav` |
| Gender split CSV | Generated by `methodology__gender_division.py` on FF++ videos | `gender_predictions.csv` |

- VoxCeleb2 audio is `.m4a` — most models need `.wav`. Convert with: `ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav`
- For audio-to-face: first 50 speaker IDs from VoxCeleb2 are used (50 speakers × 4 audio × 5 repeats = 1000).
- Never modify files in `shared/datasets/*`. Always copy to repo-local workspace first.

### Long-Running Process Management

For generation of 1000 videos (hours to days):
1. **Always use `nohup`** to detach from the Jupyter kernel:
   ```python
   cmd = "nohup python -m scripts.inference ... > /path/to/log.log 2>&1 & echo $! > /path/to/.pid"
   subprocess.run(["bash", "-lc", cmd], ...)
   ```
2. **Save PID** to a `.pid` file for later monitoring/kill.
3. **Redirect all output** to a `.log` file.
4. **Monitor periodically** — count output mp4 files, tail the log, check `ps -p <PID>`.

### Monitoring Checklist

When checking generation status, always verify:
1. **Process alive?** — `ps -p <PID> -o pid,stat,etime`
2. **GPU in use?** — `nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv,noheader`
3. **Output count** — count `.mp4` files in the output directory
4. **Log tail** — last 20 lines of the generation log (look for progress bars, errors)
5. **Gaps** — compare output filenames against expected indices to find missing videos

### Generation Architecture Patterns

Two proven patterns for 1000-video generation:

**Pattern A: Single-process sequential** (used by MuseTalk)
- One Python process iterates over a YAML config of tasks.
- Each task wrapped in `try/except` — failures are logged, process continues.
- Pros: simple. Cons: slower (1 GPU), no parallelism.

**Pattern B: Multi-worker parallel** (used by Video-Retalking)
- A `manifest.jsonl` lists all 1000 tasks.
- N worker scripts each take every Nth task (round-robin).
- Each worker runs on its own GPU via `CUDA_VISIBLE_DEVICES`.
- Worker logs to its own `worker_N.log` and `worker_N.jsonl` status file.
- Pros: 2-4x faster. Cons: more complex setup.

Choose based on model's VRAM usage: if a single inference fits in ~4-6 GB, use multi-worker. If it needs 12+ GB, use single-process.

### Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `exit()` in ML code kills entire batch | Library calls `sys.exit()` or `exit()` on error; not caught by `except Exception` since `SystemExit` inherits `BaseException` | Patch `exit()` → `raise RuntimeError(...)` or `break` |
| `UnboundLocalError: mask_sharp` / `lm` | Face detector failed on some frames; variable never assigned | Wrap in try/except inside inference loop, skip video, log failure |
| Audio shorter than video (whisper index OOB) | Mismatch between audio duration and video frame count | Truncate output to audio length (`break` in feature loop), or pad audio with silence |
| `CUDA out of memory` | Model + batch too large for GPU VRAM | Reduce `--batch_size`, or switch to a GPU with more free VRAM |
| Jupyter token expired / connection refused | Server restarted or VPN disconnected | Re-read token from `kod.txt`, verify VPN is active |

### Restart After Failure

When generation dies mid-way:
1. Count completed outputs (`.mp4` files in output dir).
2. Build a list of remaining tasks (compare manifest against outputs).
3. Write a new config/manifest with only the remaining tasks.
4. Relaunch with the new config — existing outputs are preserved.
5. If the failure was caused by a code bug, patch the code first (see Common Errors).
