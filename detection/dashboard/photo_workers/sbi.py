#!/usr/bin/env python3
"""
SBI (Self-Blended Images, EfficientNet-B4) single-image inference.
Runs in SBI venv on MIEM.

Usage: python sbi.py <face_crop_path>
Output: prints PHOTO_RESULT:{json} to stdout
"""
import sys
import os
import json
import time

HOME = os.path.expanduser("~")
SBI_DIR = os.path.join(HOME, "SelfBlendedImages")
SBI_SRC = os.path.join(SBI_DIR, "src")
sys.path.insert(0, SBI_SRC)

import cv2
import numpy as np
import torch

WEIGHTS_PATH = os.path.join(SBI_DIR, "weights", "FFraw.tar")


def main():
    image_path = sys.argv[1]
    t0 = time.time()

    try:
        from model import Detector

        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        model = Detector()
        model = model.to(device)
        ckpt = torch.load(WEIGHTS_PATH, map_location=device)
        model.load_state_dict(ckpt["model"])
        model.eval()

        image = cv2.imread(image_path)
        if image is None:
            raise RuntimeError(f"Cannot read: {image_path}")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face = cv2.resize(rgb, (380, 380))
        # SBI expects uint8 → /255 inside forward, but we pass float
        tensor = torch.from_numpy(face.transpose(2, 0, 1)).unsqueeze(0).float().to(device)
        tensor = tensor / 255.0

        with torch.no_grad():
            output = model(tensor)
            probs = output.softmax(1)
            fake_score = float(probs[0, 1].item())  # class 1 = fake

        result = {
            "detector": "sbi", "score": round(fake_score, 6),
            "label": "fake" if fake_score >= 0.5 else "real",
            "time": round(time.time() - t0, 2), "error": None,
        }
    except Exception as e:
        result = {
            "detector": "sbi", "score": None, "label": None,
            "time": round(time.time() - t0, 2), "error": str(e)[:200],
        }

    print("PHOTO_RESULT:" + json.dumps(result))


if __name__ == "__main__":
    main()
