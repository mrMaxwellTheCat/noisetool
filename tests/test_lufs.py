from __future__ import annotations

import numpy as np

from noise.lufs import measure_loudness, normalize_loudness


class TestMeasureLoudness:
    def test_silence(self, sample_rate: int) -> None:
        data = np.zeros((44100, 2), dtype=np.float32)
        assert measure_loudness(data, sample_rate) == -np.inf

    def test_full_scale_sine(self, sample_rate: int) -> None:
        t = np.linspace(0, 1, sample_rate, endpoint=False)
        data = np.sin(2 * np.pi * 1000 * t).astype(np.float32).reshape(-1, 1)
        loudness = measure_loudness(data, sample_rate)
        assert np.isfinite(loudness)
        assert loudness < 0

    def test_white_noise_loudness(self, sample_rate: int) -> None:
        rng = np.random.default_rng(42)
        data = rng.uniform(-1, 1, (sample_rate, 2)).astype(np.float32)
        loudness = measure_loudness(data, sample_rate)
        assert np.isfinite(loudness)
        assert -10 < loudness < 0

    def test_mono(self, sample_rate: int) -> None:
        rng = np.random.default_rng(42)
        data = rng.uniform(-1, 1, (sample_rate, 1)).astype(np.float32)
        loudness = measure_loudness(data, sample_rate)
        assert np.isfinite(loudness)

    def test_empty_data(self) -> None:
        data = np.array([]).reshape(0, 2)
        assert measure_loudness(data, 44100) == -np.inf


class TestNormalizeLoudness:
    def test_output_shape(self, sample_rate: int) -> None:
        rng = np.random.default_rng(42)
        data = rng.uniform(-1, 1, (sample_rate, 2)).astype(np.float32)
        normalized = normalize_loudness(data, -14.0, sample_rate)
        assert normalized.shape == data.shape
        assert normalized.dtype == data.dtype

    def test_range_preserved(self, sample_rate: int) -> None:
        rng = np.random.default_rng(42)
        data = rng.uniform(-1, 1, (sample_rate, 2)).astype(np.float32)
        normalized = normalize_loudness(data, -14.0, sample_rate)
        assert np.all(normalized >= -1.0)
        assert np.all(normalized <= 1.0)

    def test_target_loudness(self, sample_rate: int) -> None:
        rng = np.random.default_rng(42)
        data = rng.uniform(-1, 1, (sample_rate, 2)).astype(np.float32)
        target = -20.0
        normalized = normalize_loudness(data, target, sample_rate)
        measured = measure_loudness(normalized, sample_rate)
        assert abs(measured - target) < 1.0

    def test_silence_unchanged(self, sample_rate: int) -> None:
        data = np.zeros((sample_rate, 2), dtype=np.float32)
        normalized = normalize_loudness(data, -14.0, sample_rate)
        np.testing.assert_array_equal(data, normalized)
