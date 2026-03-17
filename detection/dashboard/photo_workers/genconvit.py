#!/usr/bin/env python3
"""
GenConViT (CViT) single-image inference (runs in CViT venv on MIEM).

Usage: python genconvit.py <face_crop_path>
Output: prints PHOTO_RESULT:{json} to stdout
"""
import sys
import os
import json
import time

HOME = os.path.expanduser("~")
CVIT_DIR = os.path.join(HOME, "CViT")
CVIT_MODEL_DIR = os.path.join(CVIT_DIR, "model")
sys.path.insert(0, CVIT_MODEL_DIR)
sys.path.insert(0, CVIT_DIR)

import cv2
import numpy as np
import torch

WEIGHTS_PATH = os.path.join(CVIT_DIR, "weight", "cvit2_deepfake_detection_ep_50.pth")
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def main():
    image_path = sys.argv[1]
    t0 = time.time()

    try:
        from cvit import CViT

        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        model = CViT(
            image_size=224, patch_size=7, num_classes=2,
            dim=1024, depth=6, heads=8, mlp_dim=2048,
        )
        ckpt = torch.load(WEIGHTS_PATH, map_location="cpu")
        state_dict = ckpt["state_dict"] if "state_dict" in ckpt else ckpt
        model.load_state_dict(state_dict)
        model = model.to(device)
        model.eval()

        image = cv2.imread(image_path)
        if image is None:
            raise RuntimeError(f"Cannot read: {image_path}")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face = cv2.resize(rgb, (224, 224)).astype(np.float32) / 255.0
        face = (face - MEAN) / STD
        tensor = torch.from_numpy(face.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

        with torch.no_grad():
            output = model(tensor)
            probs = output.softmax(1)
            fake_score = float(probs[0, 0].item())  # class 0 = fake

        result = {
            "detector": "genconvit", "score": round(fake_score, 6),
            "label": "fake" if fake_score >= 0.5 else "real",
            "time": round(time.time() - t0, 2), "error": None,
        }
    except Exception as e:
        result = {
            "detector": "genconvit", "score": None, "label": None,
            "time": round(time.time() - t0, 2), "error": str(e)[:200],
        }

    print("PHOTO_RESULT:" + json.dumps(result))


if __name__ == "__main__":
    main()
