"""
Каталог метаданных: описания детекторов и deepfake-алгоритмов (генераторов датасетов).
Используется на странице Rankings для отображения info-карточек.
"""

DETECTORS = {
    "genconvit": {
        "name": "GenConViT",
        "description": "Генеративный свёрточно-трансформерный детектор дипфейков. Объединяет ConvNeXt и Vision Transformer с вариационным автоэнкодером для захвата локальных и глобальных артефактов манипуляции.",
        "year": 2023,
        "github": "https://github.com/erprogs/GenConViT",
        "paper": "https://arxiv.org/abs/2307.07036",
    },
    "clip_dfdet": {
        "name": "CLIP Deepfake Detector",
        "description": "Детектор на основе визуальных признаков CLIP (ViT-L/14), дообученный для бинарной классификации дипфейков. Извлекает эмбеддинги кадров и классифицирует линейным слоем.",
        "year": 2024,
        "github": "https://github.com/yermandy/deepfake-detection",
        "paper": None,
    },
    "sbi": {
        "name": "SBI (Self-Blended Images)",
        "description": "Детектор, обученный на самосмешанных изображениях — синтетических подделках, созданных наложением лица на само себя. Использует EfficientNet-B4 и RetinaFace для выделения лиц.",
        "year": 2022,
        "github": "https://github.com/mapooon/SelfBlendedImages",
        "paper": "https://arxiv.org/abs/2204.12965",
    },
    "npr": {
        "name": "NPR (Neighboring Pixel Relationships)",
        "description": "Обнаруживает GAN-сгенерированные изображения через анализ отношений соседних пикселей. Лёгкий классификатор на ResNet (2 слоя) поверх NPR-карт признаков. Потребление VRAM ~838 МБ.",
        "year": 2023,
        "github": "https://github.com/chuangchuangtan/NPR-DeepfakeDetection",
        "paper": "https://arxiv.org/abs/2310.06728",
    },
    "clip": {
        "name": "CLIP (zero-shot)",
        "description": "Zero-shot детекция дипфейков на основе CLIP через prompt engineering без дообучения.",
        "year": 2021,
        "github": "https://github.com/openai/CLIP",
        "paper": "https://arxiv.org/abs/2103.00020",
    },
    "cvit": {
        "name": "CViT",
        "description": "Свёрточно-трансформерный детектор дипфейков. CNN-бэкбон (VGG-стиль, 5 блоков) извлекает признаки, Vision Transformer (6 слоёв, 8 голов) классифицирует. Обучен на DFDC + FF++ + TrustedMedia + DeepfakeTIMIT + Celeb-v2.",
        "year": 2022,
        "github": "https://github.com/erprogs/CViT",
        "paper": None,
    },
    "altfreezing": {
        "name": "AltFreezing",
        "description": "Темпоральный детектор на 3D ResNet-50 (I3D). Поочерёдная заморозка пространственных и темпоральных весов при обучении для захвата обоих типов артефактов.",
        "year": 2023,
        "github": "https://github.com/ZhendongWang6/AltFreezing",
        "paper": "https://arxiv.org/abs/2307.06612",
    },
}

# Ключ — имя датасета (как в metrics.json / scan_runs), суффиксы _FFpp, _FFpp_vox2 и т.д.
ALGORITHMS = {
    "FOMM_FFpp": {
        "name": "FOMM",
        "full_name": "First Order Motion Model",
        "type": "face-to-face",
        "architecture": "GAN (перенос движения на основе ключевых точек)",
        "year": 2019,
        "github": "https://github.com/AliaksandrSiarohin/first-order-model",
        "paper": "https://arxiv.org/abs/2003.00196",
    },
    "FSGAN_FFpp": {
        "name": "FSGAN",
        "full_name": "Face Swapping GAN",
        "type": "face-to-face",
        "architecture": "GAN (реконструкция + inpainting)",
        "year": 2019,
        "github": "https://github.com/YuvalNirkin/fsgan",
        "paper": "https://arxiv.org/abs/1908.05932",
    },
    "FaceDancer_FFpp": {
        "name": "FaceDancer",
        "full_name": "FaceDancer",
        "type": "face-to-face",
        "architecture": "GAN (AEI-Net + ArcFace, адаптивное слияние признаков)",
        "year": 2022,
        "github": "https://github.com/felixrosberg/FaceDancer",
        "paper": "https://arxiv.org/abs/2210.10473",
    },
    "LivePortrait_FFpp": {
        "name": "LivePortrait",
        "full_name": "LivePortrait",
        "type": "face-to-face",
        "architecture": "Неявные ключевые точки (без диффузии, stitching + retargeting)",
        "year": 2024,
        "github": "https://github.com/KwaiVGI/LivePortrait",
        "paper": "https://arxiv.org/abs/2407.03168",
    },
    "SimSwap_FFpp": {
        "name": "SimSwap",
        "full_name": "SimSwap",
        "type": "face-to-face",
        "architecture": "GAN (ID Injection Module, слабое совпадение признаков)",
        "year": 2020,
        "github": "https://github.com/neuralchen/SimSwap",
        "paper": "https://arxiv.org/abs/2106.06340",
    },
    "inswapper_FFpp": {
        "name": "inswapper",
        "full_name": "InsightFace inswapper",
        "type": "face-to-face",
        "architecture": "ONNX (пайплайн InsightFace)",
        "year": 2022,
        "github": "https://github.com/deepinsight/insightface",
        "paper": None,
    },
    "batrutdinov_FFpp_DFL": {
        "name": "DeepFaceLab",
        "full_name": "DeepFaceLab",
        "type": "face-to-face",
        "architecture": "Автоэнкодер (архитектура DF)",
        "year": 2020,
        "github": "https://github.com/iperov/DeepFaceLab",
        "paper": "https://arxiv.org/abs/2005.05535",
    },
    "SadTalker_FFpp_vox2": {
        "name": "SadTalker",
        "full_name": "SadTalker",
        "type": "audio-to-face",
        "architecture": "3DMM + GAN (ExpNet + PoseVAE + face vid2vid)",
        "year": 2023,
        "github": "https://github.com/OpenTalker/SadTalker",
        "paper": "https://arxiv.org/abs/2211.12194",
    },
    "Wav2Lip_FFpp_vox2": {
        "name": "Wav2Lip",
        "full_name": "Wav2Lip",
        "type": "audio-to-face",
        "architecture": "GAN + SyncNet",
        "year": 2020,
        "github": "https://github.com/Rudrabha/Wav2Lip",
        "paper": "https://arxiv.org/abs/2008.10010",
    },
    "MuseTalk_FFpp_vox2": {
        "name": "MuseTalk",
        "full_name": "MuseTalk",
        "type": "audio-to-face",
        "architecture": "Latent Diffusion (VAE + UNet + Whisper)",
        "year": 2024,
        "github": "https://github.com/TMElyralab/MuseTalk",
        "paper": None,
    },
    "EchoMimic_FFpp_vox2": {
        "name": "EchoMimic",
        "full_name": "EchoMimic",
        "type": "audio-to-face",
        "architecture": "Latent Diffusion (SD + temporal attention + аудиокондиционирование)",
        "year": 2024,
        "github": "https://github.com/BadToBest/EchoMimic",
        "paper": "https://arxiv.org/abs/2407.08136",
    },
    "VideoRetalking_FFpp_vox2": {
        "name": "VideoRetalking",
        "full_name": "Video ReTalking",
        "type": "audio-to-face",
        "architecture": "GAN (каскад: face parsing + lip sync + enhancement)",
        "year": 2022,
        "github": "https://github.com/OpenTalker/video-retalking",
        "paper": "https://arxiv.org/abs/2211.14758",
    },
    "BlendSwap_FFpp": {
        "name": "BlendSwap",
        "full_name": "BlendSwap (через FaceFusion)",
        "type": "face-to-face",
        "architecture": "ONNX (BlendSwap 256, через FaceFusion)",
        "year": 2024,
        "github": "https://github.com/facefusion/facefusion",
        "paper": None,
    },
    "GHOST_FFpp": {
        "name": "GHOST",
        "full_name": "GHOST (через FaceFusion)",
        "type": "face-to-face",
        "architecture": "GAN (AEI-Net + ArcFace, ghost_1_256)",
        "year": 2021,
        "github": "https://github.com/sberbank-ai/sber-swap",
        "paper": "https://arxiv.org/abs/2202.03286",
    },
    "UniFace_FFpp": {
        "name": "UniFace",
        "full_name": "UniFace (через FaceFusion)",
        "type": "face-to-face",
        "architecture": "ONNX (UniFace 256, через FaceFusion)",
        "year": 2024,
        "github": "https://github.com/facefusion/facefusion",
        "paper": None,
    },
    "HyperReenact_FFpp": {
        "name": "HyperReenact",
        "full_name": "HyperReenact",
        "type": "face-to-face (reenactment)",
        "architecture": "StyleGAN2 + HyperNetwork (уточнение латентов + retargeting)",
        "year": 2023,
        "github": "https://github.com/StelaBou/HyperReenact",
        "paper": "https://arxiv.org/abs/2307.10797",
    },
}


def get_detector_info(detector_key):
    """Получить метаданные детектора по ключу."""
    return DETECTORS.get(detector_key)


def get_algorithm_info(dataset_key):
    """Получить метаданные алгоритма по имени датасета."""
    return ALGORITHMS.get(dataset_key)
