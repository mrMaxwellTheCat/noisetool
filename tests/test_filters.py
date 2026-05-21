from __future__ import annotations

import numpy as np

from noise.effects import apply_envelope, bandpass, highpass, lowpass


class TestLowpass:
    def test_shape(self) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        out = lowpass(data, 1000, 44100)
        assert out.shape == data.shape

    def test_removes_high_freq(self) -> None:
        data = np.random.rand(4096, 1).astype(np.float32)
        out = lowpass(data, 100, 44100)
        orig_high = np.mean(np.abs(np.fft.rfft(data.ravel())[-100:]))
        out_high = np.mean(np.abs(np.fft.rfft(out.ravel())[-100:]))
        assert out_high < orig_high


class TestHighpass:
    def test_shape(self) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        out = highpass(data, 1000, 44100)
        assert out.shape == data.shape

    def test_removes_low_freq(self) -> None:
        data = np.random.rand(4096, 1).astype(np.float32)
        out = highpass(data, 1000, 44100)
        orig_low = np.mean(np.abs(np.fft.rfft(data.ravel())[:10]))
        out_low = np.mean(np.abs(np.fft.rfft(out.ravel())[:10]))
        assert out_low < orig_low


class TestBandpass:
    def test_shape(self) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        out = bandpass(data, 200, 2000, 44100)
        assert out.shape == data.shape


class TestApplyEnvelope:
    def test_shape(self) -> None:
        data = np.ones((1000, 2), dtype=np.float32)
        out = apply_envelope(data, 0.1, 0.1, 0.7, 0.2, 1000)
        assert out.shape == data.shape

    def test_attack(self) -> None:
        data = np.ones((1000, 1), dtype=np.float32)
        out = apply_envelope(data, 0.1, 0.0, 1.0, 0.0, 1000)
        assert out[0, 0] < out[-1, 0]

    def test_release(self) -> None:
        data = np.ones((1000, 1), dtype=np.float32)
        out = apply_envelope(data, 0.0, 0.0, 1.0, 0.2, 1000)
        assert out[-1, 0] < out[0, 0]
