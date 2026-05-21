from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from noise.formats import save_aiff, save_raw


class TestSaveAiff:
    def test_basic(self, tmp_path: Path) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        path = tmp_path / "test.aiff"
        result = save_aiff(path, data, sample_rate=44100, bit_depth=24)
        assert result.exists()
        loaded, sr = sf.read(str(result))
        assert sr == 44100
        assert loaded.shape == data.shape

    def test_mono(self, tmp_path: Path) -> None:
        data = np.random.rand(500, 1).astype(np.float32)
        path = tmp_path / "mono.aiff"
        result = save_aiff(path, data, sample_rate=48000)
        assert result.exists()


class TestSaveRaw:
    def test_basic_16bit(self, tmp_path: Path) -> None:
        data = np.array([0.5, -0.5, 0.0], dtype=np.float32).reshape(-1, 1)
        path = tmp_path / "test.raw"
        result = save_raw(path, data, bit_depth=16)
        assert result.exists()
        assert result.stat().st_size == 3 * 2  # 3 samples, 2 bytes each

    def test_basic_24bit(self, tmp_path: Path) -> None:
        data = np.array([0.5, -0.5], dtype=np.float32).reshape(-1, 1)
        path = tmp_path / "test24.raw"
        result = save_raw(path, data, bit_depth=24)
        assert result.exists()

    def test_stereo(self, tmp_path: Path) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        path = tmp_path / "stereo.raw"
        result = save_raw(path, data, bit_depth=16)
        assert result.exists()
