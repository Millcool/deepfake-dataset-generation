import subprocess

def sh(cmd: str):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

vox='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac'
sh('python3 - <<PY\nimport os, subprocess, heapq\nvox="'+vox+'"\nheap=[]\ncount=0\nfor root,_,files in os.walk(vox):\n    for fn in files:\n        if not fn.endswith(".m4a"):\n            continue\n        path=os.path.join(root,fn)\n        try:\n            out=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path], text=True).strip()\n            dur=float(out)\n        except Exception:\n            continue\n        count+=1\n        if len(heap)<20:\n            heapq.heappush(heap,(dur,path))\n        else:\n            if dur>heap[0][0]:\n                heapq.heapreplace(heap,(dur,path))\nprint("FILES",count)\nfor dur,path in sorted(heap, reverse=True):\n    print(f"{dur:.3f}",path)\nPY')
