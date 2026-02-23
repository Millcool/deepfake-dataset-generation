# LivePortrait setup: install deps and download weights. Run: python setup_liveportrait.py
import os, subprocess, sys
home = os.path.expanduser("~")
log_path = os.path.join(home, "liveportrait", "setup_log.txt")
def log(s):
    with open(log_path, "a") as f:
        f.write(s + "\n")
    print(s)

log("=== LivePortrait setup started ===")
pip = os.path.join(home, "venvs", "liveportrait", "bin", "pip")
python = os.path.join(home, "venvs", "liveportrait", "bin", "python")
repo = os.path.join(home, "liveportrait")

# 1) PyTorch + CUDA
log("Installing PyTorch...")
r = subprocess.run([pip, "install", "torch", "torchvision", "--index-url", "https://download.pytorch.org/whl/cu121"],
    capture_output=True, text=True, timeout=600)
log("torch install: " + str(r.returncode) + (" " + r.stderr[:200] if r.returncode != 0 else ""))

# 2) requirements_base
log("Installing requirements_base...")
r = subprocess.run([pip, "install", "-r", os.path.join(repo, "requirements_base.txt")],
    capture_output=True, text=True, timeout=300)
log("base: " + str(r.returncode))

# 3) requirements
log("Installing requirements.txt...")
r = subprocess.run([pip, "install", "-r", os.path.join(repo, "requirements.txt")],
    capture_output=True, text=True, timeout=300)
log("main: " + str(r.returncode))

# 4) Weights from HuggingFace (git lfs clone)
pw = os.path.join(repo, "pretrained_weights")
if os.path.isdir(pw) and any(os.path.isfile(os.path.join(pw, f)) for r, d, files in os.walk(pw) for f in files):
    log("pretrained_weights already has files, skip download")
else:
    log("Downloading weights from HuggingFace...")
    tmp = os.path.join(home, "liveportrait", "temp_pw")
    if os.path.isdir(tmp):
        import shutil
        shutil.rmtree(tmp)
    r = subprocess.run(["git", "clone", "https://huggingface.co/KwaiVGI/LivePortrait", tmp],
        capture_output=True, text=True, timeout=300, cwd=home)
    log("hf clone: " + str(r.returncode) + (" " + r.stderr[:300] if r.returncode != 0 else ""))
    if r.returncode == 0 and os.path.isdir(os.path.join(tmp, "pretrained_weights")):
        import shutil
        for x in os.listdir(os.path.join(tmp, "pretrained_weights")):
            src = os.path.join(tmp, "pretrained_weights", x)
            dst = os.path.join(pw, x)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        shutil.rmtree(tmp)
        log("Weights copied to pretrained_weights")
    else:
        log("HuggingFace clone failed or no pretrained_weights; check manually")

# Verify
r = subprocess.run([python, "-c", "import torch; print(torch.__version__, torch.cuda.is_available())"], capture_output=True, text=True, timeout=10)
log("Verify: " + (r.stdout or r.stderr))
log("=== Setup finished ===")
