from __future__ import annotations

import numpy as np

from noise.cli import make_loopable


class TestMakeLoopable:
    def test_output_shape(self) -> None:
        data = np.random.rand(1000, 2).astype(np.float32)
        result = make_loopable(data, crossfade_samples=128)
        assert result.shape == data.shape

    def test_mono(self) -> None:
        data = np.random.rand(1000).astype(np.float32).reshape(-1, 1)
        result = make_loopable(data, crossfade_samples=64)
        assert result.shape == data.shape

    def test_crossfade_edges(self) -> None:
        data = np.ones((1000, 1), dtype=np.float32)
        result = make_loopable(data, crossfade_samples=100)
        assert result[0, 0] < 1.0
        assert result[-1, 0] < 1.0
        assert result[500, 0] == 1.0

    def test_crossfade_too_large(self) -> None:
        data = np.ones((100, 2), dtype=np.float32)
        result = make_loopable(data, crossfade_samples=100)
        np.testing.assert_array_equal(data, result)
