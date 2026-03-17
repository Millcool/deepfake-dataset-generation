#!/usr/bin/env python3
"""
Face detection using RetinaFace (runs in SBI venv on MIEM).
Detects the most prominent face, crops with margin, saves to output path.

Usage: python face_detect.py <image_path> <output_face_path> [margin]
Output: prints FACE_RESULT:{json} to stdout
"""
import sys
import os
import json
import time

import cv2
import numpy as np
import torch
from retinaface.pre_trained_models import get_model


def main():
    image_path = sys.argv[1]
    output_path = sys.argv[2]
    margin = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5

    t0 = time.time()

    image = cv2.imread(image_path)
    if image is None:
        print("FACE_RESULT:" + json.dumps({
            "detected": False, "error": f"Cannot read image: {image_path}",
            "time": round(time.time() - t0, 2)
        }))
        sys.exit(1)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    face_detector = get_model("resnet50_2020-07-20", max_size=1024, device=device)
    face_detector.eval()

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    with torch.no_grad():
        annotations = face_detector.predict_jsons(rgb)

    faces = [a for a in annotations if a.get("score", 0) > 0.5]

    if not faces:
        print("FACE_RESULT:" + json.dumps({
            "detected": False, "error": "No face detected",
            "time": round(time.time() - t0, 2)
        }))
        sys.exit(0)

    best = max(faces, key=lambda a: a.get("score", 0))
    bbox = best["bbox"]  # [x1, y1, x2, y2]
    x1, y1, x2, y2 = bbox
    bw, bh = x2 - x1, y2 - y1
    h, w = image.shape[:2]

    cx1 = max(0, int(x1 - bw * margin))
    cy1 = max(0, int(y1 - bh * margin))
    cx2 = min(w, int(x2 + bw * margin))
    cy2 = min(h, int(y2 + bh * margin))

    face_crop = image[cy1:cy2, cx1:cx2]
    cv2.imwrite(output_path, face_crop)

    print("FACE_RESULT:" + json.dumps({
        "detected": True,
        "bbox": [cx1, cy1, cx2, cy2],
        "confidence": round(best.get("score", 0), 4),
        "time": round(time.time() - t0, 2)
    }))


if __name__ == "__main__":
    main()
