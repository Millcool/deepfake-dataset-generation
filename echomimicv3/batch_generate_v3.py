#!/usr/bin/env python3
"""
EchoMimic V3 — batch_generate_v3.py
Main batch generation loop for 1000-video dataset.

Loads all models ONCE, then iterates through the manifest CSV,
generating one video per row. Skips already-existing outputs for
restart support. Logs timing stats to a JSONL file.

Usage:
  python batch_generate_v3.py \
      --start 0 --end 1000 --gpu 0 \
      --manifest path/to/manifest_1000.csv \
      --output-dir path/to/outputs

Designed to run for days under nohup via launch_gen1000.sh.
"""
import argparse
import csv
import json
import math
import os
import sys
import time
import traceback
import datetime

import numpy as np
import torch
from PIL import Image
from einops import rearrange

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="EchoMimic V3 batch generation")
parser.add_argument("--start", type=int, default=0, help="Start index (inclusive)")
parser.add_argument("--end", type=int, default=1000, help="End index (exclusive)")
parser.add_argument("--gpu", type=int, default=0, help="GPU id (used only for log messages; CUDA_VISIBLE_DEVICES should be set externally)")
parser.add_argument("--manifest", type=str, required=True, help="Path to manifest_1000.csv")
parser.add_argument("--output-dir", type=str, required=True, help="Output directory for generated videos")
parser.add_argument("--seed-base", type=int, default=42, help="Base seed; actual seed = seed_base + idx")
parser.add_argument("--max-video-length", type=int, default=81, help="Max video length in frames (default 81)")
parser.add_argument("--num-steps", type=int, default=8, help="Number of inference steps")
parser.add_argument("--fps", type=int, default=25, help="Output FPS")
args = parser.parse_args()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ts():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    print(f"[{ts()}] [GPU-{args.gpu}] {msg}", flush=True)


def loudness_norm(audio_array, sr=16000, lufs=-23):
    """Normalize audio loudness to target LUFS."""
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(audio_array)
    if abs(loudness) > 100:
        return audio_array
    return pyln.normalize.loudness(audio_array, loudness, lufs)


def get_audio_embed(mel_input, wav2vec_feature_extractor, audio_encoder, video_length, sr=16000, fps=25, device='cpu'):
    """Extract wav2vec2 audio embeddings."""
    audio_feature = np.squeeze(wav2vec_feature_extractor(mel_input, sampling_rate=sr).input_values)
    audio_feature = torch.from_numpy(audio_feature).float().to(device=device).unsqueeze(0)
    with torch.no_grad():
        embeddings = audio_encoder(audio_feature, seq_len=int(video_length), output_hidden_states=True)
    audio_emb = torch.stack(embeddings.hidden_states[1:], dim=1).squeeze(0)
    audio_emb = rearrange(audio_emb, "b s d -> s b d")
    return audio_emb.cpu().detach()


def get_sample_size(pil_img, sample_size):
    """Compute the computation resolution (h, w) aligned to 16px."""
    w, h = pil_img.size
    ori_a = w * h
    default_a = sample_size[0] * sample_size[1]
    if default_a < ori_a:
        ratio_a = math.sqrt(ori_a / sample_size[0] / sample_size[1])
        w = w / ratio_a // 16 * 16
        h = h / ratio_a // 16 * 16
    else:
        w = w // 16 * 16
        h = h // 16 * 16
    return [int(h), int(w)]


def format_eta(seconds):
    """Format seconds into a human-readable ETA string."""
    if seconds <= 0:
        return "0s"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    if h > 0:
        return f"{h}h{m:02d}m"
    return f"{m}m"


# ---------------------------------------------------------------------------
# Change to the echomimic_v3 repo dir (needed for config/config.yaml and src/)
# ---------------------------------------------------------------------------
BASE = '/var/lib/ilanmironov@edu.hse.ru/echomimic_v3'
os.chdir(BASE)
sys.path.insert(0, '.')

# ---------------------------------------------------------------------------
# Model paths
# ---------------------------------------------------------------------------
MODEL_NAME       = os.path.join(BASE, 'pretrained_weights', 'Wan2.1-Fun-V1.1-1.3B-InP')
TRANSFORMER_PATH = os.path.join(BASE, 'pretrained_weights', 'EchoMimicV3', 'echomimicv3-flash-pro', 'diffusion_pytorch_model.safetensors')
WAV2VEC_DIR      = os.path.join(BASE, 'pretrained_weights', 'chinese-wav2vec2-base')
CONFIG_PATH      = 'config/config.yaml'
SAMPLE_SIZE      = [768, 768]
WEIGHT_DTYPE     = torch.bfloat16

# ---------------------------------------------------------------------------
# Imports from echomimic_v3 repo (after chdir + sys.path)
# ---------------------------------------------------------------------------
log("Importing EchoMimic V3 modules...")
from diffusers import FlowMatchEulerDiscreteScheduler  # noqa: E402
from omegaconf import OmegaConf  # noqa: E402
from transformers import AutoTokenizer, Wav2Vec2FeatureExtractor  # noqa: E402
from safetensors.torch import load_file  # noqa: E402
import librosa  # noqa: E402
import pyloudnorm as pyln  # noqa: E402
from moviepy import VideoFileClip, AudioFileClip  # noqa: E402

from src.wav2vec2 import Wav2Vec2Model  # noqa: E402
from src.dist import set_multi_gpus_devices  # noqa: E402
from src.wan_vae import AutoencoderKLWan  # noqa: E402
from src.wan_image_encoder import CLIPModel  # noqa: E402
from src.wan_text_encoder import WanT5EncoderModel  # noqa: E402
from src.wan_transformer3d_audio_2512 import WanTransformerAudioMask3DModel as WanTransformer  # noqa: E402
from src.pipeline_wan_fun_inpaint_audio_2512 import WanFunInpaintAudioPipeline  # noqa: E402
from src.utils import filter_kwargs, get_image_to_video_latent2, save_videos_grid  # noqa: E402
from src.fm_solvers_unipc import FlowUniPCMultistepScheduler  # noqa: E402
from src.cache_utils import get_teacache_coefficients  # noqa: E402


# ===================================================================
# LOAD ALL MODELS (ONCE)
# ===================================================================
log("=" * 60)
log("EchoMimic V3  batch_generate_v3.py")
log(f"  Range: [{args.start}, {args.end})  GPU: {args.gpu}")
log(f"  Steps: {args.num_steps}  FPS: {args.fps}  MaxFrames: {args.max_video_length}")
log(f"  Manifest: {args.manifest}")
log(f"  Output:   {args.output_dir}")
log("=" * 60)
log("Loading models...")

t_load_start = time.time()

# 1. Audio encoder (wav2vec2) — stays on CPU
audio_encoder = Wav2Vec2Model.from_pretrained(
    WAV2VEC_DIR, local_files_only=True, attn_implementation="eager"
).to('cpu')
audio_encoder.feature_extractor._freeze_parameters()
wav2vec_feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
    WAV2VEC_DIR, local_files_only=True
)
log("  Audio encoder (wav2vec2) loaded on CPU")

# 2. Device setup
device = set_multi_gpus_devices(1, 1)
config = OmegaConf.load(CONFIG_PATH)

# 3. Transformer + Flash-Pro weights
transformer = WanTransformer.from_pretrained(
    os.path.join(MODEL_NAME, config['transformer_additional_kwargs'].get('transformer_subpath', 'transformer')),
    transformer_additional_kwargs=OmegaConf.to_container(config['transformer_additional_kwargs']),
    low_cpu_mem_usage=True,
    torch_dtype=WEIGHT_DTYPE,
)
state_dict = load_file(TRANSFORMER_PATH)
m, u = transformer.load_state_dict(state_dict, strict=False)
log(f"  Transformer loaded (missing={len(m)}, unexpected={len(u)})")

# 4. VAE
vae = AutoencoderKLWan.from_pretrained(
    os.path.join(MODEL_NAME, config['vae_kwargs'].get('vae_subpath', 'vae')),
    additional_kwargs=OmegaConf.to_container(config['vae_kwargs']),
).to(WEIGHT_DTYPE)
log("  VAE loaded")

# 5. Tokenizer + Text encoder
tokenizer = AutoTokenizer.from_pretrained(
    os.path.join(MODEL_NAME, config['text_encoder_kwargs'].get('tokenizer_subpath', 'tokenizer')),
)
text_encoder = WanT5EncoderModel.from_pretrained(
    os.path.join(MODEL_NAME, config['text_encoder_kwargs'].get('text_encoder_subpath', 'text_encoder')),
    additional_kwargs=OmegaConf.to_container(config['text_encoder_kwargs']),
    low_cpu_mem_usage=True,
    torch_dtype=WEIGHT_DTYPE,
).eval()
log("  Text encoder loaded")

# 6. CLIP image encoder
clip_image_encoder = CLIPModel.from_pretrained(
    os.path.join(MODEL_NAME, config['image_encoder_kwargs'].get('image_encoder_subpath', 'image_encoder')),
).to(WEIGHT_DTYPE).eval()
log("  CLIP image encoder loaded")

# 7. Scheduler (FlowUniPC with shift=1)
scheduler = FlowUniPCMultistepScheduler(
    **filter_kwargs(FlowUniPCMultistepScheduler, {
        **OmegaConf.to_container(config['scheduler_kwargs']),
        'shift': 1
    })
)

# 8. Assemble pipeline
pipeline = WanFunInpaintAudioPipeline(
    transformer=transformer,
    vae=vae,
    tokenizer=tokenizer,
    text_encoder=text_encoder,
    scheduler=scheduler,
    clip_image_encoder=clip_image_encoder,
)

# 9. Sequential CPU offload (one GPU, moves layers on/off as needed)
pipeline.enable_sequential_cpu_offload(gpu_id=0)
log("  Sequential CPU offload enabled")

# 10. TeaCache acceleration
coefficients = get_teacache_coefficients(MODEL_NAME)
if coefficients is not None:
    pipeline.transformer.enable_teacache(
        coefficients, args.num_steps, 0.1, num_skip_start_steps=5, offload=False
    )
    log("  TeaCache enabled (threshold=0.1, skip_start=5)")
else:
    log("  WARNING: TeaCache coefficients not found, running without TeaCache")

t_load_end = time.time()
log(f"  All models loaded in {t_load_end - t_load_start:.1f}s")


# ===================================================================
# READ MANIFEST
# ===================================================================
log(f"\nReading manifest: {args.manifest}")
with open(args.manifest, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    all_rows = list(reader)

log(f"  Manifest has {len(all_rows)} rows, processing [{args.start}, {args.end})")

# Validate range
if args.start < 0 or args.end > len(all_rows) or args.start >= args.end:
    log(f"ERROR: invalid range [{args.start}, {args.end}) for manifest with {len(all_rows)} rows")
    sys.exit(1)

# Ensure output directory exists
os.makedirs(args.output_dir, exist_ok=True)

# JSONL log file for monitoring
jsonl_path = os.path.join(
    os.path.dirname(args.output_dir) or '.',
    'logs',
    f'gen1000_gpu{args.gpu}_{args.start}-{args.end}.jsonl'
)
os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)


# ===================================================================
# MAIN GENERATION LOOP
# ===================================================================
done = 0
skipped = 0
failed = 0
total_gen_time = 0.0
task_count = args.end - args.start

log(f"\n{'=' * 60}")
log(f"GENERATION START: {task_count} tasks")
log(f"{'=' * 60}")

t_gen_start = time.time()

for task_idx in range(args.start, args.end):
    row = all_rows[task_idx]
    idx = int(row['idx'])
    output_name = row['output_name']
    output_path = os.path.join(args.output_dir, output_name)

    # ----- Skip existing -----
    if os.path.isfile(output_path) and os.path.getsize(output_path) > 10000:
        skipped += 1
        continue

    t_task_start = time.time()

    try:
        # ----- Load and validate image -----
        frame_path = row['frame_640x480']
        if not os.path.isfile(frame_path):
            raise FileNotFoundError(f"Frame not found: {frame_path}")

        ref_image = Image.open(frame_path).convert('RGB')
        sample_size_0, sample_size_1 = get_sample_size(ref_image, SAMPLE_SIZE)

        # ----- Load and process audio -----
        audio_wav_path = row['audio_wav']
        if not os.path.isfile(audio_wav_path):
            raise FileNotFoundError(f"Audio not found: {audio_wav_path}")

        audio_clip = AudioFileClip(audio_wav_path)
        audio_duration = audio_clip.duration

        # Video length: min of audio_duration*fps and max_video_length,
        # aligned to VAE temporal compression ratio
        video_length = min(int(audio_duration * args.fps), args.max_video_length)
        video_length = int(
            (video_length - 1) // vae.config.temporal_compression_ratio
            * vae.config.temporal_compression_ratio
        ) + 1

        if video_length < 5:
            raise ValueError(f"Video too short: {video_length} frames from {audio_duration:.2f}s audio")

        # Audio embeddings via wav2vec2
        mel_input, sr = librosa.load(audio_wav_path, sr=16000)
        mel_input = loudness_norm(mel_input, sr)
        mel_input = mel_input[:int(video_length / args.fps * sr)]

        audio_feature_wav2vec = get_audio_embed(
            mel_input, wav2vec_feature_extractor, audio_encoder, video_length
        )
        audio_embeds = audio_feature_wav2vec.to(device=device, dtype=WEIGHT_DTYPE)

        # Temporal windowing (5-frame context window)
        indices = (torch.arange(5) - 2) * 1
        center_indices = torch.arange(0, video_length, 1).unsqueeze(1) + indices.unsqueeze(0)
        center_indices = torch.clamp(center_indices, min=0, max=audio_embeds.shape[0] - 1)
        audio_embeds = audio_embeds[center_indices].unsqueeze(0).to(device=device)

        # ----- Prepare input tensors -----
        ref_start = np.array(ref_image)
        validation_image_start = Image.fromarray(ref_start).convert('RGB')
        input_video, input_video_mask, clip_image = get_image_to_video_latent2(
            validation_image_start, None,
            video_length=video_length,
            sample_size=[sample_size_0, sample_size_1]
        )

        # ----- Run pipeline -----
        generator = torch.Generator(device=device).manual_seed(args.seed_base + idx)

        with torch.no_grad():
            sample = pipeline(
                "A person is speaking.",
                num_frames=video_length,
                negative_prompt="Gesture is bad. Gesture is unclear. Strange and twisted hands. Bad hands.",
                audio_embeds=audio_embeds,
                audio_scale=1.0,
                ip_mask=None,
                use_un_ip_mask=False,
                height=sample_size_0,
                width=sample_size_1,
                generator=generator,
                neg_scale=1.0,
                neg_steps=0,
                use_dynamic_cfg=False,
                use_dynamic_acfg=False,
                guidance_scale=6.0,
                audio_guidance_scale=3.0,
                num_inference_steps=args.num_steps,
                video=input_video,
                mask_video=input_video_mask,
                clip_image=clip_image,
                cfg_skip_ratio=0.0,
                shift=5.0,
            ).videos

        # ----- Save video (temp without audio, then mux audio) -----
        tmp_path = output_path.replace('.mp4', '_tmp.mp4')
        save_videos_grid(sample[:, :, :video_length], tmp_path, fps=args.fps)

        video_clip_out = VideoFileClip(tmp_path)
        audio_trimmed = audio_clip.subclipped(0, video_length / args.fps)
        video_clip_out = video_clip_out.with_audio(audio_trimmed)
        video_clip_out.write_videofile(
            output_path, codec="libx264", audio_codec="aac",
            threads=2, logger=None  # suppress moviepy progress bars
        )

        # Cleanup temp file
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)

        # Close moviepy clips to release file handles
        try:
            video_clip_out.close()
        except Exception:
            pass
        try:
            audio_clip.close()
        except Exception:
            pass

        t_task_end = time.time()
        elapsed = t_task_end - t_task_start
        file_size = os.path.getsize(output_path)
        done += 1
        total_gen_time += elapsed

        # ----- Progress and ETA -----
        processed = done + failed
        remaining = task_count - skipped - processed
        avg_time = total_gen_time / processed if processed > 0 else elapsed
        eta_seconds = avg_time * remaining

        log(f"  [{done + skipped + failed}/{task_count}] idx={idx} "
            f"OK {elapsed:.0f}s ({elapsed / 60:.1f}min) "
            f"size={file_size / 1024:.0f}KB "
            f"frames={video_length} res={sample_size_1}x{sample_size_0} "
            f"ETA={format_eta(eta_seconds)} "
            f"(done={done} skip={skipped} fail={failed})")

        # ----- JSONL log entry -----
        log_entry = {
            "ts": ts(),
            "idx": idx,
            "status": "ok",
            "elapsed_s": round(elapsed, 1),
            "file_size_bytes": file_size,
            "video_length": video_length,
            "resolution": f"{sample_size_1}x{sample_size_0}",
            "output": output_name,
            "done": done,
            "skipped": skipped,
            "failed": failed,
        }
        with open(jsonl_path, 'a', encoding='utf-8') as jf:
            jf.write(json.dumps(log_entry) + '\n')

    except Exception as e:
        failed += 1
        t_task_end = time.time()
        elapsed = t_task_end - t_task_start
        total_gen_time += elapsed

        error_msg = f"{type(e).__name__}: {str(e)[:300]}"
        log(f"  [{done + skipped + failed}/{task_count}] idx={idx} "
            f"FAIL {elapsed:.0f}s — {error_msg}")

        # Log traceback to JSONL
        log_entry = {
            "ts": ts(),
            "idx": idx,
            "status": "error",
            "elapsed_s": round(elapsed, 1),
            "error": error_msg,
            "traceback": traceback.format_exc()[-500:],
            "done": done,
            "skipped": skipped,
            "failed": failed,
        }
        with open(jsonl_path, 'a', encoding='utf-8') as jf:
            jf.write(json.dumps(log_entry) + '\n')

        # Cleanup any leftover temp file
        tmp_path = output_path.replace('.mp4', '_tmp.mp4')
        if os.path.isfile(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        # Close audio_clip if it was opened
        try:
            audio_clip.close()
        except Exception:
            pass

        # If we get a CUDA OOM, it's best to exit rather than corrupt state
        if 'CUDA out of memory' in str(e) or 'OutOfMemoryError' in type(e).__name__:
            log("FATAL: CUDA OOM — exiting to prevent GPU corruption")
            sys.exit(2)


# ===================================================================
# SUMMARY
# ===================================================================
t_gen_end = time.time()
total_elapsed = t_gen_end - t_gen_start
total_with_load = t_gen_end - t_load_start

log(f"\n{'=' * 60}")
log(f"GENERATION COMPLETE")
log(f"{'=' * 60}")
log(f"  Range:       [{args.start}, {args.end})")
log(f"  Done:        {done}")
log(f"  Skipped:     {skipped} (already existed)")
log(f"  Failed:      {failed}")
log(f"  Total tasks: {task_count}")
log(f"  Generation time: {total_elapsed / 3600:.1f}h ({total_elapsed:.0f}s)")
log(f"  Total time (incl. model loading): {total_with_load / 3600:.1f}h")
if done > 0:
    avg = total_gen_time / (done + failed) if (done + failed) > 0 else 0
    log(f"  Avg per video: {avg:.0f}s ({avg / 60:.1f}min)")
log(f"  JSONL log: {jsonl_path}")

# Count actual output files
output_files = [f for f in os.listdir(args.output_dir) if f.endswith('.mp4')]
log(f"  Output files: {len(output_files)} in {args.output_dir}")
log(f"{'=' * 60}")
