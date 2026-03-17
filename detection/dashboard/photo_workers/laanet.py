#!/usr/bin/env python3
"""
LAA-Net (CVPR 2024, PoseEfficientNet-B4 + E-FPN) single-image inference.
Requires float64. Runs in LAA-Net venv on MIEM.

Usage: python laanet.py <face_crop_path>
Output: prints PHOTO_RESULT:{json} to stdout
"""
import sys
import os
import json
import time
import glob as globmod

HOME = os.path.expanduser("~")
LAA_NET_DIR = os.path.join(HOME, "LAA-Net")

import cv2
import numpy as np
import torch
from torchvision import transforms as T

# LAA-Net config
FACE_IMG_SIZE = 384
ASPECT_RATIO = 1.0
PIXEL_STD = 200

MODEL_CFG = dict(
    type="PoseEfficientNet",
    model_name="efficientnet-b4",
    include_top=False,
    include_hm_decoder=True,
    head_conv=64,
    use_c2=False,
    use_c3=True,
    use_c4=True,
    use_c51=True,
    efpn=True,
    tfpn=False,
    se_layer=False,
    heads=dict(hm=1, cls=1, cstency=256),
)


def get_center_scale(shape, aspect_ratio, pixel_std=200):
    h, w = shape[0], shape[1]
    center = np.zeros((2), dtype=np.float32)
    center[0] = (w - 1) / 2
    center[1] = (h - 1) / 2
    if w > h * aspect_ratio:
        h = w * 1.0 / aspect_ratio
    else:
        w = h * 1.0 / aspect_ratio
    scale = np.array([w * 1.0 / pixel_std, h * 1.0 / pixel_std], dtype=np.float32)
    return center, scale


def get_dir(src_point, rot_rad):
    sn, cs = np.sin(rot_rad), np.cos(rot_rad)
    return [src_point[0] * cs - src_point[1] * sn,
            src_point[0] * sn + src_point[1] * cs]


def get_3rd_point(a, b):
    direct = a - b
    return b + np.array([-direct[1], direct[0]], dtype=np.float32)


def get_affine_transform(center, scale, rot, output_size,
                         shift=np.array([0, 0], dtype=np.float32), pixel_std=200):
    if not isinstance(scale, np.ndarray) and not isinstance(scale, list):
        scale = np.array([scale, scale])
    scale_tmp = scale * pixel_std
    src_w = scale_tmp[0]
    dst_w, dst_h = output_size[0], output_size[1]
    rot_rad = np.pi * rot / 180
    src_dir = get_dir([0, (src_w - 1) * -0.5], rot_rad)
    dst_dir = np.array([0, (dst_w - 1) * -0.5], np.float32)
    src = np.zeros((3, 2), dtype=np.float32)
    dst = np.zeros((3, 2), dtype=np.float32)
    src[0, :] = center + scale_tmp * shift
    src[1, :] = center + src_dir + scale_tmp * shift
    dst[0, :] = [(dst_w - 1) * 0.5, (dst_h - 1) * 0.5]
    dst[1, :] = np.array([(dst_w - 1) * 0.5, (dst_h - 1) * 0.5]) + dst_dir
    src[2:, :] = get_3rd_point(src[0, :], src[1, :])
    dst[2:, :] = get_3rd_point(dst[0, :], dst[1, :])
    return cv2.getAffineTransform(np.float32(src), np.float32(dst))


def preprocess_face(face_crop):
    img = cv2.resize(face_crop, (317, 317))
    img = img[60:317, 30:287, :]  # 257x257
    c, s = get_center_scale(img.shape[:2], ASPECT_RATIO, PIXEL_STD)
    trans = get_affine_transform(c, s, 0, [FACE_IMG_SIZE, FACE_IMG_SIZE], pixel_std=PIXEL_STD)
    img = cv2.warpAffine(img, trans, (FACE_IMG_SIZE, FACE_IMG_SIZE), flags=cv2.INTER_LINEAR)
    normalize = T.Compose([
        T.ToTensor(),
        T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])
    img_tensor = normalize(img / 255.0)
    return img_tensor.to(torch.float64)


def find_weight_file():
    patterns = [
        os.path.join(LAA_NET_DIR, "pretrained", "**", "*SBI*"),
        os.path.join(LAA_NET_DIR, "pretrained", "**", "*sbi*"),
        os.path.join(LAA_NET_DIR, "pretrained", "**", "*model_best*"),
    ]
    found = []
    for pat in patterns:
        found.extend(globmod.glob(pat, recursive=True))
    found = [w for w in found if os.path.isfile(w)]
    if not found:
        raise FileNotFoundError(f"No LAA-Net weight file found in {LAA_NET_DIR}/pretrained/")
    return found[0]


def main():
    image_path = sys.argv[1]
    t0 = time.time()

    try:
        original_cwd = os.getcwd()
        os.chdir(LAA_NET_DIR)
        if LAA_NET_DIR not in sys.path:
            sys.path.insert(0, LAA_NET_DIR)

        from models import build_model, load_pretrained, MODELS

        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        model = build_model(MODEL_CFG, MODELS)
        model = model.to(torch.float64)
        weight_path = find_weight_file()
        model = load_pretrained(model, weight_path)
        model = model.to(device)
        model.eval()

        os.chdir(original_cwd)

        image = cv2.imread(image_path)
        if image is None:
            raise RuntimeError(f"Cannot read: {image_path}")

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tensor = preprocess_face(rgb).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(tensor)
            cls_logits = outputs[0]["cls"]
            score = float(cls_logits.sigmoid().item())

        result = {
            "detector": "laanet", "score": round(score, 6),
            "label": "fake" if score >= 0.5 else "real",
            "time": round(time.time() - t0, 2), "error": None,
        }
    except Exception as e:
        result = {
            "detector": "laanet", "score": None, "label": None,
            "time": round(time.time() - t0, 2), "error": str(e)[:200],
        }

    print("PHOTO_RESULT:" + json.dumps(result))


if __name__ == "__main__":
    main()
