from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

SAMPLE_RATE: int = 44100

BIT_DEPTH_MAP: dict[int, str] = {
    16: "PCM_16",
    24: "PCM_24",
    32: "PCM_32",
}


def save_wav(
    path: Path,
    data: np.ndarray,
    sample_rate: int = SAMPLE_RATE,
    bit_depth: int = 24,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    subtype = BIT_DEPTH_MAP.get(bit_depth, "PCM_24")
    sf.write(str(path), data, sample_rate, subtype=subtype)
    return path


def save_flac(
    path: Path,
    data: np.ndarray,
    sample_rate: int = SAMPLE_RATE,
    bit_depth: int = 24,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), data, sample_rate, format="FLAC", subtype=f"PCM_{bit_depth}")
    return path
