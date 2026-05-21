from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from noise.analysis import ascii_spectrum, compute_stats, save_json_stats


class TestComputeStats:
    def test_silence(self) -> None:
        data = np.zeros((44100, 2), dtype=np.float32)
        stats = compute_stats(data, 44100)
        assert stats.peak == 0.0
        assert stats.rms == 0.0
        assert stats.dc_offset == 0.0

    def test_full_scale(self) -> None:
        data = np.ones((1000, 1), dtype=np.float32)
        stats = compute_stats(data, 44100)
        assert stats.peak == 1.0
        assert stats.peak_db == 0.0

    def test_stats_table(self) -> None:
        data = np.random.rand(44100, 2).astype(np.float32)
        stats = compute_stats(data, 44100)
        table = stats.to_table()
        assert len(table) == 11
        assert table[0][0] == "Duration"

    def test_to_json(self) -> None:
        data = np.random.rand(100, 1).astype(np.float32)
        stats = compute_stats(data, 100)
        parsed = json.loads(stats.to_json())
        assert parsed["duration_s"] == 1.0
        assert parsed["n_samples"] == 100


class TestAsciiSpectrum:
    def test_output_string(self) -> None:
        data = np.random.rand(4096).astype(np.float32)
        result = ascii_spectrum(data, 44100, width=20, height=5)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_insufficient_data(self) -> None:
        data = np.array([1, 2, 3], dtype=np.float32)
        result = ascii_spectrum(data, 44100)
        assert "insufficient" in result


class TestSaveJsonStats:
    def test_saves_file(self, tmp_path: Path) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        path = tmp_path / "stats.json"
        result = save_json_stats(data, 44100, path)
        assert result.exists()
        content = json.loads(path.read_text())
        assert "peak" in content
        assert "rms" in content
