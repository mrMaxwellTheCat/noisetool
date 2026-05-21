from __future__ import annotations

import numpy as np

from noise.preview import ascii_waveform, waveform_stats


class TestAsciiWaveform:
    def test_output_is_string(self) -> None:
        data = np.zeros((100, 2), dtype=np.float32)
        result = ascii_waveform(data, width=20, height=5)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_sine_wave(self) -> None:
        t = np.linspace(0, 1, 1000, endpoint=False)
        data = np.sin(2 * np.pi * 10 * t).astype(np.float32).reshape(-1, 1)
        result = ascii_waveform(data, width=20, height=5)
        assert "█" in result

    def test_empty_data(self) -> None:
        data = np.array([]).reshape(0, 1)
        result = ascii_waveform(data)
        assert "[no data]" in result

    def test_mono_data(self) -> None:
        data = np.random.rand(100).astype(np.float32)
        result = ascii_waveform(data, width=10, height=5)
        assert isinstance(result, str)


class TestWaveformStats:
    def test_basic_stats(self) -> None:
        data = np.random.rand(44100, 2).astype(np.float32)
        stats = waveform_stats(data, 44100)
        assert stats["Duration"] == "1.00s"
        assert stats["Channels"] == "2"
        assert stats["Sample Rate"] == "44100 Hz"

    def test_mono_stats(self) -> None:
        data = np.random.rand(22050).astype(np.float32)
        stats = waveform_stats(data, 44100)
        assert stats["Duration"] == "0.50s"
        assert stats["Channels"] == "1"

    def test_empty_stats(self) -> None:
        data = np.array([]).reshape(0, 2)
        stats = waveform_stats(data, 44100)
        assert stats["Duration"] == "0.00s"
