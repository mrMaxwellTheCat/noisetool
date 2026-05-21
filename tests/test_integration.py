from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from noise.cli import main
from noise.lufs import measure_loudness


def test_cli_generates_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    main(
        [
            "--type",
            "white",
            "--duration",
            "0.1",
            "--sample-rate",
            "44100",
            "--mono",
            "-f",
            "wav",
            "-o",
            str(output_dir),
            "--seed",
            "42",
        ]
    )
    files = list(output_dir.iterdir())
    assert len(files) == 1
    wav_file = files[0]
    assert wav_file.suffix == ".wav"
    assert "white" in wav_file.stem
    assert "mono" in wav_file.stem
    data, sr = sf.read(str(wav_file))
    assert sr == 44100
    n_expected = int(0.1 * 44100)
    assert abs(len(data) - n_expected) <= 1


def test_cli_measure(caplog: pytest.LogCaptureFixture) -> None:
    import logging

    caplog.set_level(logging.INFO)
    main(
        [
            "--measure",
            "--type",
            "white",
            "--duration",
            "0.1",
            "--seed",
            "42",
        ]
    )
    assert any("White" in rec.message and "LUFS" in rec.message for rec in caplog.records)


def test_cli_reproducible(tmp_path: Path) -> None:
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    main(
        [
            "--type",
            "white",
            "--duration",
            "0.1",
            "--mono",
            "-f",
            "wav",
            "-o",
            str(out1),
            "--seed",
            "123",
        ]
    )
    main(
        [
            "--type",
            "white",
            "--duration",
            "0.1",
            "--mono",
            "-f",
            "wav",
            "-o",
            str(out2),
            "--seed",
            "123",
        ]
    )
    f1 = list(out1.iterdir())[0]
    f2 = list(out2.iterdir())[0]
    d1, _ = sf.read(str(f1))
    d2, _ = sf.read(str(f2))
    np.testing.assert_array_equal(d1, d2)


def test_lufs_normalization(tmp_path: Path) -> None:
    output_dir = tmp_path / "lufs_test"
    main(
        [
            "--type",
            "pink",
            "--duration",
            "0.5",
            "--mono",
            "-f",
            "wav",
            "-o",
            str(output_dir),
            "--lufs",
            "-14",
            "--seed",
            "99",
        ]
    )
    files = list(output_dir.iterdir())
    assert len(files) >= 1
    data, sr = sf.read(str(files[0]))
    measured = measure_loudness(
        data.reshape(-1, 1) if data.ndim == 1 else data,
        sr,
    )
    assert abs(measured - (-14.0)) < 3.0


def test_all_noise_types(tmp_path: Path) -> None:
    output_dir = tmp_path / "all_types"
    main(
        [
            "--type",
            "all",
            "--duration",
            "0.05",
            "-f",
            "wav",
            "-o",
            str(output_dir),
            "--seed",
            "7",
        ]
    )
    files = sorted(str(f.name) for f in output_dir.iterdir())
    assert any("white" in f for f in files)
    assert any("pink" in f for f in files)
    assert any("brown" in f for f in files)


def test_verbose_logging(tmp_path: Path) -> None:
    output_dir = tmp_path / "verbose_test"
    main(
        [
            "--type",
            "white",
            "--duration",
            "0.05",
            "--mono",
            "-f",
            "wav",
            "-o",
            str(output_dir),
            "--verbose",
            "--seed",
            "1",
        ]
    )
    files = list(output_dir.iterdir())
    assert len(files) >= 1
