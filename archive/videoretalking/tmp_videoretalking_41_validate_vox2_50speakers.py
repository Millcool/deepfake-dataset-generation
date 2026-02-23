import subprocess

def sh(cmd):
    print(f"\n$ {cmd}")
    p = subprocess.run(["bash","-lc",cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(p.stdout)

vox='/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac'
sh('python3 - <<PY\nimport os\nvox="'+vox+'"\npersons=sorted([d for d in os.listdir(vox) if d.startswith("id") and os.path.isdir(os.path.join(vox,d))])\nfirst=persons[:50]\nprint("TOTAL_PERSONS",len(persons),"USING",len(first))\nbad=[]\nfor p in first:\n    clips=sorted([d for d in os.listdir(os.path.join(vox,p)) if os.path.isdir(os.path.join(vox,p,d))])\n    if len(clips)<4:\n        bad.append((p,len(clips)))\nprint("BAD",len(bad))\nfor x in bad[:20]:\n    print(x)\nPY')
