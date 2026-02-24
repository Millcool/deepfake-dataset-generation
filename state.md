# Текущее состояние проекта (2026-02-24)

## Завершённые датасеты

| Алгоритм | Модальность | Видео | Статус | shared/ | GitLab |
|-----------|-------------|-------|--------|---------|--------|
| EchoMimic V1 | audio-to-face | 1000/1000 | DONE | EchoMimic_FFpp_vox2/ | deepfake2025/echomimic |
| MuseTalk | audio-to-face | 1000/1000 | DONE | MuseTalk_FFpp_vox2/ | deepfake2025/musetalk |

## Генерация в процессе

| Алгоритм | Модальность | Видео | GPU | Примечание |
|-----------|-------------|-------|-----|------------|
| EchoMimic V3 | audio-to-face | 294/1000 | GPU-0 | PID 269595, dir: echomimic_v3/ |
| FaceFusion BlendSwap | face-to-face | ~9/1000 | GPU-1 | BlendSwap_FFpp |
| FaceFusion GHOST | face-to-face | ~12/1000 | GPU-2 | GHOST_FFpp |
| FaceFusion UniFace | face-to-face | ~1/1000 | GPU-3 | UniFace_FFpp |

## Требует действий

### VideoRetalking — 22 недостающих видео
- **Статус**: 978/1000 готово, 22 видео не сгенерированы из-за ошибок face detection
- **Проблема**: VR требует лицо на КАЖДОМ кадре; у 22 видео есть кадры без лица
- **Решение готово**: `fix_22/` — 22 видео обрезаны до сегментов с лицом (21 @ 5с, 1 @ 4с)
- **Ожидание**: свободный GPU для перезапуска (все 4 заняты)
- **Проблемные индексы**: 016, 019, 040, 056, 105, 202, 243, 343, 442, 489, 509, 582, 590, 674, 722, 776, 812, 824, 850, 861, 891, 957
- **Подробности**: videoretalking_problem_videos.md

## README / документация

| Алгоритм | Локальный файл | На сервере | GitLab |
|-----------|---------------|------------|--------|
| EchoMimic V1 | echomimic_readme.md | echomimic/workspace/.../readme.md | deepfake2025/echomimic |
| MuseTalk | — | musetalk/workspace/.../readme.md | deepfake2025/musetalk |

## Что дальше

1. Дождаться завершения FaceFusion (3 × 1000 видео, ~18 часов)
2. Запустить перегенерацию 22 VR видео (когда GPU освободится)
3. Дождаться EchoMimic V3 (706 видео осталось)
4. Для каждого завершённого датасета: README + скрипты + загрузка на GitLab + копирование в shared/
