from __future__ import annotations

import numpy as np

from noise.effects import (
    dc_blocker,
    fade_in,
    fade_out,
    invert_phase,
    normalize_peak,
    reverse,
)


class TestDCBlocker:
    def test_output_shape(self) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        out = dc_blocker(data)
        assert out.shape == data.shape
        assert out.dtype == data.dtype

    def test_removes_dc(self) -> None:
        data = np.ones((1000, 1), dtype=np.float32) * 0.5
        out = dc_blocker(data, alpha=0.9)
        assert abs(float(np.mean(out[-100:]))) < 0.01


class TestFadeIn:
    def test_fade_applied(self) -> None:
        data = np.ones((1000, 2), dtype=np.float32)
        out = fade_in(data, 0.5, 1000)
        assert out[0, 0] < 0.1
        assert out[-1, 0] == 1.0

    def test_zero_fade(self) -> None:
        data = np.ones((100, 2), dtype=np.float32)
        out = fade_in(data, 0.0, 44100)
        np.testing.assert_array_equal(data, out)

    def test_longer_than_data(self) -> None:
        data = np.ones((10, 2), dtype=np.float32)
        out = fade_in(data, 10.0, 44100)
        np.testing.assert_array_equal(data, out)


class TestFadeOut:
    def test_fade_applied(self) -> None:
        data = np.ones((1000, 2), dtype=np.float32)
        out = fade_out(data, 0.5, 1000)
        assert out[-1, 0] < 0.1
        assert out[0, 0] == 1.0


class TestReverse:
    def test_reverse_mono(self) -> None:
        data = np.array([[1], [2], [3]], dtype=np.float32)
        out = reverse(data)
        np.testing.assert_array_equal(out, np.array([[3], [2], [1]], dtype=np.float32))

    def test_reverse_stereo(self) -> None:
        data = np.array([[1, 2], [3, 4]], dtype=np.float32)
        out = reverse(data)
        np.testing.assert_array_equal(out, np.array([[3, 4], [1, 2]], dtype=np.float32))


class TestInvertPhase:
    def test_invert(self) -> None:
        data = np.array([[1, -2], [3, -4]], dtype=np.float32)
        out = invert_phase(data)
        np.testing.assert_array_equal(out, np.array([[-1, 2], [-3, 4]], dtype=np.float32))


class TestNormalizePeak:
    def test_normalize(self) -> None:
        data = np.random.rand(100, 2).astype(np.float32)
        out = normalize_peak(data, -6.0)
        peak = float(np.max(np.abs(out)))
        assert abs(peak - 0.5) < 0.01

    def test_silence(self) -> None:
        data = np.zeros((100, 2), dtype=np.float32)
        out = normalize_peak(data)
        np.testing.assert_array_equal(data, out)
