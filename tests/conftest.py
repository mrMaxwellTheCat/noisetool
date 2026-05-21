from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(42)


@pytest.fixture
def sample_rate() -> int:
    return 44100


@pytest.fixture
def short_samples() -> int:
    return 2048
