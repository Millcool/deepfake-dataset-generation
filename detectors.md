# Deepfake Detectors Tracker

Comprehensive catalog of open-source deepfake detection methods for evaluation on our generated datasets.
Status: research phase — collecting detectors, verifying repos, planning smoke tests.

---

## Summary Table

| # | Method | Year | Venue | Category | GitHub Stars | Code Available | Tested |
|---|--------|------|-------|----------|-------------|----------------|--------|
| 1 | DeepfakeBench | 2023 | NeurIPS | Benchmark (36 methods) | ~985 | Yes | - |
| 2 | DF40 | 2024 | NeurIPS | Dataset+Benchmark (40 techniques) | ~325 | Yes | - |
| 3 | Xception | 2019 | ICCV | Naive / CNN | ~2700 (FF++) | Yes | - |
| 4 | MesoNet | 2018 | WIFS | Naive / CNN | ~299 | Yes | - |
| 5 | MesoInception | 2018 | WIFS | Naive / CNN | ~299 | Yes | - |
| 6 | EfficientNet-B4 | 2019 | — | Naive / CNN | ~857 (DFDC winner) | Yes | - |
| 7 | CNN-Aug | 2020 | CVPR | Naive / CNN | ~979 | Yes | - |
| 8 | Capsule | 2019 | ICASSP | Spatial | ~120 | Yes | - |
| 9 | DSP-FWA | 2019 | CVPRW | Spatial | ~133 | Yes | - |
| 10 | FFD | 2020 | CVPR | Spatial | ~117 | Yes | - |
| 11 | Face X-Ray | 2020 | CVPR | Spatial | ~92 (unofficial) | Unofficial | - |
| 12 | Multi-Attention | 2021 | CVPR | Spatial | ~275 | Yes | - |
| 13 | CORE | 2022 | CVPRW | Spatial | ~52 | Yes | - |
| 14 | RECCE | 2022 | CVPR | Spatial | ~153 | Yes | - |
| 15 | SLADD | 2022 | CVPR Oral | Spatial | ~140 | Yes | - |
| 16 | ICT | 2022 | CVPR | Spatial | ~100 | Yes | - |
| 17 | UIA-ViT | 2022 | ECCV Oral | Spatial | ~36 | Yes | - |
| 18 | SBI | 2022 | CVPR Oral | Spatial | ~255 | Yes | - |
| 19 | UCF | 2023 | ICCV | Spatial | in DFBench | Yes (DFBench) | - |
| 20 | IID | 2023 | CVPR | Spatial | in DFBench | Yes (DFBench) | - |
| 21 | CADDM | 2023 | CVPR | Spatial | ~176 | Yes | - |
| 22 | SeeABLE | 2023 | ICCV | Spatial | — | Limited | - |
| 23 | LSDA | 2024 | CVPR | Spatial | in DFBench | Yes (DFBench) | - |
| 24 | LAA-Net | 2024 | CVPR | Spatial | ~172 | Yes | - |
| 25 | NPR | 2024 | CVPR | Spatial | ~294 | Yes | - |
| 26 | Exposing the Deception | 2024 | AAAI | Spatial | ~78 | Yes | - |
| 27 | UVIF | 2024 | ECAI | Spatial | — | Yes | - |
| 28 | Fairness-Generalization | 2024 | CVPR | Spatial | ~61 | Yes | - |
| 29 | DeepFake-Adapter | 2025 | IJCV | Spatial | — | Yes | - |
| 30 | Effort | 2025 | ICML Oral | Spatial / CLIP | ~195 | Yes | - |
| 31 | C2P-CLIP | 2025 | AAAI | Spatial / CLIP | ~93 | Yes | - |
| 32 | CLIP DF Detection | 2026 | WACV | Spatial / CLIP | — | Yes | - |
| 33 | D3 | 2025 | CVPR | Spatial | ~43 | Yes | - |
| 34 | ODDN | 2025 | AAAI Oral | Spatial | ~10 | Yes | - |
| 35 | F3-Net | 2020 | ECCV | Frequency | ~173 | Yes | - |
| 36 | SPSL | 2021 | CVPR | Frequency | in DFBench | Yes (DFBench) | - |
| 37 | SRM | 2021 | CVPR | Frequency | ~46 | Yes | - |
| 38 | FreqNet | 2024 | AAAI | Frequency | ~142 | Yes | - |
| 39 | FTCN | 2021 | ICCV | Video-level | ~122 | Yes | - |
| 40 | LipForensics | 2021 | CVPR | Video-level | ~143 | Yes | - |
| 41 | RealForensics | 2022 | CVPR | Video-level | ~103 | Yes | - |
| 42 | AltFreezing | 2023 | CVPR Highlight | Video-level | ~94 | Yes | - |
| 43 | TALL / TALL++ | 2023-2024 | ICCV / arXiv | Video-level | ~105 | Yes | - |
| 44 | MINTIME | 2024 | IEEE TIFS | Video-level | — | Yes | - |
| 45 | GenConViT | 2023 | — | Video-level | ~87 | Yes | - |
| 46 | FakeSTormer | 2025 | ICCV | Video-level | — | Yes | - |
| 47 | Cross-EfficientViT | 2021 | ICIAP | Video-level | — | Yes | - |
| 48 | LipFD | 2024 | NeurIPS | Multimodal (AV) | ~134 | Yes | - |
| 49 | SpeechForensics | 2024 | NeurIPS | Multimodal (AV) | ~22 | Yes | - |
| 50 | AVFF | 2024 | CVPR | Multimodal (AV) | — | Unofficial | - |
| 51 | M2F2-Det | 2025 | CVPR Oral | Multimodal (VLM+LLM) | ~105 | Yes | - |
| 52 | DIRE | 2023 | ICCV | Diffusion-specific | ~386 | Yes | - |
| 53 | UnivFD | 2023 | CVPR | Universal (CLIP) | ~328 | Yes | - |
| 54 | DiffusionFake | 2024 | NeurIPS | Diffusion-specific | ~57 | Yes | - |
| 55 | CoDE | 2024 | ECCV | Diffusion-specific | ~52 | Yes | - |

---

## I. Benchmarks & Frameworks

### 1. DeepfakeBench
- **Year:** 2023 (NeurIPS Datasets & Benchmarks)
- **Description:** Unified benchmark with 36 detectors (28 image + 8 video) under one roof. Standardized training, evaluation, data loading.
- **Detectors included:** Xception, MesoNet, MesoInception, CNN-Aug, EfficientNet-B4, Capsule, DSP-FWA, Face X-Ray, FFD, CORE, RECCE, UCF, IID, SBI, Multi-Attention, LSDA, UIA-ViT, SLADD, F3-Net, SPSL, SRM, FTCN, AltFreezing, TALL, Effort, and more
- **Datasets:** FF++, Celeb-DF-v1/v2, DFDC, DFDCP, DFD, FFIW, WildDeepfake, DeeperForensics, DF40
- **Pre-trained weights:** Yes (for all 36 detectors)
- **Paper:** https://arxiv.org/abs/2307.01426
- **GitHub:** https://github.com/SCLBD/DeepfakeBench (~985 stars)
- **Priority:** HIGH — best starting point for testing multiple detectors with a single codebase

### 2. DF40
- **Year:** 2024 (NeurIPS Datasets & Benchmarks)
- **Description:** Next-generation dataset with 40 distinct deepfake generation techniques (face-swapping, reenactment, synthesis, editing). Million-level scale.
- **Protocols:** 4 evaluation protocols (same/different domain, same/different forgery, one-vs-all)
- **Paper:** https://arxiv.org/abs/2406.13495
- **GitHub:** https://github.com/YZY-stack/DF40 (~325 stars)

### 3. FaceForensics++ (FF++)
- **Year:** 2019 (ICCV)
- **Description:** De facto standard benchmark. 1000 YouTube videos x 4 manipulations (Deepfakes, Face2Face, FaceSwap, NeuralTextures) x 3 compression levels (raw, c23, c40).
- **Paper:** https://arxiv.org/abs/1901.08971
- **GitHub:** https://github.com/ondyari/FaceForensics (~2700 stars)

### 4. DeepFake-O-Meter v2.0
- **Year:** 2024
- **Description:** Turnkey detection platform with web GUI. Integrates XceptionNet, MesoNet, DSP-FWA, FTCN, and others.
- **GitHub:** https://github.com/yuezunli/deepfake-o-meter (~27 stars)

---

## II. Naive / Baseline Detectors

### 5. MesoNet / MesoInception (2018)
- **Architecture:** Lightweight CNN (4 conv layers) / Inception-like CNN
- **Performance:** AUC ~83-86% (FaceForensics); >98% accuracy video-level (Deepfakes)
- **Datasets:** FaceForensics, custom
- **Paper:** https://arxiv.org/abs/1809.00888
- **GitHub:** https://github.com/DariusAf/MesoNet (~299 stars)
- **Notes:** Pioneering early work, very lightweight. Does not generalize well to modern methods.

### 6. Xception (2019)
- **Architecture:** XceptionNet (depthwise separable convolutions), ImageNet pretrained
- **Performance:** Up to 99.26% accuracy on FF++ raw; ~94.50% AUC on FF++ c23 (DeepfakeBench)
- **Datasets:** FF++, Celeb-DF, DFDC
- **Paper:** https://arxiv.org/abs/1901.08971
- **GitHub:** https://github.com/ondyari/FaceForensics (~2700 stars)
- **Notes:** Standard baseline for all deepfake detection papers. Poor cross-dataset generalization.

### 7. EfficientNet-B4 (2019-2020)
- **Architecture:** EfficientNet (compound scaling: depth, width, resolution)
- **Performance:** ~93.89% AUC on FF++ c23 (DeepfakeBench); DFDC Challenge winner used B7 (65.18% on black-box test)
- **Datasets:** FF++, DFDC, Celeb-DF
- **Paper:** Various; DFDC winning solution
- **GitHub:** https://github.com/selimsef/dfdc_deepfake_challenge (~857 stars)
- **Notes:** Strong feature extraction, widely used backbone.

### 8. CNN-Aug / CNNDetection (2020)
- **Architecture:** ResNet-50 + extensive data augmentation (JPEG, blur, noise)
- **Performance:** >97% AP on ProGAN; 92% AUC generalizing to StyleGAN3; evaluated across 11 CNN generators
- **Datasets:** ProGAN, StyleGAN, StyleGAN2, BigGAN, CycleGAN, StarGAN, GauGAN, etc.
- **Paper:** https://openaccess.thecvf.com/content_CVPR_2020/papers/Wang_CNN-Generated_Images_Are_Surprisingly_Easy_to_Spot..._for_Now_CVPR_2020_paper.pdf (CVPR 2020)
- **GitHub:** https://github.com/PeterWang512/CNNDetection (~979 stars)
- **Notes:** Key insight: classifier trained on one generator generalizes to many others. Augmentation is critical.

---

## III. Spatial Detectors

### 9. Capsule Network (2019)
- **Architecture:** VGG features + Capsule layers with dynamic routing
- **Performance:** AUC ~99.33% (FF++ Deepfakes), ~98.29% (Celeb-DF)
- **Datasets:** FF++ (all 4 methods), CGvsPhoto, Replay-Attack
- **Paper:** https://arxiv.org/abs/1910.12467 (ICASSP 2019)
- **GitHub:** https://github.com/nii-yamagishilab/Capsule-Forensics-v2 (~120 stars)
- **Notes:** Part-whole relationships via capsules. Computationally more expensive.

### 10. DSP-FWA (2019)
- **Architecture:** Dual Spatial Pyramid + CNN for detecting face warping artifacts
- **Performance:** AUC ~87.4% (Celeb-DF)
- **Datasets:** UADFV, FF++, Celeb-DF
- **Paper:** https://arxiv.org/abs/1811.00656 (CVPRW 2019)
- **GitHub:** https://github.com/yuezunli/CVPRW2019_Face_Artifacts (~133 stars)
- **Notes:** Physically motivated — exploits warping. Performance degrades on high-quality fakes.

### 11. FFD — Face Forgery Detection (2020)
- **Architecture:** Xception + attention (joint detection + localization)
- **Performance:** AUC ~99%+ (UADFV), ~65.3% (Celeb-DF cross-dataset)
- **Datasets:** FF++, UADFV, Celeb-DF
- **Paper:** https://arxiv.org/abs/1910.01717 (CVPR 2020)
- **GitHub:** https://github.com/JStehouwer/FFD_CVPR2020 (~117 stars)
- **Notes:** Multi-task: detection + localization via attention maps.

### 12. Face X-Ray (2020)
- **Architecture:** HRNet backbone; predicts blending boundary map
- **Performance:** AUC ~95.40% (FF++ BI), ~80.58% (Celeb-DF cross-dataset)
- **Datasets:** FF++, Celeb-DF
- **Paper:** https://arxiv.org/abs/1912.13458 (CVPR 2020)
- **GitHub:** https://github.com/neverUseThisName/Face-X-Ray (~92 stars, unofficial)
- **Notes:** No official code. Method-agnostic: only assumes blending step exists. Influential on SBI.

### 13. Multi-Attention (2021)
- **Architecture:** EfficientNet-B4 + multiple spatial attention heads + textural feature enhancement
- **Performance:** AUC ~99.80% (FF++ c23), ~67.44% (Celeb-DF cross-dataset)
- **Datasets:** FF++, Celeb-DF, DFDC, WildDeepfake
- **Paper:** https://arxiv.org/abs/2103.02406 (CVPR 2021)
- **GitHub:** https://github.com/yoctta/multiple-attention (~275 stars)
- **Notes:** Fine-grained local attention. Microsoft Research.

### 14. CORE (2022)
- **Architecture:** Xception + consistency regularization via augmentation pairs
- **Performance:** AUC ~99.46% (FF++ HQ), ~99.94% TDR
- **Datasets:** FF++ (HQ, RAW), Celeb-DF, DFD, DFDC-P
- **Paper:** https://arxiv.org/abs/2206.02749 (CVPRW 2022)
- **GitHub:** https://github.com/niyunsheng/CORE (~52 stars)
- **Notes:** Simple but effective consistency loss between augmented views.

### 15. RECCE (2022)
- **Architecture:** Encoder-decoder (reconstruction on real faces only) + graph reasoning + multi-scale
- **Performance:** AUC ~91.33% (DFDC), ~68.71% (Celeb-DF), ~64.31% (WildDeepfake)
- **Datasets:** FF++, Celeb-DF, WildDeepfake, DFDC, DFD
- **Paper:** https://openaccess.thecvf.com/content/CVPR2022/papers/Cao_End-to-End_Reconstruction-Classification_Learning_for_Face_Forgery_Detection_CVPR_2022_paper.pdf (CVPR 2022)
- **GitHub:** https://github.com/VISION-SJTU/RECCE (~153 stars)
- **Notes:** One-class paradigm — treats fakes as outliers from real distribution. SJTU.

### 16. SLADD (2022)
- **Architecture:** Self-supervised adversarial training with augmentation pool
- **Performance:** Strong cross-dataset generalization
- **Datasets:** FF++, Celeb-DF, DFDC, DFDCP
- **Paper:** CVPR 2022 Oral
- **GitHub:** https://github.com/liangchen527/SLADD (~140 stars)
- **Notes:** Adversarial training generates the hardest forgeries for current model.

### 17. ICT — Identity Consistency Transformer (2022)
- **Architecture:** ViT; detects identity inconsistency between inner/outer face regions
- **Performance:** Consistency loss improves 23-40% over ablation
- **Datasets:** FF++, Celeb-DF-v2, DFDC
- **Paper:** https://arxiv.org/abs/2203.01318 (CVPR 2022)
- **GitHub:** https://github.com/LightDXY/ICT_DeepFake (~100 stars)
- **Notes:** Identity-based — robust to compression. Primarily for face-swapping.

### 18. UIA-ViT (2022)
- **Architecture:** ViT + Unsupervised Patch Consistency Learning + Progressive Consistency Assembly
- **Performance:** AUC 99.33% (FF++ HQ), 82.41% (Celeb-DF-v2), 75.80% (DFDC)
- **Datasets:** FF++, DFD, Celeb-DF-v1/v2, DFDC
- **Paper:** https://arxiv.org/abs/2210.12752 (ECCV 2022 Oral)
- **GitHub:** https://github.com/wany0824/UIA-ViT (~36 stars)
- **Notes:** No pixel-level annotations needed. Pre-trained weights available.

### 19. SBI — Self-Blended Images (2022)
- **Architecture:** EfficientNet-B4; self-blended training (no fake data needed)
- **Performance:** Cross-dataset accuracy: Celeb-DF 93.82%, DFD 97.87%, DFDC 73.01%, DFDCP 85.70%
- **Datasets:** FF++, Celeb-DF-v2, DFD, DFDC, DFDCP, FFIW
- **Paper:** https://arxiv.org/abs/2204.08376 (CVPR 2022 Oral)
- **GitHub:** https://github.com/mapooon/SelfBlendedImages (~255 stars)
- **Notes:** Influential — widely adopted as augmentation strategy. No fake data needed.

### 20. UCF — Uncovering Common Features (2023)
- **Architecture:** Multi-task disentanglement; separates common forgery features from method-specific ones
- **Performance:** AUC 95.37% (FF++ avg in DeepfakeBench), 82.4% (Celeb-DF)
- **Datasets:** FF++, Celeb-DF, DFDC, DFDCP
- **Paper:** https://arxiv.org/abs/2304.13949 (ICCV 2023)
- **GitHub:** In DeepfakeBench (`training/detectors/ucf_detector.py`)
- **Notes:** Top cross-manipulation performer. No standalone repo.

### 21. IID — Implicit Identity Driven (2023)
- **Architecture:** Mines implicit target identity from fake face
- **Datasets:** FF++, Celeb-DF, DFDC
- **Paper:** CVPR 2023
- **GitHub:** In DeepfakeBench (`training/detectors/iid_detector.py`)
- **Notes:** Designed for face-swapping; may miss reenactment forgeries.

### 22. CADDM (2023)
- **Architecture:** EfficientNet-B4; reduces identity leakage in detection
- **Performance:** AUC 99.79% (FF++), 93.88% (Celeb-DF), 73.85% (DFDC)
- **Datasets:** FF++, Celeb-DF, DFDC
- **Paper:** CVPR 2023
- **GitHub:** https://github.com/megvii-research/CADDM (~176 stars)
- **Notes:** Megvii Research. Strong Celeb-DF performance.

### 23. SeeABLE (2023)
- **Architecture:** One-class OOD detection + soft discrepancies + bounded contrastive learning
- **Performance:** AUC 98.5% (FF++ HQ avg), 99.6% (FF++ raw)
- **Datasets:** FF++, Celeb-DF, DFDC
- **Paper:** ICCV 2023
- **GitHub:** No well-maintained public repo found
- **Notes:** No fake data needed. Code availability limited.

### 24. LSDA — Latent Space Data Augmentation (2024)
- **Architecture:** Teacher-student with latent space augmentation
- **Datasets:** FF++, Celeb-DF, DFDC, DeeperForensics
- **Paper:** https://arxiv.org/abs/2311.11278 (CVPR 2024)
- **GitHub:** In DeepfakeBench
- **Notes:** Plug-and-play latent augmentation approach.

### 25. LAA-Net — Localized Artifact Attention (2024)
- **Architecture:** Enhanced FPN + heatmap attention + self-consistency attention
- **Performance:** AUC 99.96% (FF++), 95.40% (Celeb-DF), 86.94% (DFDC), 80.03% (WildDeepfake)
- **Datasets:** FF++, Celeb-DF, DFW, DFD, DFDC
- **Paper:** https://arxiv.org/abs/2401.13856 (CVPR 2024)
- **GitHub:** https://github.com/10Ring/LAA-Net (~172 stars)
- **Notes:** Quality-agnostic. Strong Celeb-DF cross-dataset (95.40%).

### 26. NPR — Neighboring Pixel Relationships (2024)
- **Architecture:** Captures local up-sampling artifacts via pixel relationship analysis
- **Performance:** Avg accuracy 93.2% across 17 GANs; GenImage 90.1% acc, 96.9% AP
- **Datasets:** AIGCDetectBenchmark, GenImage, ProGAN, StyleGAN, diffusion models
- **Paper:** https://arxiv.org/abs/2312.10461 (CVPR 2024)
- **GitHub:** https://github.com/chuangchuangtan/NPR-DeepfakeDetection (~294 stars)
- **Notes:** Very simple, lightweight, strong generalization to unseen generators.

### 27. Exposing the Deception (2024)
- **Architecture:** Framework uncovering additional forgery clues
- **Datasets:** FF++, Celeb-DF, DFDC
- **Paper:** AAAI 2024
- **GitHub:** https://github.com/QingyuLiu/Exposing-the-Deception (~78 stars)

### 28. UVIF (2024)
- **Datasets:** (details pending)
- **Paper:** https://ebooks.iospress.nl/doi/10.3233/FAIA240548 (ECAI 2024)
- **GitHub:** https://github.com/haotianll/UVIF

### 29. Fairness-Generalization (2024)
- **Architecture:** Disentanglement + Fairness Learning + SAM optimization
- **Performance:** Maintains fairness and accuracy cross-domain; reduces FPR across demographics
- **Datasets:** FF++, DFDC, Celeb-DF, DFD (demographic subgroups)
- **Paper:** https://openaccess.thecvf.com/content/CVPR2024/papers/Lin_Preserving_Fairness_Generalization_in_Deepfake_Detection_CVPR_2024_paper.pdf (CVPR 2024)
- **GitHub:** https://github.com/Purdue-M2/Fairness-Generalization (~61 stars)
- **Notes:** First method ensuring fairness across demographics in cross-domain detection.

### 30. Effort — Orthogonal Subspace Decomposition (2025)
- **Architecture:** Plug-and-play module for ViT/CLIP; orthogonal subspace decomposition
- **Performance:** SOTA on DF40; works for both face deepfakes and general AIGI
- **Datasets:** DF40, GenImage, FF++, Chameleon
- **Paper:** ICML 2025 Oral
- **GitHub:** https://github.com/YZY-stack/Effort-AIGI-Detection (~195 stars)
- **Notes:** Most recent top-tier. Plug-and-play into any ViT backbone.

### 31. C2P-CLIP (2025)
- **Architecture:** CLIP with category common prompts ("Deepfake" / "Camera")
- **Performance:** +12.41% improvement over vanilla CLIP; zero extra inference params
- **Paper:** https://arxiv.org/abs/2408.09647 (AAAI 2025)
- **GitHub:** https://github.com/chuangchuangtan/C2P-CLIP-DeepfakeDetection (~93 stars)

### 32. CLIP Deepfake Detection (2026)
- **Architecture:** CLIP ViT-L/14 + LN-tuning (parameter-efficient fine-tuning)
- **Paper:** WACV 2026
- **GitHub:** https://github.com/yermandy/deepfake-detection

### 33. D3 — Discrepancy Dual-Branch (2025)
- **Architecture:** Dual-branch: original detection + distorted feature discrepancy signal
- **Performance:** ID accuracy 96.6%, OOD accuracy 86.7%, total 90.7% (+5.3% OOD over SOTA)
- **Paper:** CVPR 2025
- **GitHub:** https://github.com/BigAandSmallq/D3 (~43 stars)

### 34. DeepFake-Adapter (2025)
- **Architecture:** Dual-level adapter (GBA + LSA) for pre-trained ViT
- **Paper:** IJCV 2025
- **GitHub:** https://github.com/rshaojimmy/DeepFake-Adapter

### 35. ODDN — Open-world Detection on Social Networks (2025)
- **Architecture:** Handles unpaired data in open-world social media scenarios
- **Paper:** https://arxiv.org/abs/2410.18687 (AAAI 2025 Oral)
- **GitHub:** https://github.com/ManyiLee/Open-world-Deepfake-Detection-Network (~10 stars)

---

## IV. Frequency-Domain Detectors

### 36. F3-Net (2020)
- **Architecture:** Two-stream: frequency-aware decomposition (DCT) + local frequency statistics; Xception backbone
- **Performance:** AUC ~94.49% (FF++ c23 in DFBench); 90.43% acc on FF++ LQ
- **Datasets:** FF++ (raw, c23, c40)
- **Paper:** https://arxiv.org/abs/2007.09355 (ECCV 2020)
- **GitHub:** https://github.com/yyk-wew/F3Net (~173 stars)
- **Notes:** Pioneer in frequency-domain deepfake detection. Strong on compressed (LQ) media.

### 37. SPSL — Spatial-Phase Shallow Learning (2021)
- **Architecture:** Combines spatial image + phase spectrum (Fourier transform); shallow features for transferability
- **Performance:** AUC ~96.91% (FF++ c23), ~78.75% avg cross-domain (best in DeepfakeBench)
- **Datasets:** FF++, Celeb-DF, DFDC
- **Paper:** CVPR 2021
- **GitHub:** In DeepfakeBench (`training/detectors/spsl_detector.py`)
- **Notes:** Top cross-domain performer in DeepfakeBench. Phase spectrum captures up-sampling artifacts.

### 38. SRM — Spatial Rich Model (2021)
- **Architecture:** Two-stream: SRM high-frequency noise filters + RGB with cross-modality attention
- **Performance:** Strong cross-dataset generalization
- **Datasets:** FF++, Celeb-DF, DFDC
- **Paper:** https://arxiv.org/abs/2103.12376 (CVPR 2021)
- **GitHub:** https://github.com/crywang/face-forgery-detection (~46 stars)
- **Notes:** SRM filters from steganalysis. Captures noise residuals invisible to spatial methods.

### 39. FreqNet (2024)
- **Architecture:** Frequency domain learning (FFT -> conv -> iFFT on phase + amplitude); only 1.9M params
- **Performance:** +9.8% improvement over baselines across 17 GANs; 91.5% mean accuracy (4-class)
- **Datasets:** 17 GAN architectures
- **Paper:** https://arxiv.org/abs/2403.07240 (AAAI 2024)
- **GitHub:** https://github.com/chuangchuangtan/FreqNet-DeepfakeDetection (~142 stars)
- **Notes:** Extremely lightweight (1.9M params) yet outperforms 304M-param methods. Same author as NPR.

---

## V. Video-Level / Temporal Detectors

### 40. FTCN — Fully Temporal Convolution Network (2021)
- **Architecture:** 3D ResNet-50 (spatial kernel=1) + Temporal Transformer (12 heads)
- **Performance:** Video-level AUC: ~86.9% (Celeb-DF-v2), ~74.0% (DFDC), ~98.8% (FaceShifter)
- **Datasets:** FF++, Celeb-DF-v2, DFDC, FaceShifter, DeeperForensics
- **Paper:** https://arxiv.org/abs/2108.06693 (ICCV 2021)
- **GitHub:** https://github.com/yinglinzheng/FTCN (~122 stars)
- **Notes:** Temporal-only approach — eliminates spatial overfitting. Included in TrueMedia platform.

### 41. LipForensics (2021)
- **Architecture:** Pre-trained on lipreading (MS-TCN), fine-tuned for forgery detection
- **Performance:** Video-level AUC: 82.4% (Celeb-DF-v2), 73.5% (DFDC), 97.1% (FaceShifter), 97.6% (DeeperForensics)
- **Datasets:** FF++, Celeb-DF-v2, DFDC, FaceShifter, DeeperForensics
- **Paper:** https://arxiv.org/abs/2012.07657 (CVPR 2021)
- **GitHub:** https://github.com/ahaliassos/LipForensics (~143 stars)
- **Notes:** Semantic lip-movement analysis. Robust to compression/noise. May miss non-mouth manipulations.

### 42. RealForensics (2022)
- **Architecture:** Self-supervised on real talking face videos (LRW dataset), then fine-tuned
- **Performance:** Video-level AUC: 86.9% (Celeb-DF-v2), 75.9% (DFDC), 99.7% (FaceShifter), 99.3% (DeeperForensics)
- **Datasets:** FF++, Celeb-DF-v2, DFDC, FaceShifter, DeeperForensics
- **Paper:** https://arxiv.org/abs/2201.07131 (CVPR 2022)
- **GitHub:** https://github.com/ahaliassos/RealForensics (~103 stars)
- **Notes:** Improves over LipForensics on all metrics. Self-supervised on real data only. Requires 8 GPUs for training.

### 43. AltFreezing (2023)
- **Architecture:** 3D ConvNet with alternating frozen spatial/temporal weights
- **Performance:** AUC 89.5% (Celeb-DF v2), 98.5% (DFD), 99.4% (FaceShifter), avg 96.7%
- **Datasets:** FF++, Celeb-DF v2, DFD, FaceShifter, DeeperForensics
- **Paper:** https://arxiv.org/pdf/2307.08317 (CVPR 2023 Highlight)
- **GitHub:** https://github.com/ZhendongWang6/AltFreezing (~94 stars)
- **Notes:** Elegant training strategy. Disentangles spatial and temporal features.

### 44. TALL / TALL++ (2023-2024)
- **Architecture:** Thumbnail Layout (video frames → grid image) + Swin-B backbone; TALL++ adds Graph Reasoning Block (GRB) + Semantic Consistency Loss
- **Performance:** TALL AUC: 99.87% (FF++ HQ), 94.57% (FF++ LQ); TALL++ AUC: 99.92% (FF++ HQ), 98.68% (FF++ LQ), 91.96% (FF++→Celeb-DF), 78.51% (FF++→DFDC)
- **Datasets:** FF++, Celeb-DF, DFDC, Wild-DF, KoDF, DeeperForensics
- **Paper:** https://arxiv.org/pdf/2403.10261
- **GitHub:** https://github.com/rainy-xu/TALL4Deepfake (~105 stars)
- **Notes:** Model-agnostic trick — transforms temporal into spatial. Extremely simple to implement.

### 45. MINTIME (2024)
- **Architecture:** TimeSformer + Divided Space-Time Attention + Temporal Coherent Positional Embedding + Size Embedding
- **Performance:** +14% AUC on ForgeryNet multi-person scenarios
- **Datasets:** ForgeryNet, FF++
- **Paper:** IEEE TIFS 2024
- **GitHub:** https://github.com/davide-coccomini/MINTIME-Multi-Identity-size-iNvariant-TIMEsformer-for-Video-Deepfake-Detection
- **Notes:** Specialized for multi-face videos.

### 46. GenConViT (2023)
- **Architecture:** ConvNeXt + Swin Transformer + VAE autoencoder
- **Performance:** 95.8% accuracy, 99.3% AUC
- **Datasets:** DFDC, FF++, DeepfakeTIMIT, Celeb-DF v2
- **GitHub:** https://github.com/erprogs/GenConViT (~87 stars)
- **Notes:** Pre-trained weights on HuggingFace. Native video-level.

### 47. FakeSTormer (2025)
- **Architecture:** Multi-task self-supervised learning (spatial + temporal vulnerabilities); Self-Blended Video (SBV)
- **Paper:** ICCV 2025
- **GitHub:** https://github.com/10Ring/FakeSTormer
- **Notes:** SOTA for video-level detection. From same lab as LAA-Net.

### 48. Cross-EfficientViT (2021)
- **Architecture:** EfficientNet-B0 + Vision Transformers for video-level
- **Performance:** AUC 0.951 (DFDC)
- **GitHub:** https://github.com/davide-coccomini/Combining-EfficientNet-and-Vision-Transformers-for-Video-Deepfake-Detection

---

## VI. Multimodal / Audio-Visual Detectors

### 49. LipFD — Lip Forgery Detection (2024)
- **Architecture:** Temporal lip-audio inconsistency detection; captures lip-head biological links
- **Performance:** Avg accuracy 96.93% (4 lip forgery types), 95.3% avg lip-sync detection, 90.2% real-world (WeChat)
- **Datasets:** AVLips (340K samples: MakeItTalk, Wav2Lip, TalkLip, SadTalker)
- **Paper:** https://arxiv.org/abs/2401.15668 (NeurIPS 2024)
- **GitHub:** https://github.com/AaronComo/LipFD (~134 stars)
- **Notes:** Custom large-scale dataset included. Specifically for lip-syncing deepfakes.

### 50. SpeechForensics (2024)
- **Architecture:** Audio-visual speech representation via self-supervised masked prediction
- **Performance:** AUC: 97.6% (FF++), 99.0% (FakeAVCeleb), 91.7% (KoDF)
- **Datasets:** FF++, FakeAVCeleb, KoDF
- **Paper:** NeurIPS 2024
- **GitHub:** https://github.com/Eleven4AI/SpeechForensics (~22 stars)
- **Notes:** No fake data needed for pre-training. Audio modality required.

### 51. AVFF — Audio-Visual Feature Fusion (2024)
- **Architecture:** Two-stage cross-modal learning (self-supervised AV correspondence → supervised detection)
- **Performance:** FakeAVCeleb: 98.6% accuracy, 99.1% AUC (+14.9% acc over prior SOTA)
- **Datasets:** FakeAVCeleb
- **Paper:** CVPR 2024
- **GitHub:** https://github.com/JoeLeelyf/OpenAVFF (unofficial)
- **Notes:** Official code not publicly released.

### 52. M2F2-Det (2025)
- **Architecture:** CLIP + LLM for joint detection and natural language explanation
- **Performance:** FF++ (c40): +1.01% acc and +2.01% AUC over TALL
- **Datasets:** FF++, cross-dataset evaluations
- **Paper:** CVPR 2025 Oral
- **GitHub:** https://github.com/CHELSEA234/M2F2_Det (~105 stars)
- **Notes:** First method to jointly detect and explain forgeries. LLM adds inference cost.

---

## VII. Diffusion-Specific & Universal Detectors

### 53. DIRE — Diffusion Reconstruction Error (2023)
- **Architecture:** Pre-trained diffusion model; measures reconstruction error between input and reconstruction
- **Performance:** Detects both GAN and diffusion-generated images; generalizes to unseen generators
- **Datasets:** Various GAN + diffusion model outputs
- **Paper:** https://arxiv.org/abs/2303.09295 (ICCV 2023)
- **GitHub:** https://github.com/ZhendongWang6/DIRE (~386 stars)
- **Notes:** Slow inference (requires diffusion forward/backward pass). DistilDIRE is 3.2x faster distillation.

### 54. UnivFD — Universal Fake Detection (2023)
- **Architecture:** Pre-trained CLIP features + linear probing
- **Performance:** Tested on 19 generative models (11 GANs + 8 diffusion including Stable Diffusion, DALL-E, Midjourney)
- **Datasets:** 19 generators
- **Paper:** https://arxiv.org/abs/2302.10174 (CVPR 2023)
- **GitHub:** https://github.com/WisconsinAIVision/UniversalFakeDetect (~328 stars)
- **Notes:** Remarkably simple. Less competitive on face-specific benchmarks.

### 55. DiffusionFake (2024)
- **Architecture:** Plug-and-play; injects detector features into frozen Stable Diffusion for source/target identity reconstruction
- **Performance:** Significantly improves cross-domain generalization of any detector
- **Datasets:** Multiple cross-domain
- **Paper:** NeurIPS 2024
- **GitHub:** https://github.com/skJack/DiffusionFake (~57 stars)
- **Notes:** No extra params at inference. Requires SD during training.

### 56. CoDE — Contrasting Deepfakes Diffusion (2024)
- **Architecture:** Contrastive learning + global-local similarity; trained on D3 dataset (11.5M images)
- **Datasets:** Stable Diffusion 1.4, SD 2.1, SDXL, DeepFloyd IF
- **Paper:** ECCV 2024
- **GitHub:** https://github.com/aimagelab/CoDE (~52 stars)
- **Notes:** Focused on diffusion model detection specifically.

---

## VIII. Awesome Lists & Resources

| Resource | GitHub | Stars | Description |
|----------|--------|-------|-------------|
| Awesome-Deepfakes-Detection | https://github.com/Daisy-Zhang/Awesome-Deepfakes-Detection | ~1700 | Papers, tools, datasets, code |
| Awesome-Comprehensive-DF-Detection | https://github.com/qiqitao77/Awesome-Comprehensive-Deepfake-Detection | — | Systematic taxonomy, updated |
| Awesome-DF-Generation-and-Detection | https://github.com/flyingby/Awesome-Deepfake-Generation-and-Detection | — | Both generation and detection |
| Awesome-Face-Forgery | https://github.com/clpeng/Awesome-Face-Forgery-Generation-and-Detection | — | Curated articles and code |
| DeepfakeSoK | https://github.com/shahroztariq/DeepfakeSoK | — | Systematization of Knowledge |

---

## Key Trends & Observations

1. **Generalization > In-domain accuracy.** FF++ in-domain is saturated (99%+). All 2023-2025 papers focus on cross-dataset and cross-manipulation.
2. **CLIP/VLM dominance (2024-2025).** UnivFD, C2P-CLIP, Effort, M2F2-Det leverage pre-trained vision-language models.
3. **Frequency domain remains powerful.** NPR, FreqNet, F3-Net, SPSL — up-sampling artifacts are a reliable signal.
4. **Self-supervised / one-class learning rising.** SBI, SLADD, RealForensics, SpeechForensics — training without fake data improves generalization.
5. **Multimodal detection increasingly important.** Lip-syncing deepfakes (Wav2Lip, SadTalker) demand audio-visual approaches (LipFD, SpeechForensics, AVFF).
6. **DeepfakeBench is the go-to starting point.** 36 methods, pretrained weights, unified pipeline — ideal for our evaluation.

---

## Testing Plan (TODO)

- [ ] Set up DeepfakeBench on remote server (covers ~36 methods at once)
- [ ] Smoke test: 1 video per detector to verify it runs
- [ ] Prioritize: video-level detectors (FTCN, AltFreezing, TALL, LipForensics, RealForensics) — most relevant for our video datasets
- [ ] Evaluate standalone methods not in DeepfakeBench (GenConViT, LipFD, MINTIME, Effort, LAA-Net)
- [ ] Document results in this file
