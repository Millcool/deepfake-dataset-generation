#!/usr/bin/env python3
"""
CLIP-DFDet (deepfake-detection, TorchScript CLIP ViT-L/14) single-image inference.
No face detection needed — works on full frame.
Runs in deepfake-detection venv on MIEM.

Usage: python clip_dfdet.py <image_path>
Output: prints PHOTO_RESULT:{json} to stdout
"""
import sys
import os
import json
import time

import cv2
import numpy as np
import torch
from PIL import Image

HOME = os.path.expanduser("~")
CLIP_DIR = os.path.join(HOME, "deepfake-detection")
WEIGHTS_PATH = os.path.join(CLIP_DIR, "weights", "model.torchscript")


def main():
    image_path = sys.argv[1]
    t0 = time.time()

    try:
        from transformers import CLIPImageProcessor

        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        model = torch.jit.load(WEIGHTS_PATH, map_location=device)
        model.eval()

        processor = CLIPImageProcessor.from_pretrained("openai/clip-vit-large-patch14")

        image = cv2.imread(image_path)
        if image is None:
            raise RuntimeError(f"Cannot read: {image_path}")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        inputs = processor(images=[pil_img], return_tensors="pt")
        pixel_values = inputs["pixel_values"].to(device)

        with torch.no_grad():
            logits = model(pixel_values)  # (1, 2) [real, fake]
            probs = torch.softmax(logits.float(), dim=-1)
            fake_score = float(probs[0, 1].item())

        result = {
            "detector": "clip_dfdet", "score": round(fake_score, 6),
            "label": "fake" if fake_score >= 0.5 else "real",
            "time": round(time.time() - t0, 2), "error": None,
        }
    except Exception as e:
        result = {
            "detector": "clip_dfdet", "score": None, "label": None,
            "time": round(time.time() - t0, 2), "error": str(e)[:200],
        }

    print("PHOTO_RESULT:" + json.dumps(result))


if __name__ == "__main__":
    main()
