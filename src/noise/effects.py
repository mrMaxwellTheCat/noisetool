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


def lowpass(data: np.ndarray, cutoff_hz: float, sample_rate: int) -> np.ndarray:
    n = data.shape[0]
    fft_data = np.fft.rfft(data, axis=0)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    fft_data[freqs > cutoff_hz] = 0
    result = np.fft.irfft(fft_data, n=n, axis=0)
    max_val = np.max(np.abs(result))
    if max_val > 0:
        result /= max_val
    return result.astype(data.dtype)


def highpass(data: np.ndarray, cutoff_hz: float, sample_rate: int) -> np.ndarray:
    n = data.shape[0]
    fft_data = np.fft.rfft(data, axis=0)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    fft_data[freqs < cutoff_hz] = 0
    result = np.fft.irfft(fft_data, n=n, axis=0)
    max_val = np.max(np.abs(result))
    if max_val > 0:
        result /= max_val
    return result.astype(data.dtype)


def bandpass(data: np.ndarray, low_hz: float, high_hz: float, sample_rate: int) -> np.ndarray:
    n = data.shape[0]
    fft_data = np.fft.rfft(data, axis=0)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    fft_data[(freqs < low_hz) | (freqs > high_hz)] = 0
    result = np.fft.irfft(fft_data, n=n, axis=0)
    max_val = np.max(np.abs(result))
    if max_val > 0:
        result /= max_val
    return result.astype(data.dtype)


def apply_envelope(
    data: np.ndarray,
    attack: float,
    decay: float,
    sustain_level: float,
    release: float,
    sample_rate: int,
) -> np.ndarray:
    n = data.shape[0]
    n_attack = int(attack * sample_rate)
    n_decay = int(decay * sample_rate)
    n_release = int(release * sample_rate)

    envelope = np.ones(n, dtype=np.float64)

    if n_attack > 0:
        attack_curve = np.linspace(0.0, 1.0, min(n_attack, n))
        envelope[: min(n_attack, n)] = attack_curve[: min(n_attack, n)]

    attack_end = min(n_attack, n)
    decay_end = min(attack_end + n_decay, n)
    decay_len = decay_end - attack_end
    if decay_len > 0:
        envelope[attack_end:decay_end] = np.linspace(1.0, sustain_level, decay_len)

    if n_attack + n_decay < n and sustain_level < 1.0:
        envelope[n_attack + n_decay : n - n_release] = sustain_level

    if n_release > 0:
        release_start = max(0, n - n_release)
        release_len = n - release_start
        if release_len > 0:
            envelope[release_start:] = np.linspace(sustain_level, 0.0, release_len)

    return (data * envelope.reshape(-1, 1)).astype(data.dtype)


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
