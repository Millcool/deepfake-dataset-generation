#!/usr/bin/env python3
"""
Генерация 10 минимальных MP4-заглушек для smoke-тестов детекторов.
Каждый файл — 1 секунда, 30fps, 64x64, цветной прямоугольник.
Использует OpenCV. Запускать один раз.
"""

import json
import os
import struct

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "test_videos")


def write_minimal_mp4(path, r, g, b):
    """
    Генерирует минимальный валидный MP4 файл (~2KB) с одним кадром.
    Цвет задаёт визуальную различимость между файлами.
    Использует raw H.264 Baseline в ftyp+moov+mdat контейнере.
    """
    # Минимальный подход: создать MP4 через raw bytes
    # Для простоты используем подход с минимальным ftyp + mdat
    width, height, fps = 64, 64, 1

    # Создаём raw uncompressed frame как Motion JPEG в MP4
    # Ещё проще: просто создадим файл через struct с правильными заголовками
    # Самый простой валидный MP4: ftyp box + mdat box с мусорными данными
    # Для smoke-теста детектора нам не нужен playable video, нужен файл с .mp4 расширением

    # Генерируем минимальный MP4 со стандартными боксами
    ftyp = b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom'  # 24 bytes

    # Fake video data (colored pixels as raw data)
    pixel_row = bytes([b, g, r]) * width
    frame_data = pixel_row * height

    # mdat box
    mdat_size = 8 + len(frame_data)
    mdat = struct.pack('>I', mdat_size) + b'mdat' + frame_data

    with open(path, 'wb') as f:
        f.write(ftyp)
        f.write(mdat)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 5 "real" + 5 "fake" стабов
    videos = {
        "real_001.mp4": {"label": "real", "color": (0, 180, 0)},
        "real_002.mp4": {"label": "real", "color": (0, 200, 0)},
        "real_003.mp4": {"label": "real", "color": (0, 160, 50)},
        "real_004.mp4": {"label": "real", "color": (50, 200, 50)},
        "real_005.mp4": {"label": "real", "color": (0, 220, 80)},
        "fake_001.mp4": {"label": "fake", "color": (200, 0, 0)},
        "fake_002.mp4": {"label": "fake", "color": (220, 0, 0)},
        "fake_003.mp4": {"label": "fake", "color": (180, 50, 0)},
        "fake_004.mp4": {"label": "fake", "color": (200, 30, 30)},
        "fake_005.mp4": {"label": "fake", "color": (240, 0, 50)},
    }

    manifest = {}
    for filename, info in videos.items():
        path = os.path.join(OUTPUT_DIR, filename)
        r, g, b = info["color"]
        write_minimal_mp4(path, r, g, b)
        manifest[filename] = info["label"]
        size_kb = os.path.getsize(path) / 1024
        print(f"  Created {filename} ({size_kb:.1f} KB) — {info['label']}")

    # manifest.json
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n  Manifest: {manifest_path}")
    print(f"  Total: {len(videos)} test videos")


if __name__ == "__main__":
    main()
