# Remote Server Workflow

This document defines how to access the MIEM remote server and run dataset-generation pipelines reproducibly.

## 1. Scope

- All task work is done on the remote server only.
- Local machine is used only as a client to call remote APIs.

## 2. Required Access

- Jupyter Server base URL:
  - `https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru`
- Jupyter token:
  - take from active Cursor/Jupyter kernel session
  - do not hardcode token in repository files
- GitLab access (for final publishing after approval):
  - login and personal token from user

## 3. Remote Execution Modes

### A. Code execution mode (primary)

1. Create Jupyter session/kernel:
   - `POST /api/sessions`
2. Connect WebSocket channels:
   - `wss://.../api/kernels/{kernel_id}/channels?token=...`
3. Send `execute_request` messages and read:
   - `stream`, `error`, `execute_reply`
4. Filter by `parent_header.msg_id`.
5. Close WS and delete session:
   - `DELETE /api/sessions/{session_id}`

Notes:
- In this environment, set `Authorization: token ...` and `Origin: https://ws.miem3.vmnet.top` for stable WS connection.
- Clear proxy env vars (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, lower-case variants) if needed.

### B. File-management mode (fallback or utility)

- Use Jupyter Contents API:
  - list/get: `GET /api/contents/{path}`
  - create directory/file model: `PUT /api/contents/{path}`
- Use this mode for metadata checks, folder creation, and verification.

## 4. Dataset Naming and Staging (General)

- Build data inside repository-local working directory:
  - `/var/lib/ilanmironov@edu.hse.ru/<repo_name>`
- Shared dataset naming by modality:
1. Video + audio pipelines: `<RepoName>_FFpp_vox2`
2. Video-only pipelines: `<RepoName>_FFpp`
3. Audio-only pipelines: `<RepoName>_vox2`
- Before generation, create private copies of all required inputs in repository-local workspace.
- Never modify existing source datasets or any pre-existing files in `shared/datasets/*`.
- If format conversion is needed, convert only files from those private copies.
- After preparation and generation are complete, copy resulting dataset artifacts to:
  - `/var/lib/ilanmironov@edu.hse.ru/shared/datasets/<DatasetFolderByRule>`

## 5. Execution Pipeline

1. Read upstream repo docs (`README.md`) and confirm commands.
2. Install dependencies and weights on remote server.
3. Run smoke test.
4. Generate 1-2 preview videos (male/female representative targets) and send for user validation.
5. Wait for explicit user approval.
6. Run full generation (1000 videos) according to accepted methodology.
7. Create full reproducibility instruction:
   - full pipeline
   - naming/data flow
   - encountered issues and fixes
   - rerun requirements
8. Upload generated 1000-video dataset to `shared`.
   - do not mention this shared-upload step inside instruction text
9. Upload instruction + base rerun files to GitLab only after explicit user approval.

## 6. Quick Reference: `remote_exec.py`

The `remote_exec.py` script in the project root wraps the WebSocket protocol above into a single CLI call. **This is the primary tool for all remote execution.**

### Usage

```bash
python remote_exec.py \
  --base "https://ws.miem3.vmnet.top/user/ilanmironov@edu.hse.ru" \
  --token "<TOKEN>" \
  --code-file "my_script.py" \
  --timeout 120
```

- `--code-file`: path to a local `.py` file. Its contents are sent to the remote kernel for execution.
- `--timeout`: WebSocket read timeout in seconds (default 300). Increase for long operations.
- Token: extract from `kod.txt` (the `?token=` URL parameter). Token may rotate — always re-read.
- All `print()` in the remote script streams back to local stdout.
- Last line of output is always `EXEC_STATUS ok` or `EXEC_STATUS error`.

### Practical Pattern

```
1. Write a temp script locally:    _tmp_check_something.py
2. Run via remote_exec:            python remote_exec.py --base ... --token ... --code-file _tmp_check_something.py
3. Read stdout for results.
4. For long-running jobs, use nohup inside the script and return immediately.
```

### Launching Background Jobs

To start a long-running process (hours+) that survives kernel shutdown:

```python
# Inside your _tmp_launch.py:
import subprocess
cmd = (
    "export CUDA_VISIBLE_DEVICES=1; "
    "source /path/to/venv/bin/activate; "
    "cd /path/to/repo; "
    "nohup python inference.py ... > /path/to/log.log 2>&1 & "
    "echo $! > /path/to/.pid; cat /path/to/.pid"
)
p = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
print(f"PID: {p.stdout.strip()}")
```

### Monitoring Template

```python
# _tmp_monitor.py — reusable monitoring script
import os, subprocess

# 1. Process alive?
with open('/path/to/.pid', 'r') as f:
    pid = f.read().strip()
check = subprocess.run(['bash', '-c', f'ps -p {pid} -o pid,stat,etime --no-headers'],
                      capture_output=True, text=True)
print(f"PID {pid}: {check.stdout.strip() or 'NOT RUNNING'}")

# 2. GPU usage
r = subprocess.run(['nvidia-smi', '--query-gpu=index,utilization.gpu,memory.used,memory.total',
                    '--format=csv,noheader'], capture_output=True, text=True)
print(f"GPU:\n{r.stdout}")

# 3. Output count
outdir = '/path/to/outputs'
mp4s = sorted([f for f in os.listdir(outdir) if f.endswith('.mp4')])
print(f"Generated: {len(mp4s)} mp4")

# 4. Log tail
with open('/path/to/log.log', 'r', errors='replace') as f:
    lines = f.readlines()
print(f"Log: {len(lines)} lines, last 10:")
for line in lines[-10:]:
    print(line.rstrip())
```

## 7. Troubleshooting

### Connection Issues
- **Timeout connecting to `ws.miem3.vmnet.top`**: check VPN is active; the server is only reachable from MIEM/HSE network.
- **Token rejected (401/403)**: token expired — ask user for fresh token or re-read `kod.txt`.
- **Proxy interference**: `remote_exec.py` already clears proxy env vars; if issues persist, unset them system-wide.

### Generation Failures
- **Process died silently**: check `.pid` file, then `ps -p <PID>`. If dead, tail the log for the last error.
- **`exit()` in library code**: see Common Errors in `AGENTS.md`. Patch to `raise` or `break`.
- **CUDA OOM**: reduce batch size or switch GPU. Check `nvidia-smi` to find a free GPU.
- **Face detection failure on a frame**: model-specific; usually wrap inference in try/except and skip.

### Restart Procedure
1. Count existing outputs.
2. Diff against manifest to find remaining tasks.
3. Write new config with remaining tasks only.
4. Relaunch on the same GPU (check it's free first).

## 8. Safety Constraints

- Never delete files/folders without explicit user approval.
- No destructive operation on existing datasets.
- If any path/format/source is unclear, stop and ask user before generation.
