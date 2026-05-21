from __future__ import annotations

import numpy as np


def ascii_waveform(
    data: np.ndarray,
    width: int = 60,
    height: int = 10,
    channel: int = 0,
) -> str:
    """Generate an ASCII waveform visualization of audio data.

    Args:
        data: Audio array of shape (n_samples, n_channels).
        width: Character width of the output.
        height: Character height (vertical resolution).
        channel: Channel index to visualize.

    Returns:
        A string containing the ASCII waveform.
    """
    samples = data if data.ndim == 1 else data[:, channel]

    n = len(samples)
    if n == 0:
        return "[no data]"

    block_size = max(1, n // width)
    peaks = np.max(np.abs(samples[: block_size * width].reshape(-1, block_size)), axis=1)

    max_val = np.max(peaks) if np.max(peaks) > 0 else 1.0
    normalized = (peaks / max_val * (height - 1)).astype(int)

    lines: list[list[str]] = [[" "] * width for _ in range(height)]
    mid = height // 2

    for x, peak in enumerate(normalized):
        for y in range(mid - peak, mid + peak + 1):
            if 0 <= y < height:
                lines[y][x] = "█"

    for x in range(width):
        lines[mid][x] = "▄"

    # Add axis labels
    if width > 15:
        lines[0][0] = "+"
        lines[0][width - 1] = "+"
        for x in range(min(6, width)):
            lines[height - 1][x] = "0"
        for x in range(max(0, width - 6), width):
            lines[height - 1][x] = str(n)

    return "\n".join("".join(line) for line in lines)


def waveform_stats(data: np.ndarray, sample_rate: int) -> dict[str, str]:
    """Compute summary statistics for audio data."""
    if data.size == 0:
        return {
            "Duration": "0.00s",
            "Channels": str(data.shape[1] if data.ndim > 1 else 1),
            "Sample Rate": f"{sample_rate} Hz",
            "Samples": "0",
            "Peak": "0.0000",
            "RMS": "0.0000",
        }
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    n_channels = data.shape[1]
    duration = data.shape[0] / sample_rate

    stats: dict[str, str] = {}
    stats["Duration"] = f"{duration:.2f}s"
    stats["Channels"] = str(n_channels)
    stats["Sample Rate"] = f"{sample_rate} Hz"
    stats["Samples"] = f"{data.shape[0]:,}"
    stats["Peak"] = f"{float(np.max(np.abs(data))):.4f}"
    stats["RMS"] = f"{float(np.sqrt(np.mean(data**2))):.4f}"

    if n_channels >= 2:
        left, right = data[:, 0], data[:, 1]
        diff = left - right
        stats["Stereo Diff"] = f"{float(np.sqrt(np.mean(diff**2))):.4f}"

    return stats
