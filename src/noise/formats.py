from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from noise.utils import SAMPLE_RATE


def save_aiff(
    path: Path, data: np.ndarray, sample_rate: int = SAMPLE_RATE, bit_depth: int = 24
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    subtype = {16: "PCM_16", 24: "PCM_24", 32: "PCM_32"}.get(bit_depth, "PCM_24")
    sf.write(str(path), data, sample_rate, format="AIFF", subtype=subtype)
    return path


def save_ogg(
    path: Path,
    data: np.ndarray,
    sample_rate: int = SAMPLE_RATE,
    bit_depth: int = 24,  # noqa: ARG001
) -> Path:
    """Save audio data as OGG Vorbis format.

    Args:
        path: Output file path.
        data: Audio array, shape (n_samples, n_channels).
        sample_rate: Sample rate in Hz.
        bit_depth: Ignored for OGG (always uses Vorbis compression).

    Returns:
        Path to the saved file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), data, sample_rate, format="OGG")
    return path


def save_raw(
    path: Path,
    data: np.ndarray,
    sample_rate: int = SAMPLE_RATE,  # noqa: ARG001
    bit_depth: int = 24,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dtype_map = {16: np.int16, 24: np.int32, 32: np.int32}
    dtype = dtype_map.get(bit_depth, np.int32)
    max_int = {16: 32767, 24: 8388607, 32: 2147483647}.get(bit_depth, 2147483647)
    int_data = (data * max_int).astype(dtype)
    if bit_depth == 24:
        bytes_ = bytearray()
        for sample in int_data.ravel():
            val = int(sample) & 0xFFFFFF
            if val >= 0x800000:
                val -= 0x1000000
            bytes_.extend(val.to_bytes(3, "little", signed=True))
        path.write_bytes(bytes_)
    else:
        path.write_bytes(int_data.tobytes())
    return path
