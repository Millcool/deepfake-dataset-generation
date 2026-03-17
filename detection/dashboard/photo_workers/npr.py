#!/usr/bin/env python3
"""
NPR (Neighboring Pixel Relationships, ResNet50) single-image inference.
No face detection needed — works on full frame.
Runs in NPR venv on MIEM.

Usage: python npr.py <image_path>
Output: prints PHOTO_RESULT:{json} to stdout
"""
import sys
import os
import json
import time

HOME = os.path.expanduser("~")
NPR_DIR = os.path.join(HOME, "NPR-DeepfakeDetection")
sys.path.insert(0, NPR_DIR)

import cv2
import numpy as np
import torch

WEIGHTS_PATH = os.path.join(NPR_DIR, "NPR.pth")
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def main():
    image_path = sys.argv[1]
    t0 = time.time()

    try:
        from networks.resnet import resnet50

        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        model = resnet50(num_classes=1)
        state_dict = torch.load(WEIGHTS_PATH, map_location="cpu")
        if isinstance(state_dict, dict) and "model" in state_dict:
            state_dict = state_dict["model"]
        clean_sd = {}
        for k, v in state_dict.items():
            clean_key = k.replace("module.", "") if k.startswith("module.") else k
            clean_sd[clean_key] = v
        model.load_state_dict(clean_sd)
        model = model.to(device)
        model.eval()

        image = cv2.imread(image_path)
        if image is None:
            raise RuntimeError(f"Cannot read: {image_path}")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(rgb, (256, 256)).astype(np.float32) / 255.0
        frame = (frame - MEAN) / STD
        tensor = torch.from_numpy(frame.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

        with torch.no_grad():
            logits = model(tensor)
            score = float(logits.sigmoid().item())

        result = {
            "detector": "npr", "score": round(score, 6),
            "label": "fake" if score >= 0.5 else "real",
            "time": round(time.time() - t0, 2), "error": None,
        }
    except Exception as e:
        result = {
            "detector": "npr", "score": None, "label": None,
            "time": round(time.time() - t0, 2), "error": str(e)[:200],
        }

    print("PHOTO_RESULT:" + json.dumps(result))


if __name__ == "__main__":
    main()
