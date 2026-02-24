# EchoMimic_FFpp_vox2 — Документ воспроизводимости

## Обзор

Датасет из 1000 дипфейк-видео, сгенерированных моделью **EchoMimic** — латентной диффузионной моделью для аудио-управляемой анимации портретов.

- **Модель**: [EchoMimic](https://github.com/BadToBest/EchoMimic) (Terminal Technology / BadToBest, 2024)
- **Архитектура**: Latent Diffusion (SD Image Variations + Reference UNet + Motion Module) с аудиокондиционированием через Whisper
- **Модальность**: Audio-to-face (изображение + аудио → видео с анимированным лицом)
- **Исходные изображения**: Первые кадры из FaceForensics++ C23 Original (1000 видео → 1000 кадров, `000_first.jpg`–`999_first.jpg`)
- **Исходное аудио**: VoxCeleb2 test AAC (50 спикеров × 4 клипа × 5 повторов = 1000 аудиоклипов)
- **Итого**: 1000 видео, ~0.51 ГБ

## Этапы пайплайна

### Шаг 1 — Клонирование репозитория

```bash
cd /var/lib/ilanmironov@edu.hse.ru/
git clone https://github.com/BadToBest/EchoMimic.git echomimic
cd echomimic
```

Коммит репозитория: `a53e970` (Update README.md)

### Шаг 2 — Настройка окружения

Виртуальное окружение:

```bash
python3 -m venv .venv_echomimic
source .venv_echomimic/bin/activate
pip install -r requirements.txt
pip install torch==2.2.2+cu121 torchvision==0.17.2+cu121 torchaudio==2.2.2+cu121 --index-url https://download.pytorch.org/whl/cu121
```

Ключевые установленные пакеты:
| Пакет | Версия |
|-------|--------|
| torch | 2.2.2+cu121 |
| torchaudio | 2.2.2+cu121 |
| torchvision | 0.17.2+cu121 |
| diffusers | 0.24.0 |
| accelerate | 1.12.0 |
| transformers | 4.38.2 |
| opencv-python | 4.13.0.92 |
| moviepy | 1.0.3 |
| numpy | 1.26.4 |

### Шаг 3 — Загрузка весов модели

Веса модели хранятся в `echomimic/pretrained_weights/`:

```
pretrained_weights/
├── audio_processor/           # Whisper Tiny — извлечение аудиопризнаков (72 МБ)
│   └── whisper_tiny.pt
├── denoising_unet.pth         # Denoising UNet (~3.2 ГБ)
├── face_locator.pth           # Face Locator (~4 МБ)
├── motion_module.pth          # Motion Module (~1.7 ГБ)
├── reference_unet.pth         # Reference UNet (~3.1 ГБ)
├── sd-image-variations-diffusers/  # Stable Diffusion Image Variations (базовая модель)
└── sd-vae-ft-mse/             # VAE из Stable Diffusion (~638 МБ)
```

Веса можно скачать через:

```bash
huggingface-cli download BadToBest/EchoMimic --local-dir pretrained_weights
```

### Шаг 4 — Подготовка входных данных

Источники данных:

- **Изображения**: Первые кадры видео FaceForensics++ C23 Original → `inputs/frames/000_first.jpg`–`999_first.jpg`
  - Извлечение: `ffmpeg -y -i {video} -vframes 1 -q:v 2 {output.jpg}`
  - Источник: `/var/lib/ilanmironov@edu.hse.ru/shared/datasets/FaceForensics++_C23/Original/`
- **Аудио**: VoxCeleb2 test AAC → 50 спикеров × 4 клипа × 5 повторов
  - Источник: `/var/lib/ilanmironov@edu.hse.ru/shared/datasets/vox2_test_aac/`
  - Сконвертированы в WAV: `inputs/audio_wav/spk{NN}_clip{NN}_{speakerID}_{clipID}.wav`
  - Команда: `ffmpeg -y -v warning -i input.m4a -ac 1 -ar 16000 -c:a pcm_s16le output.wav`

Алгоритм выбора аудио (50 спикеров × 4 клипа × 5 повторов):

1. 50 спикеров выбираются из VoxCeleb2 test (сортировка по ID).
2. У каждого спикера выбираются 4 аудиоклипа.
3. Каждый клип повторяется 5 раз: `person = i // 20`, `clip = (i % 20) // 5`.
4. Итого: 50 × 4 × 5 = 1000 пар (изображение + аудио).

### Шаг 5 — Генерация конфигурации инференса

Скрипт подготовки создаёт:

- `metadata/generation_1000.yaml` — YAML-конфигурация с путями к весам и 1000 тест-кейсами
- `metadata/manifest_1000.csv` — CSV-манифест (idx, target_video, target_frame, speaker, audio_slot, audio_source_m4a, audio_m4a, audio_wav, output_name)

Формат test_cases в YAML:

```yaml
test_cases:
  /path/to/inputs/frames/000_first.jpg:
    - /path/to/inputs/audio_wav/spk000_clip00_id00017_00001.wav
  /path/to/inputs/frames/001_first.jpg:
    - /path/to/inputs/audio_wav/spk000_clip00_id00017_00001.wav
```

### Шаг 6 — Генерация

Команда запуска:

```bash
export CUDA_VISIBLE_DEVICES=3
export MPLBACKEND=agg
source /var/lib/ilanmironov@edu.hse.ru/echomimic/.venv_echomimic/bin/activate
cd /var/lib/ilanmironov@edu.hse.ru/echomimic

python -u infer_audio2vid_acc.py \
  --config /path/to/metadata/generation_1000.yaml \
  --steps 6 --fps 24 --device cuda \
  > /path/to/logs/gen.log 2>&1
```

Ключевые параметры:
| Параметр | Значение | Описание |
|----------|----------|----------|
| `--steps` | 6 | Количество шагов деноизинга (ускоренный режим) |
| `--fps` | 24 | Частота кадров выходного видео |
| `--seed` | 420 | Фиксированный seed для воспроизводимости |
| `--cfg` | 1.0 | Classifier-free guidance scale |
| `--context_frames` | 12 | Количество кадров в контексте |
| `--context_overlap` | 3 | Перекрытие между контекстными окнами |
| `--sample_rate` | 16000 | Частота дискретизации аудио |
| `sampler` | DDIM | Алгоритм семплирования |

Назначение GPU: `CUDA_VISIBLE_DEVICES=3` (физический GPU-3, используется ~14 ГБ VRAM).

Скорость генерации: ~6 минут / видео на NVIDIA GPU (15 ГБ VRAM).

### Шаг 7 — Переименование после генерации

Исходные имена файлов: `{idx}_first_{audio_name}_{resolution}_{cfg}_{time}_withaudio.mp4`

Пример: `000_first_spk000_clip00_id00017_00001_512x512_1_1756_withaudio.mp4`

Переименованы в описательный формат: `{idx}_{speaker_id}_{yt_video_id}_{clip_id}.mp4`

Пример: `000_id00017_01dfn2spqyE_00001.mp4`

- `000` — порядковый индекс (соответствует FFpp видео 000.mp4)
- `id00017` — ID спикера VoxCeleb2
- `01dfn2spqyE` — ID видео на YouTube
- `00001` — номер клипа

## Схема потока данных

```
FaceForensics++ C23 (1000 видео)      VoxCeleb2 test AAC (50 спикеров)
         ↓ ffmpeg → первый кадр                  ↓ копирование + ffmpeg → WAV
   inputs/frames/                      inputs/audio_wav/
   000_first.jpg – 999_first.jpg       spk000_clip00_id00017_00001.wav – ...
         ↓                                      ↓
         └──────────┐       ┌────────────────────┘
                    ↓       ↓
         generation_1000.yaml (1000 test_cases)
                    ↓
        Инференс EchoMimic (acc mode)
        (GPU-3, DDIM 6 steps, FPS=24)
                    ↓
          output/{date}/{time}--seed_420-512x512/
          000_first_..._withaudio.mp4
          ...
          999_first_..._withaudio.mp4
                    ↓ переименование + копирование
          shared/datasets/EchoMimic_FFpp_vox2/fake/
          000_id00017_01dfn2spqyE_00001.mp4
          ...
          999_id03524_3VavIcYEQZs_00010.mp4
```

## Структура выходного датасета

```
EchoMimic_FFpp_vox2/
├── fake/                  # 1000 сгенерированных дипфейк-видео (0.51 ГБ)
│   ├── 000_id00017_01dfn2spqyE_00001.mp4
│   ├── 001_id00017_01dfn2spqyE_00001.mp4
│   └── ...
├── original_videos/       # 1000 симлинков на исходные видео из FFpp C23
│   ├── 000.mp4 → /shared/datasets/FaceForensics++_C23/Original/000.mp4
│   ├── 001.mp4
│   └── ...
└── original_audio/        # 41 уникальный .m4a файл из VoxCeleb2
    ├── 00001.m4a
    └── ...
```

## Требования для воспроизведения

1. **Сервер с NVIDIA GPU** (рекомендуется не менее 14 ГБ VRAM)
2. **Python 3.10+** с поддержкой venv
3. **FFmpeg** (для извлечения кадров и конвертации .m4a → .wav)
4. **Репозиторий EchoMimic**: `git clone https://github.com/BadToBest/EchoMimic.git`
5. **Веса модели**: скачать через `huggingface-cli download BadToBest/EchoMimic`
6. **Исходные данные**:
   - FaceForensics++ C23 Original (1000 видео)
   - VoxCeleb2 test AAC (минимум 50 спикеров с ≥4 клипами)
7. **Ключевые скрипты** (в `workspace/datasets/EchoMimic_FFpp_vox2/`):
   - Скрипт подготовки данных (извлечение кадров, конвертация аудио, генерация YAML)
   - `infer_audio2vid_acc.py` — основной скрипт инференса (в корне репозитория)
   - Скрипт переименования выходных файлов в описательный формат
