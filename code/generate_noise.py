"""
Deprecated: This script has been moved to the `noisetool` package.

Please use the CLI instead:

    pip install noisetool
    noisetool [--type white|pink|brown] [--duration 30] [options]

Or as a Python module:

    python -m noise [options]

See README.md for full documentation.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Dict, Callable

import numpy as np
import soundfile as sf

warnings.warn(
    "code/generate_noise.py is deprecated. Use `noisetool` CLI instead.",
    DeprecationWarning,
    stacklevel=2,
)

SAMPLE_RATE: int = 44100
DURATION: int = 30
NUM_SAMPLES: int = SAMPLE_RATE * DURATION
OUTPUT_DIR: Path = Path(__file__).resolve().parent.parent / "audio"


def generate_white_noise(n_samples: int, n_channels: int = 2) -> np.ndarray:
    return np.random.uniform(-1, 1, (n_samples, n_channels)).astype(np.float32)


def generate_pink_noise(n_samples: int, n_channels: int = 2) -> np.ndarray:
    white = np.random.uniform(-1, 1, (n_samples, n_channels)).astype(np.float64)
    freq = np.fft.rfftfreq(n_samples, d=1.0 / SAMPLE_RATE)
    freq[0] = freq[1]
    pink_filter = (1.0 / np.sqrt(freq)).astype(np.float64)
    pink = np.empty_like(white)
    for ch in range(n_channels):
        fft = np.fft.rfft(white[:, ch])
        fft *= pink_filter
        pink[:, ch] = np.fft.irfft(fft, n=n_samples)
    max_val = np.max(np.abs(pink))
    if max_val > 0:
        pink /= max_val
    return pink.astype(np.float32)


def generate_brown_noise(n_samples: int, n_channels: int = 2) -> np.ndarray:
    white = np.random.uniform(-0.1, 0.1, (n_samples, n_channels)).astype(np.float64)
    brown = np.cumsum(white, axis=0)
    max_val = np.max(np.abs(brown))
    if max_val > 0:
        brown /= max_val
    return brown.astype(np.float32)


def save_wav(path: Path, data: np.ndarray, bit_depth: int = 24) -> None:
    subtype_map: Dict[int, str] = {16: "PCM_16", 24: "PCM_24", 32: "PCM_32"}
    sf.write(str(path), data, SAMPLE_RATE, subtype=subtype_map.get(bit_depth, "PCM_24"))


def save_flac(path: Path, data: np.ndarray, bit_depth: int = 24) -> None:
    sf.write(str(path), data, SAMPLE_RATE, format="FLAC", subtype=f"PCM_{bit_depth}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    noises: Dict[str, Callable[[int, int], np.ndarray]] = {
        "brown": generate_brown_noise,
        "white": generate_white_noise,
        "pink": generate_pink_noise,
    }
    for name, generator in noises.items():
        print(f"Generating {name} noise ({NUM_SAMPLES} samples, {SAMPLE_RATE} Hz)...")
        stereo = generator(NUM_SAMPLES, n_channels=2)
        mono = np.mean(stereo, axis=1, keepdims=True)
        for suffix, data in [("", stereo), ("_mono", mono)]:
            wav = OUTPUT_DIR / f"{name}_noise{suffix}.wav"
            flac = OUTPUT_DIR / f"{name}_noise{suffix}.flac"
            save_wav(wav, data, bit_depth=24)
            save_flac(flac, data, bit_depth=24)
            print(f"  Writing {wav}")
            print(f"  Writing {flac}")
    print(f"\nDone. Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
