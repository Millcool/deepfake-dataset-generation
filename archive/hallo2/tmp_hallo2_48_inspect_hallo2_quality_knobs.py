import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash", "-lc", cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

repo = "/var/lib/ilanmironov@edu.hse.ru/hallo2"

sh(f"cd {repo} && echo '=== configs/inference/long.yaml (head) ===' && sed -n '1,260p' configs/inference/long.yaml")
sh(
    f"cd {repo} && echo '=== inference_long.py args ===' && "
    "(command -v rg >/dev/null 2>&1 && rg -n \"argparse|pose_weight|face_weight|lip_weight|face_expand_ratio|inference_steps|guidance|cfg|scale|fps|resolution|image_size|sample\" scripts/inference_long.py | head -n 220) "
    "|| (grep -nE \"argparse|pose_weight|face_weight|lip_weight|face_expand_ratio|inference_steps|guidance|cfg|scale|fps|resolution|image_size|sample\" scripts/inference_long.py | head -n 220)"
)
sh(
    f"cd {repo} && echo '=== long.yaml key lines ===' && "
    "(command -v rg >/dev/null 2>&1 && rg -n \"inference_steps|guidance|cfg|scale|fps|resolution|image_size|seed|face_expand_ratio|pose_weight|face_weight|lip_weight|audio\" configs/inference/long.yaml) "
    "|| (grep -nE \"inference_steps|guidance|cfg|scale|fps|resolution|image_size|seed|face_expand_ratio|pose_weight|face_weight|lip_weight|audio\" configs/inference/long.yaml)"
)

