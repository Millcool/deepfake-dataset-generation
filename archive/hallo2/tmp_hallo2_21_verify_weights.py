import os
from pathlib import Path

repo=Path('/var/lib/ilanmironov@edu.hse.ru/hallo2')
paths=[
  'pretrained_models/hallo2/net.pth',
  'pretrained_models/hallo2/net_g.pth',
  'pretrained_models/audio_separator/Kim_Vocal_2.onnx',
  'pretrained_models/face_analysis/models/face_landmarker_v2_with_blendshapes.task',
  'pretrained_models/face_analysis/models/2d106det.onnx',
  'pretrained_models/face_analysis/models/1k3d68.onnx',
  'pretrained_models/face_analysis/models/scrfd_10g_bnkps.onnx',
  'pretrained_models/motion_module/mm_sd_v15_v2.ckpt',
  'pretrained_models/sd-vae-ft-mse/diffusion_pytorch_model.safetensors',
  'pretrained_models/stable-diffusion-v1-5/unet/diffusion_pytorch_model.safetensors',
  'pretrained_models/wav2vec/wav2vec2-base-960h/model.safetensors',
  'pretrained_models/realesrgan/RealESRGAN_x2plus.pth',
  'pretrained_models/facelib/parsing_parsenet.pth',
]

missing=[]
for p in paths:
  fp=repo/p
  if not fp.exists():
    missing.append(p)

print('missing_count', len(missing))
for p in missing:
  print('MISSING', p)

# size summary
pm=repo/'pretrained_models'
if pm.exists():
  total=0
  for f in pm.rglob('*'):
    if f.is_file():
      total += f.stat().st_size
  print('pretrained_models_total_gb', round(total/1024**3,2))