from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from noise.cli import parse_args
from noise.config import generate_example_config, load_config


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

    def test_preview(self) -> None:
        args = parse_args(["--preview"])
        assert args.preview

    def test_play(self) -> None:
        args = parse_args(["--play"])
        assert args.play

    def test_stats(self) -> None:
        args = parse_args(["--stats"])
        assert args.stats

    def test_spectrum(self) -> None:
        args = parse_args(["--spectrum"])
        assert args.spectrum

    def test_json(self) -> None:
        args = parse_args(["--json", "stats.json"])
        assert args.json == Path("stats.json")

    def test_dry_run(self) -> None:
        args = parse_args(["--dry-run"])
        assert args.dry_run

    def test_format_aiff(self) -> None:
        args = parse_args(["-f", "aiff"])
        assert args.format == "aiff"

    def test_format_raw(self) -> None:
        args = parse_args(["-f", "raw"])
        assert args.format == "raw"

    def test_loop(self) -> None:
        args = parse_args(["--loop"])
        assert args.loop

    def test_continuous(self) -> None:
        args = parse_args(["--continuous"])
        assert args.continuous

    def test_parallel(self) -> None:
        args = parse_args(["--parallel"])
        assert args.parallel

    def test_workers(self) -> None:
        args = parse_args(["--workers", "4"])
        assert args.workers == 4

    def test_benchmark(self) -> None:
        args = parse_args(["--benchmark"])
        assert args.benchmark

    def test_format_ogg(self) -> None:
        args = parse_args(["-f", "ogg"])
        assert args.format == "ogg"

    def test_mix(self) -> None:
        args = parse_args(["--mix", "pink=0.7,white=0.3"])
        assert args.mix == "pink=0.7,white=0.3"

    def test_lowpass(self) -> None:
        args = parse_args(["--lowpass", "1000"])
        assert args.lowpass == 1000.0

    def test_highpass(self) -> None:
        args = parse_args(["--highpass", "100"])
        assert args.highpass == 100.0

    def test_bandpass(self) -> None:
        args = parse_args(["--bandpass", "20,20000"])
        assert args.bandpass == "20,20000"

    def test_envelope(self) -> None:
        args = parse_args(["--envelope", "0.1,0.2,0.7,0.3"])
        assert args.envelope == "0.1,0.2,0.7,0.3"

    def test_width(self) -> None:
        args = parse_args(["--width", "0.5"])
        assert args.width == 0.5

    def test_pan(self) -> None:
        args = parse_args(["--pan", "-0.5"])
        assert args.pan == -0.5

    def test_tremolo(self) -> None:
        args = parse_args(["--tremolo", "5,0.5"])
        assert args.tremolo == "5,0.5"

    def test_bitcrush(self) -> None:
        args = parse_args(["--bitcrush", "8"])
        assert args.bitcrush == 8

    def test_dither(self) -> None:
        args = parse_args(["--dither", "16"])
        assert args.dither == 16

    def test_compressor(self) -> None:
        args = parse_args(["--compressor", "-20,4"])
        assert args.compressor == "-20,4"

    def test_rms(self) -> None:
        args = parse_args(["--rms", "-18"])
        assert args.rms == -18.0

    def test_invalid_noise_type(self) -> None:
        with pytest.raises(SystemExit):
            parse_args(["--type", "green"])

    def test_pattern(self) -> None:
        args = parse_args(["--pattern", "{type}_{format}_{sr}"])
        assert args.pattern == "{type}_{format}_{sr}"

    def test_seeds(self) -> None:
        args = parse_args(["--seeds", "1,2,3,42,100"])
        assert args.seeds == "1,2,3,42,100"


def test_config_load_json(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    generate_example_config(config_file)
    assert config_file.exists()
    config = load_config(config_file)
    assert config.noise_type == "all"
    assert config.duration == 30.0
    assert config.sample_rate == 44100
    assert config.bit_depth == 24
    assert config.lufs == -14.0
    assert config.seed == 42


def test_generate_completion() -> None:
    from noise.completion import SHELL_COMPLETION_SCRIPT

    assert "_noisetool_completion" in SHELL_COMPLETION_SCRIPT
    assert "noisetool" in SHELL_COMPLETION_SCRIPT
