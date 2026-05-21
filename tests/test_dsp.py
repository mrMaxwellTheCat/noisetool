from __future__ import annotations

import numpy as np

from noise.effects import compressor, dither, normalize_rms


class TestDither:
    def test_shape(self) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        out = dither(data, 16)
        assert out.shape == data.shape

    def test_high_bitrate(self) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        out = dither(data, 24)
        np.testing.assert_array_equal(data, out)

    def test_noise_added(self) -> None:
        data = np.zeros((1000, 1), dtype=np.float32)
        out = dither(data, 8)
        assert np.any(out != 0)


class TestCompressor:
    def test_shape(self) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        out = compressor(data, -20, 4, sample_rate=44100)
        assert out.shape == data.shape

    def test_reduces_peaks(self) -> None:
        data = np.zeros((1000, 1), dtype=np.float32)
        data[100] = 1.0
        data[200] = 0.5
        out = compressor(data, -30, 10, sample_rate=44100)
        assert float(np.max(out)) < 1.0


class TestNormalizeRMS:
    def test_shape(self) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        out = normalize_rms(data, -18)
        assert out.shape == data.shape

    def test_target_level(self) -> None:
        data = np.ones((1000, 1), dtype=np.float32)
        out = normalize_rms(data, -6)
        rms = float(np.sqrt(np.mean(out**2)))
        assert abs(20 * np.log10(rms) - (-6)) < 1.0

    def test_silence(self) -> None:
        data = np.zeros((100, 2), dtype=np.float32)
        out = normalize_rms(data, -18)
        np.testing.assert_array_equal(data, out)
