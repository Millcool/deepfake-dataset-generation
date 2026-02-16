# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Academic research project for generating large-scale synthetic deepfake video datasets (1000 videos each) using multiple face-swapping and portrait animation models. Part of HSE master's program (3rd semester). All heavy computation runs on a remote MIEM server via Jupyter API.

## Mandatory Rules

All rules in `AGENTS.md` are mandatory. Key points:
- **All work happens on the remote server** (`/var/lib/ilanmironov@edu.hse.ru/`). Do not run ML tasks locally.
- **Never delete files** without explicit user consent (any method: `rm`, Python, Jupyter API).
- **Never modify original source datasets** or pre-existing files in `shared/datasets/*`.
- **Never start 1000-video generation** without explicit user approval. Always follow the pipeline: smoke test -> preview -> approval -> full generation.
- Follow `REMOTE_SERVER_WORKFLOW.md` for all server interactions.

## Remote Execution

Remote code runs via `remote_exec.py`, which creates a Jupyter kernel session over WebSocket:

```bash
python remote_exec.py --base "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru" --token "$MIEM_TOKEN" --code-file script.py
```

Key details:
- Auth: `Authorization: token ...` header + `Origin: https://ws.miem3.vmnet.top`
- Must clear proxy env vars (`HTTP_PROXY`, `HTTPS_PROXY`, etc.) before connecting
- File management fallback: Jupyter Contents API (`GET/PUT /api/contents/{path}`)

## Architecture

### Generation Pipelines

Each model (LivePortrait, MuseTalk, Hallo2, SberSwap/GHOST) follows the same pattern:
1. Clone repo into `/var/lib/ilanmironov@edu.hse.ru/<repo_name>/`
2. Create venv, install deps, download weights
3. Smoke test (single inference)
4. Preview (1-2 videos, male+female) -> send to user
5. Full generation (1000 videos) after approval
6. Post-processing: rename, create reproducibility doc, upload to `shared/datasets/`

### Key Scripts (root-level, prefixed by pipeline name)

- `liveportrait__batch_generate.py` - Task orchestrator: builds source/target pairs by gender, distributes across 4 GPUs
- `liveportrait__gpu_worker.py` - Per-GPU worker: loads model once, processes all assigned tasks
- `liveportrait__run_single.py` - Single-pair inference wrapper
- `liveportrait__setup_liveportrait.py` - Environment setup (PyTorch, weights from HuggingFace)
- `remote_exec.py` - WebSocket-based remote code execution client
- `musetalk_hourly_status.py` - Polls remote generation status hourly
- `rename_resume_remote_payload.py` - Post-generation renaming from `fake_XXXX.mp4` to readable names
- `methodology__gender_division.py` - Gender classification using DeepFace/RetinaFace
- `methodology__audio_name.py` - Audio source mapping for audio-to-face pipelines

### Dataset Methodology

**Face-to-face:** Split by gender. Source videos taken from end of sorted list (999, 998...), targets in consecutive blocks of 20 from start. One source paired with its 20-target block.

**Audio-to-face:** 50 speakers x 4 audio clips x 5 repeats = 1000 videos. Formula: `person = i // 20`, `clip = (i % 20) // 5`.

### Dataset Naming Convention

Shared output path: `/var/lib/ilanmironov@edu.hse.ru/shared/datasets/<name>`
- Video + audio pipeline: `<RepoName>_FFpp_vox2`
- Video-only pipeline: `<RepoName>_FFpp`
- Audio-only pipeline: `<RepoName>_vox2`

### Subdirectories

- `sber/sber-swap/` - GHOST face-swap model (Sberbank AI). Has its own `requirements.txt` and model download script.
- `tmp_*.py` files - Incremental development/debugging scripts (160+). These document the research process step-by-step.

## Tech Stack

- Python 3.10+, PyTorch with CUDA 12.1, OpenCV, FFmpeg
- Models: LivePortrait, MuseTalk, Hallo2, SberSwap/GHOST, DeepFace
- Remote: Jupyter REST API + WebSocket, requests, websocket-client
- Data: pandas (manifests as CSV), insightface, HuggingFace Hub

## Post-Generation Checklist

1. Create reproducibility document (pipeline steps, data flow, issues, rerun requirements)
2. Upload 1000-video dataset to `shared/datasets/` on remote server
3. Do NOT mention the shared upload step inside the reproducibility document
4. Upload reproducibility doc + base files to GitLab only after user approval
