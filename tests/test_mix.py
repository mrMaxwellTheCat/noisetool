from __future__ import annotations

import numpy as np

from noise.cli import parse_mix_arg
from noise.generator import mix_noise


class TestMixNoise:
    def test_default_mix(self) -> None:
        data = mix_noise(1000, n_channels=2)
        assert data.shape == (1000, 2)
        assert data.dtype == np.float32

    def test_mono(self) -> None:
        data = mix_noise(1000, n_channels=1)
        assert data.shape == (1000, 1)

    def test_custom_weights(self) -> None:
        weights = {"white": 0.5, "pink": 0.5}
        data = mix_noise(1000, n_channels=2, weights=weights)
        assert data.shape == (1000, 2)

    def test_range(self) -> None:
        data = mix_noise(1000, n_channels=2)
        assert np.all(data >= -1.0)
        assert np.all(data <= 1.0)

    def test_reproducible(self) -> None:
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        d1 = mix_noise(1000, n_channels=2, rng=rng1)
        d2 = mix_noise(1000, n_channels=2, rng=rng2)
        np.testing.assert_array_equal(d1, d2)


class TestParseMixArg:
    def test_simple(self) -> None:
        result = parse_mix_arg("pink=0.7,white=0.3")
        assert result == {"pink": 0.7, "white": 0.3}

    def test_single(self) -> None:
        result = parse_mix_arg("pink=1.0")
        assert result == {"pink": 1.0}

    def test_no_weight(self) -> None:
        result = parse_mix_arg("pink")
        assert result == {"pink": 1.0}
