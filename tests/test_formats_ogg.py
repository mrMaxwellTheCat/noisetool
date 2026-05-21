from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from noise.formats import save_ogg


class TestSaveOgg:
    def test_basic(self, tmp_path: Path) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        path = tmp_path / "test.ogg"
        result = save_ogg(path, data, sample_rate=44100)
        assert result.exists()
        loaded, sr = sf.read(str(result))
        assert sr == 44100
        assert loaded.shape[0] == data.shape[0]

    def test_mono(self, tmp_path: Path) -> None:
        data = np.random.rand(500, 1).astype(np.float32)
        path = tmp_path / "mono.ogg"
        result = save_ogg(path, data, sample_rate=48000)
        assert result.exists()
