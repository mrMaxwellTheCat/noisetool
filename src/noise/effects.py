from __future__ import annotations

import numpy as np


def dc_blocker(data: np.ndarray, alpha: float = 0.995) -> np.ndarray:
    """Remove DC offset using a high-pass IIR filter.

    y[n] = x[n] - x[n-1] + alpha * y[n-1]

    Args:
        data: Audio array, shape (n_samples, n_channels).
        alpha: Filter coefficient (0.99-0.999 typical, higher = steeper cutoff).

    Returns:
        DC-blocked audio, same shape as input.
    """
    out = np.empty_like(data)
    x_prev = np.zeros(data.shape[1])
    y_prev = np.zeros(data.shape[1])
    for i in range(data.shape[0]):
        y = data[i] - x_prev + alpha * y_prev
        out[i] = y
        x_prev = data[i]
        y_prev = y
    return out


def fade_in(data: np.ndarray, duration: float, sample_rate: int) -> np.ndarray:
    """Apply a linear fade-in at the start.

    Args:
        data: Audio array, shape (n_samples, n_channels).
        duration: Fade duration in seconds.
        sample_rate: Sample rate in Hz.

    Returns:
        Audio with fade-in applied.
    """
    n_fade = int(duration * sample_rate)
    if n_fade <= 0 or n_fade > data.shape[0]:
        return data
    fade_curve = np.linspace(0.0, 1.0, n_fade).reshape(-1, 1)
    out = data.copy()
    out[:n_fade] *= fade_curve
    return out  # type: ignore[no-any-return]


def fade_out(data: np.ndarray, duration: float, sample_rate: int) -> np.ndarray:
    """Apply a linear fade-out at the end.

    Args:
        data: Audio array, shape (n_samples, n_channels).
        duration: Fade duration in seconds.
        sample_rate: Sample rate in Hz.

    Returns:
        Audio with fade-out applied.
    """
    n_fade = int(duration * sample_rate)
    if n_fade <= 0 or n_fade > data.shape[0]:
        return data
    fade_curve = np.linspace(1.0, 0.0, n_fade).reshape(-1, 1)
    out = data.copy()
    out[-n_fade:] *= fade_curve
    return out  # type: ignore[no-any-return]


def reverse(data: np.ndarray) -> np.ndarray:
    """Reverse audio in time.

    Args:
        data: Audio array, shape (n_samples, n_channels).

    Returns:
        Time-reversed audio.
    """
    return data[::-1]


def invert_phase(data: np.ndarray) -> np.ndarray:
    """Invert the phase (multiply by -1).

    Args:
        data: Audio array, shape (n_samples, n_channels).

    Returns:
        Phase-inverted audio.
    """
    return -data


def normalize_peak(data: np.ndarray, target_db: float = -1.0) -> np.ndarray:
    """Peak-normalize audio to a target level in dB.

    Args:
        data: Audio array, shape (n_samples, n_channels).
        target_db: Target peak level in dBFS (e.g., -1.0 to prevent clipping).

    Returns:
        Peak-normalized audio.
    """
    current_peak = float(np.max(np.abs(data)))
    if current_peak <= 0:
        return data
    target_peak = 10.0 ** (target_db / 20.0)
    return data * (target_peak / current_peak)  # type: ignore[no-any-return]
