from __future__ import annotations

import numpy as np

from noise.effects import bitcrush, modulate_amplitude, pan, stereo_width


class TestStereoWidth:
    def test_mono_unchanged(self) -> None:
        data = np.random.rand(100, 1).astype(np.float32)
        out = stereo_width(data, 2.0)
        np.testing.assert_array_equal(data, out)

    def test_zero_width(self) -> None:
        data = np.array([[1, -1], [0.5, -0.5]], dtype=np.float32)
        out = stereo_width(data, 0.0)
        assert abs(out[0, 0] - out[0, 1]) < 0.01

    def test_shape(self) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        out = stereo_width(data, 1.5)
        assert out.shape == data.shape


class TestPan:
    def test_shape(self) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        out = pan(data, 0.5)
        assert out.shape == data.shape

    def test_mono_to_stereo(self) -> None:
        data = np.random.rand(100, 1).astype(np.float32)
        out = pan(data, 0.0)
        assert out.shape == (100, 2)

    def test_hard_left(self) -> None:
        data = np.ones((10, 2), dtype=np.float32)
        out = pan(data, -1.0)
        assert out[0, 1] == 0.0
        assert out[0, 0] > 0


class TestModulateAmplitude:
    def test_shape(self) -> None:
        data = np.ones((1000, 2), dtype=np.float32)
        out = modulate_amplitude(data, 5.0, 0.5, 1000)
        assert out.shape == data.shape

    def test_modulation_applied(self) -> None:
        data = np.ones((1000, 1), dtype=np.float32)
        out = modulate_amplitude(data, 10.0, 1.0, 1000)
        assert float(np.min(out)) < 0.5
        assert float(np.max(out)) == 1.0


class TestBitcrush:
    def test_shape(self) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        out = bitcrush(data, 8)
        assert out.shape == data.shape

    def test_quantization(self) -> None:
        data = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32).reshape(-1, 1)
        out = bitcrush(data, 4)
        uniq = len(np.unique(out))
        assert uniq < len(data)  # Quantization reduced unique values

    def test_high_bits(self) -> None:
        data = np.random.rand(100, 1).astype(np.float32)
        out = bitcrush(data, 24)
        assert out.shape == data.shape
