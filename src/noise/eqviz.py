from __future__ import annotations

import numpy as np


def plot_filter_response(
    filter_type: str,
    params: list[float],
    sample_rate: int = 44100,
    width: int = 50,
    height: int = 10,
) -> str:
    """Generate an ASCII plot of a filter's frequency response.

    Args:
        filter_type: 'lowpass', 'highpass', or 'bandpass'.
        params: Filter parameters [cutoff] or [low, high].
        sample_rate: Sample rate in Hz.
        width: Character width of the plot.
        height: Character height.

    Returns:
        ASCII string showing the filter response curve.
    """
    nyquist = sample_rate / 2
    freqs = np.linspace(0, nyquist, width)

    if filter_type == "lowpass" and len(params) >= 1:
        cutoff = params[0]
        response = 1.0 / (1.0 + (freqs / cutoff) ** 4)
    elif filter_type == "highpass" and len(params) >= 1:
        cutoff = params[0]
        response = 1.0 / (1.0 + (cutoff / (freqs + 1e-10)) ** 4)
    elif filter_type == "bandpass" and len(params) >= 2:
        low, high = params[0], params[1]
        low_resp = 1.0 / (1.0 + (low / (freqs + 1e-10)) ** 4)
        high_resp = 1.0 / (1.0 + (freqs / high) ** 4)
        response = low_resp * high_resp
    else:
        response = np.ones(width)

    response_db = 20.0 * np.log10(np.maximum(response, 1e-6))

    lines: list[list[str]] = [[" "] * width for _ in range(height)]
    db_min, db_max = -48, 3

    for x in range(width):
        norm = int((response_db[x] - db_min) / (db_max - db_min) * (height - 1))
        norm = max(0, min(height - 1, norm))
        for y in range(norm, height):
            lines[y][x] = "█"

    # Axis at 0 dB
    db_zero = int((0 - db_min) / (db_max - db_min) * (height - 1))
    db_zero = max(0, min(height - 1, db_zero))
    for x in range(width):
        if lines[db_zero][x] == " ":
            lines[db_zero][x] = "─"

    # Labels
    lines[0][0] = "0"
    lines[height - 1][0] = f"{nyquist:.0f}"
    width // 2
    cutoff_pos = int((params[0] if len(params) >= 1 else nyquist / 2) / nyquist * (width - 1))
    cutoff_pos = max(0, min(width - 1, cutoff_pos))
    if height > 2:
        lines[1][cutoff_pos] = "▼"

    return "\n".join("".join(line) for line in lines)
