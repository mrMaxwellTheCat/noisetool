from __future__ import annotations

import numpy as np


def _design_pre_filter() -> tuple[np.ndarray, np.ndarray]:
    """Design the ITU-R BS.1770-4 pre-filter (two-stage IIR).

    Returns:
        (sos1, sos2) second-order sections for the pre-filter.
    """
    sos1 = np.array(
        [
            [
                1.53512485958697,
                -2.69169618940638,
                1.19839281085285,
                1.0,
                -1.69065929318241,
                0.73248077421585,
            ],
        ]
    )
    sos2 = np.array(
        [
            [1.0, -2.0, 1.0, 1.0, -1.99004745483398, 0.99007225036621],
        ]
    )
    return sos1, sos2


def _apply_filter(
    data: np.ndarray,
    sos: np.ndarray,
    zi: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply a second-order IIR filter section using direct form II.

    This is a simplified DF-II implementation that avoids the scipy dependency.
    """
    n_samples = data.shape[0]
    n_channels = data.shape[1] if data.ndim > 1 else 1

    data_2d = data.reshape(-1, 1) if data.ndim == 1 else data

    b0, b1, b2, a0, a1, a2 = sos[0]
    a0_inv = 1.0 / a0

    out = np.empty_like(data_2d)

    if zi is None:
        w1 = np.zeros(n_channels)
        w2 = np.zeros(n_channels)
    else:
        w1 = zi[0].copy()
        w2 = zi[1].copy()

    for i in range(n_samples):
        x = data_2d[i]
        w0 = x - a1 * w1 - a2 * w2
        y = b0 * w0 + b1 * w1 + b2 * w2
        out[i] = a0_inv * y
        w2 = w1.copy()
        w1 = w0.copy()

    zi_out = np.stack([w1, w2])

    if data.ndim == 1:
        return out.ravel(), zi_out
    return out, zi_out


def _k_weight(data: np.ndarray) -> np.ndarray:
    """Apply K-weighting (pre-filter + RLB weighting) per ITU-R BS.1770-4.

    Note: The filter coefficients are designed for 48000 Hz but are applied
    approximately for other sample rates. For best accuracy, resample to
    48000 Hz before measurement.

    Args:
        data: Audio samples, shape (n_samples, n_channels).

    Returns:
        K-weighted audio signal, same shape as input.
    """
    sos1, sos2 = _design_pre_filter()
    filtered, _ = _apply_filter(data, sos1)
    result, _ = _apply_filter(filtered, sos2)
    return result


def measure_loudness(data: np.ndarray, sample_rate: int = 44100) -> float:  # noqa: ARG001
    """Measure integrated loudness in LUFS (ITU-R BS.1770-4).

    Args:
        data: Audio samples, shape (n_samples, n_channels). Should be float in [-1, 1].
        sample_rate: Sample rate in Hz.

    Returns:
        Integrated loudness in LUFS (typically -14 to -30 for mastered audio,
        around -3 to -6 for raw generated noise).
    """
    if data.size == 0:
        return -np.inf

    if data.ndim == 1:
        data = data.reshape(-1, 1)

    n_channels = data.shape[1]

    weighted = _k_weight(data)

    channel_powers = np.mean(weighted**2, axis=0)

    channel_weights = {1: [1.0], 2: [1.0, 1.0], 5: [1.0, 1.0, 1.0, 1.41, 1.41]}
    weights = np.array(channel_weights.get(n_channels, [1.0] * n_channels))

    weighted_power = np.sum(channel_powers * weights) / np.sum(weights)

    if weighted_power <= 0:
        return -np.inf

    return float(10.0 * np.log10(weighted_power) + 0.691)


def normalize_loudness(
    data: np.ndarray,
    target_lufs: float = -14.0,
    sample_rate: int = 44100,
) -> np.ndarray:
    """Normalize audio to a target LUFS loudness.

    Args:
        data: Audio samples, shape (n_samples, n_channels). Float in [-1, 1].
        target_lufs: Target integrated loudness in LUFS (e.g., -14 for streaming).
        sample_rate: Sample rate in Hz.

    Returns:
        Loudness-normalized audio, same shape as input.
    """
    current = measure_loudness(data, sample_rate)
    if current == -np.inf:
        return data

    gain_db = target_lufs - current
    gain_linear = 10.0 ** (gain_db / 20.0)

    adjusted = data * gain_linear

    max_val = np.max(np.abs(adjusted))
    if max_val > 1.0:
        adjusted /= max_val

    return adjusted  # type: ignore[no-any-return]
