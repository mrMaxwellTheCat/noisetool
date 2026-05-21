from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from noise.cli import parse_args


class TestParseArgs:
    def test_defaults(self) -> None:
        args = parse_args([])
        assert args.type == "all"
        assert args.duration == 30.0
        assert args.sample_rate == 44100
        assert not args.mono
        assert not args.stereo
        assert args.output_dir == Path("audio")
        assert args.format == "all"
        assert args.bit_depth == 24
        assert args.lufs is None
        assert not args.measure
        assert args.seed is None
        assert not args.verbose

    def test_noise_type(self) -> None:
        args = parse_args(["--type", "pink"])
        assert args.type == "pink"

    def test_duration(self) -> None:
        args = parse_args(["-d", "60"])
        assert args.duration == 60.0

    def test_sample_rate(self) -> None:
        args = parse_args(["-r", "96000"])
        assert args.sample_rate == 96000

    def test_mono(self) -> None:
        args = parse_args(["--mono"])
        assert args.mono
        assert not args.stereo

    def test_stereo(self) -> None:
        args = parse_args(["--stereo"])
        assert args.stereo
        assert not args.mono

    def test_output_dir(self) -> None:
        args = parse_args(["-o", "/tmp/noise"])
        assert args.output_dir == Path("/tmp/noise")

    def test_format_wav(self) -> None:
        args = parse_args(["-f", "wav"])
        assert args.format == "wav"

    def test_bit_depth(self) -> None:
        args = parse_args(["--bit-depth", "16"])
        assert args.bit_depth == 16

    def test_lufs(self) -> None:
        args = parse_args(["--lufs", "-14"])
        assert args.lufs == -14.0

    def test_measure(self) -> None:
        args = parse_args(["--measure"])
        assert args.measure

    def test_seed(self) -> None:
        args = parse_args(["--seed", "42"])
        assert args.seed == 42

    def test_verbose(self) -> None:
        args = parse_args(["-v"])
        assert args.verbose

    def test_version(self) -> None:

        with pytest.raises(SystemExit) as exc, contextlib.redirect_stdout(io.StringIO()):
            parse_args(["--version"])
        assert exc.value.code == 0

    def test_list(self) -> None:
        args = parse_args(["--list"])
        assert args.list

    def test_peak(self) -> None:
        args = parse_args(["--peak", "-1.0"])
        assert args.peak == -1.0

    def test_log_file(self) -> None:
        args = parse_args(["--log-file", "/tmp/noise.log"])
        assert args.log_file == Path("/tmp/noise.log")

    def test_invalid_noise_type(self) -> None:
        with pytest.raises(SystemExit):
            parse_args(["--type", "green"])
