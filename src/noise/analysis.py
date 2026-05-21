from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class AudioStats:
    duration_s: float
    n_samples: int
    n_channels: int
    sample_rate: int
    peak: float
    peak_db: float
    rms: float
    rms_db: float
    crest_factor: float
    dc_offset: float
    bit_depth: int = 24

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_table(self) -> list[tuple[str, str]]:
        return [
            ("Duration", f"{self.duration_s:.2f}s"),
            ("Samples", f"{self.n_samples:,}"),
            ("Channels", str(self.n_channels)),
            ("Sample Rate", f"{self.sample_rate} Hz"),
            ("Bit Depth", str(self.bit_depth)),
            ("Peak", f"{self.peak:.6f}"),
            ("Peak (dBFS)", f"{self.peak_db:.2f}"),
            ("RMS", f"{self.rms:.6f}"),
            ("RMS (dBFS)", f"{self.rms_db:.2f}"),
            ("Crest Factor", f"{self.crest_factor:.2f} dB"),
            ("DC Offset", f"{self.dc_offset:.8f}"),
        ]


def compute_stats(data: np.ndarray, sample_rate: int) -> AudioStats:
    """Compute comprehensive audio statistics.

    Args:
        data: Audio array, shape (n_samples, n_channels).
        sample_rate: Sample rate in Hz.

    Returns:
        AudioStats dataclass with all computed values.
    """
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    n_samples, n_channels = data.shape
    duration = n_samples / sample_rate
    peak = float(np.max(np.abs(data)))
    peak_db = 20.0 * np.log10(max(peak, 1e-10))
    rms = float(np.sqrt(np.mean(data**2)))
    rms_db = 20.0 * np.log10(max(rms, 1e-10))
    crest = peak_db - rms_db
    dc = float(np.mean(data))

    return AudioStats(
        duration_s=duration,
        n_samples=n_samples,
        n_channels=n_channels,
        sample_rate=sample_rate,
        peak=peak,
        peak_db=peak_db,
        rms=rms,
        rms_db=rms_db,
        crest_factor=crest,
        dc_offset=dc,
    )


def ascii_spectrum(data: np.ndarray, sample_rate: int, width: int = 60, height: int = 10) -> str:
    """Generate an ASCII spectrum (frequency-domain) visualization.

    Args:
        data: Audio array, shape (n_samples, n_channels). Mono preferred.
        sample_rate: Sample rate in Hz.
        width: Character width of the output.
        height: Character height (vertical resolution).

    Returns:
        A string containing the ASCII spectrum plot.
    """
    samples = data[:, 0] if data.ndim > 1 else data

    n = len(samples)
    if n < 4:
        return "[insufficient data for spectrum]"

    window = np.hanning(n)
    spectrum = np.abs(np.fft.rfft(samples * window))
    spectrum_db = 20.0 * np.log10(spectrum / np.max(spectrum) + 1e-10)
    spectrum_db = np.maximum(spectrum_db, -height * 3)

    np.fft.rfftfreq(n, d=1.0 / sample_rate)

    block_size = max(1, len(spectrum_db) // width)
    binned = np.array(
        [
            np.max(spectrum_db[i : i + block_size])
            for i in range(0, len(spectrum_db) - block_size + 1, block_size)
        ]
    )

    nyquist = sample_rate / 2
    min_val = -height * 3
    max_val = 0.0
    lines: list[list[str]] = [[" "] * len(binned) for _ in range(height)]

    for x, val in enumerate(binned):
        normalized_pos = int((val - min_val) / (max_val - min_val) * (height - 1))
        normalized_pos = max(0, min(height - 1, normalized_pos))
        for y in range(normalized_pos, height):
            if y >= 0 and y < height:
                lines[y][x] = "\u2588"

    # Add frequency labels
    if len(binned) > 10:
        labels = [
            (0, "0"),
            (len(binned) // 4, f"{nyquist / 4:.0f}Hz"),
            (len(binned) // 2, f"{nyquist / 2:.0f}Hz"),
            (3 * len(binned) // 4, f"{3 * nyquist / 4:.0f}Hz"),
        ]
        for pos, label in labels:
            if pos < len(binned):
                for j, ch in enumerate(label):
                    if pos + j < len(binned):
                        lines[0][pos + j] = ch

    return "\n".join("".join(line) for line in lines)


def save_json_stats(data: np.ndarray, sample_rate: int, path: Path) -> Path:
    """Compute stats and save as JSON.

    Returns:
        Path to the saved JSON file.
    """
    stats = compute_stats(data, sample_rate)
    path.write_text(stats.to_json(), encoding="utf-8")
    return path
