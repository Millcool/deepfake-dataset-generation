import subprocess

script = r"""
set -euo pipefail
ROOT=/var/lib/ilanmironov@edu.hse.ru
REPO=$ROOT/musetalk
WORK=$REPO/workspace/preview_inputs
VIDEOS_SRC=$ROOT/shared/datasets/Wav2Lip_FFpp_vox2/real_videos
AUDIO_SRC=$ROOT/shared/datasets/Wav2Lip_FFpp_vox2/real_audio

mkdir -p $WORK/videos $WORK/audio_m4a $WORK/audio_wav $REPO/results/preview

# Copy two target videos into repository-local workspace
cp -f $VIDEOS_SRC/000.mp4 $WORK/videos/000.mp4
cp -f $VIDEOS_SRC/001.mp4 $WORK/videos/001.mp4

# Pick two audio samples from the first sorted speaker and first two sorted clips
speaker=$(ls -1 $AUDIO_SRC | sort | head -n 1)
clip1=$(ls -1 $AUDIO_SRC/$speaker | sort | sed -n '1p')
clip2=$(ls -1 $AUDIO_SRC/$speaker | sort | sed -n '2p')
file1=$(ls -1 $AUDIO_SRC/$speaker/$clip1 | sort | head -n 1)
file2=$(ls -1 $AUDIO_SRC/$speaker/$clip2 | sort | head -n 1)

cp -f $AUDIO_SRC/$speaker/$clip1/$file1 $WORK/audio_m4a/audio_0.m4a
cp -f $AUDIO_SRC/$speaker/$clip2/$file2 $WORK/audio_m4a/audio_1.m4a

# Convert only copied audio files
ffmpeg -y -v warning -i $WORK/audio_m4a/audio_0.m4a -ar 16000 -ac 1 $WORK/audio_wav/audio_0.wav
ffmpeg -y -v warning -i $WORK/audio_m4a/audio_1.m4a -ar 16000 -ac 1 $WORK/audio_wav/audio_1.wav

cat > $REPO/configs/inference/preview_user.yaml << 'YAML'
task_0:
  video_path: "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/preview_inputs/videos/000.mp4"
  audio_path: "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/preview_inputs/audio_wav/audio_0.wav"
  result_name: "preview_000_audio0.mp4"

task_1:
  video_path: "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/preview_inputs/videos/001.mp4"
  audio_path: "/var/lib/ilanmironov@edu.hse.ru/musetalk/workspace/preview_inputs/audio_wav/audio_1.wav"
  result_name: "preview_001_audio1.mp4"
YAML

echo "speaker=$speaker"
echo "clip1=$clip1 file1=$file1"
echo "clip2=$clip2 file2=$file2"
echo "preview_config=$REPO/configs/inference/preview_user.yaml"

rm -f $REPO/.preview_exit
LOG=$REPO/preview_generation.log
CMD='export MPLBACKEND=Agg; source /var/lib/ilanmironov@edu.hse.ru/venvs/musetalk/bin/activate; cd /var/lib/ilanmironov@edu.hse.ru/musetalk; python -m scripts.inference --inference_config configs/inference/preview_user.yaml --result_dir results/preview --unet_model_path models/musetalkV15/unet.pth --unet_config models/musetalkV15/musetalk.json --version v15 --gpu_id 0 --use_float16 --batch_size 8; echo $? > /var/lib/ilanmironov@edu.hse.ru/musetalk/.preview_exit'
nohup bash -lc "$CMD" > "$LOG" 2>&1 &
echo "preview_pid=$!"
echo "preview_log=$LOG"
"""

p = subprocess.run(["bash", "-lc", script], capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
print("exit", p.returncode)
