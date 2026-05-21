from __future__ import annotations

import numpy as np

from noise.generator import (
    generate_blue_noise,
    generate_brown_noise,
    generate_grey_noise,
    generate_pink_noise,
    generate_violet_noise,
    generate_white_noise,
)


class TestWhiteNoise:
    def test_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_white_noise(short_samples, n_channels=2, rng=rng)
        assert data.shape == (short_samples, 2)
        assert data.dtype == np.float32

    def test_mono_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_white_noise(short_samples, n_channels=1, rng=rng)
        assert data.shape == (short_samples, 1)

    def test_range(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_white_noise(short_samples, n_channels=2, rng=rng)
        assert np.all(data >= -1.0)
        assert np.all(data <= 1.0)

    def test_mean_near_zero(self, rng: np.random.Generator) -> None:
        data = generate_white_noise(100000, n_channels=2, rng=rng)
        assert abs(np.mean(data)) < 0.01

    def test_reproducible(self, short_samples: int) -> None:
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        d1 = generate_white_noise(short_samples, n_channels=2, rng=rng1)
        d2 = generate_white_noise(short_samples, n_channels=2, rng=rng2)
        np.testing.assert_array_equal(d1, d2)


class TestPinkNoise:
    def test_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_pink_noise(short_samples, n_channels=2, rng=rng)
        assert data.shape == (short_samples, 2)
        assert data.dtype == np.float32

    def test_mono_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_pink_noise(short_samples, n_channels=1, rng=rng)
        assert data.shape == (short_samples, 1)

    def test_range(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_pink_noise(short_samples, n_channels=2, rng=rng)
        assert np.all(data >= -1.0)
        assert np.all(data <= 1.0)

    def test_low_freq_emphasis(self, rng: np.random.Generator) -> None:
        data = generate_pink_noise(8192, n_channels=1, rng=rng).ravel()
        spectrum = np.abs(np.fft.rfft(data))
        low = np.mean(spectrum[: len(spectrum) // 8])
        high = np.mean(spectrum[7 * len(spectrum) // 8 :])
        assert low > high, "Pink noise should have more low-frequency energy"

    def test_reproducible(self, short_samples: int) -> None:
        rng1 = np.random.default_rng(99)
        rng2 = np.random.default_rng(99)
        d1 = generate_pink_noise(short_samples, n_channels=2, rng=rng1)
        d2 = generate_pink_noise(short_samples, n_channels=2, rng=rng2)
        np.testing.assert_array_equal(d1, d2)


class TestBrownNoise:
    def test_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_brown_noise(short_samples, n_channels=2, rng=rng)
        assert data.shape == (short_samples, 2)
        assert data.dtype == np.float32

    def test_mono_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_brown_noise(short_samples, n_channels=1, rng=rng)
        assert data.shape == (short_samples, 1)

    def test_range(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_brown_noise(short_samples, n_channels=2, rng=rng)
        assert np.all(data >= -1.0)
        assert np.all(data <= 1.0)

    def test_low_freq_emphasis(self, rng: np.random.Generator) -> None:
        data = generate_brown_noise(8192, n_channels=1, rng=rng).ravel()
        spectrum = np.abs(np.fft.rfft(data))
        low = np.mean(spectrum[: len(spectrum) // 8])
        high = np.mean(spectrum[7 * len(spectrum) // 8 :])
        assert low > high, "Brown noise should have more low-frequency energy"

    def test_reproducible(self, short_samples: int) -> None:
        rng1 = np.random.default_rng(77)
        rng2 = np.random.default_rng(77)
        d1 = generate_brown_noise(short_samples, n_channels=2, rng=rng1)
        d2 = generate_brown_noise(short_samples, n_channels=2, rng=rng2)
        np.testing.assert_array_equal(d1, d2)


class TestDefaultRNG:
    def test_no_rng_provided(self, short_samples: int) -> None:
        data = generate_white_noise(short_samples, n_channels=1)
        assert data.shape == (short_samples, 1)


class TestBlueNoise:
    def test_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_blue_noise(short_samples, n_channels=2, rng=rng)
        assert data.shape == (short_samples, 2)
        assert data.dtype == np.float32

    def test_range(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_blue_noise(short_samples, n_channels=2, rng=rng)
        assert np.all(data >= -1.0)
        assert np.all(data <= 1.0)

    def test_high_freq_emphasis(self, rng: np.random.Generator) -> None:
        data = generate_blue_noise(8192, n_channels=1, rng=rng).ravel()
        spectrum = np.abs(np.fft.rfft(data))
        low = np.mean(spectrum[: len(spectrum) // 8])
        high = np.mean(spectrum[7 * len(spectrum) // 8 :])
        assert high > low, "Blue noise should have more high-frequency energy"

    def test_reproducible(self, short_samples: int) -> None:
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        d1 = generate_blue_noise(short_samples, n_channels=2, rng=rng1)
        d2 = generate_blue_noise(short_samples, n_channels=2, rng=rng2)
        np.testing.assert_array_equal(d1, d2)


class TestVioletNoise:
    def test_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_violet_noise(short_samples, n_channels=2, rng=rng)
        assert data.shape == (short_samples, 2)

    def test_range(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_violet_noise(short_samples, n_channels=2, rng=rng)
        assert np.all(data >= -1.0)
        assert np.all(data <= 1.0)

    def test_high_freq_emphasis(self, rng: np.random.Generator) -> None:
        data = generate_violet_noise(8192, n_channels=1, rng=rng).ravel()
        spectrum = np.abs(np.fft.rfft(data))
        low = np.mean(spectrum[: len(spectrum) // 8])
        high = np.mean(spectrum[7 * len(spectrum) // 8 :])
        assert high > low, "Violet noise should have more high-frequency energy"

    def test_reproducible(self, short_samples: int) -> None:
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        d1 = generate_violet_noise(short_samples, n_channels=2, rng=rng1)
        d2 = generate_violet_noise(short_samples, n_channels=2, rng=rng2)
        np.testing.assert_array_equal(d1, d2)


class TestGreyNoise:
    def test_shape(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_grey_noise(short_samples, n_channels=2, rng=rng)
        assert data.shape == (short_samples, 2)

    def test_range(self, rng: np.random.Generator, short_samples: int) -> None:
        data = generate_grey_noise(short_samples, n_channels=2, rng=rng)
        assert np.all(data >= -1.0)
        assert np.all(data <= 1.0)

    def test_reproducible(self, short_samples: int) -> None:
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        d1 = generate_grey_noise(short_samples, n_channels=2, rng=rng1)
        d2 = generate_grey_noise(short_samples, n_channels=2, rng=rng2)
        np.testing.assert_array_equal(d1, d2)
