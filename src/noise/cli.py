from __future__ import annotations

import argparse
import concurrent.futures
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np

from noise import __version__
from noise.analysis import ascii_spectrum, compute_stats, save_json_stats
from noise.completion import SHELL_COMPLETION_SCRIPT, add_completion_args
from noise.config import generate_example_config, load_config
from noise.effects import (
    apply_envelope,
    bandpass,
    bitcrush,
    compressor,
    dc_blocker,
    dither,
    fade_in,
    fade_out,
    highpass,
    invert_phase,
    lowpass,
    modulate_amplitude,
    normalize_rms,
    pan,
    stereo_width,
)
from noise.effects import reverse as reverse_audio
from noise.formats import save_aiff, save_ogg, save_raw
from noise.generator import (
    generate_blue_noise,
    generate_brown_noise,
    generate_grey_noise,
    generate_pink_noise,
    generate_violet_noise,
    generate_white_noise,
    mix_noise,
)
from noise.lufs import measure_loudness
from noise.lufs import normalize_loudness as lufs_normalize
from noise.preview import ascii_waveform
from noise.ui import (
    console,
    make_progress,
    print_banner,
    print_error,
    print_info,
    print_noise_table,
    print_results_table,
    print_success,
    print_warning,
)
from noise.utils import SAMPLE_RATE, save_flac, save_wav

logger = logging.getLogger("noisetool")

NOISE_GENERATORS = {
    "white": generate_white_noise,
    "pink": generate_pink_noise,
    "brown": generate_brown_noise,
    "blue": generate_blue_noise,
    "violet": generate_violet_noise,
    "grey": generate_grey_noise,
}

NOISE_DESCRIPTIONS = {
    "white": "Flat power spectrum across all frequencies",
    "pink": "Power decreases 3 dB/octave (1/f spectrum)",
    "brown": "Power decreases 6 dB/octave (1/f^2 spectrum)",
    "blue": "Power increases 3 dB/octave (rising spectrum)",
    "violet": "Power increases 6 dB/octave (rising spectrum)",
    "grey": "Psychoacoustic equal-loudness noise",
}

FORMATS = {
    "wav": save_wav,
    "flac": save_flac,
    "aiff": save_aiff,
    "raw": save_raw,
    "ogg": save_ogg,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="noisetool",
        description="Generate high-quality noise audio files (white, pink, brown, blue, violet, grey).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  noisetool                           Generate all noise types (defaults)\n"
            "  noisetool --type white --mono       Generate white noise, mono only\n"
            "  noisetool --type pink --duration 60 --sample-rate 96000\n"
            "  noisetool --type brown --lufs -23   Normalize to broadcast loudness\n"
            "  noisetool --type all --seed 42      Reproducible output\n"
        ),
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        default="all",
        choices=["all", "white", "pink", "brown", "blue", "violet", "grey"],
        help="Noise type to generate (default: all)",
    )

    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=30.0,
        help="Duration in seconds (default: 30)",
    )

    parser.add_argument(
        "-r",
        "--sample-rate",
        type=int,
        default=SAMPLE_RATE,
        help=f"Sample rate in Hz (default: {SAMPLE_RATE})",
    )

    parser.add_argument(
        "--mono",
        action="store_true",
        default=False,
        help="Generate mono audio only",
    )

    parser.add_argument(
        "--stereo",
        action="store_true",
        default=False,
        help="Generate stereo audio only",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("audio"),
        help="Output directory (default: audio/)",
    )

    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="all",
        choices=["all", "wav", "flac", "aiff", "raw", "ogg"],
        help="Output format (default: both wav and flac)",
    )

    parser.add_argument(
        "--bit-depth",
        type=int,
        default=24,
        choices=[16, 24, 32],
        help="Bit depth for audio files (default: 24)",
    )

    parser.add_argument(
        "--lufs",
        type=float,
        default=None,
        metavar="TARGET",
        help="Target loudness in LUFS for normalization (e.g., -14 for streaming, -23 for broadcast)",
    )

    parser.add_argument(
        "--measure",
        action="store_true",
        default=False,
        help="Measure and display loudness of generated audio without saving",
    )

    parser.add_argument(
        "--peak",
        type=float,
        default=None,
        metavar="LEVEL",
        help="Peak normalize to target level in dB (e.g., -1.0 to prevent clipping)",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible generation",
    )

    parser.add_argument(
        "--benchmark",
        action="store_true",
        default=False,
        help="Run performance benchmark of all noise generators and exit",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        default=False,
        help="List available noise types with descriptions and exit",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"noisetool {__version__}",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose / debug output",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write log output to a file in addition to stderr",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        default=False,
        help="Run in interactive wizard mode",
    )

    parser.add_argument(
        "--no-banner",
        action="store_true",
        default=False,
        help="Suppress the startup banner",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        metavar="FILE",
        help="Load generation config from JSON or YAML file",
    )
    parser.add_argument(
        "--example-config",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write an example config file and exit",
    )
    add_completion_args(parser)

    parser.add_argument(
        "--mix",
        type=str,
        default=None,
        metavar="TYPE1=WEIGHT,TYPE2=WEIGHT,...",
        help="Mix multiple noise types with weights (e.g., pink=0.7,white=0.3)",
    )

    parser.add_argument(
        "--pattern",
        type=str,
        default=None,
        metavar="TEMPLATE",
        help="Custom filename pattern. Variables: {type}, {channels}, {format}, {sr}, {bits}, {seed}",
    )

    parser.add_argument(
        "--seeds",
        type=str,
        default=None,
        metavar="SEEDS",
        help="Generate with multiple seeds (comma-separated). E.g., 1,2,3,42,100",
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        default=False,
        help="Show ASCII waveform preview of generated audio",
    )

    parser.add_argument(
        "--play",
        action="store_true",
        default=False,
        help="Play generated audio through system audio output",
    )

    parser.add_argument(
        "--dc-block",
        action="store_true",
        default=False,
        help="Apply DC offset removal filter",
    )

    parser.add_argument(
        "--fade-in",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Apply linear fade-in at start (duration in seconds)",
    )

    parser.add_argument(
        "--fade-out",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Apply linear fade-out at end (duration in seconds)",
    )

    parser.add_argument(
        "--reverse",
        action="store_true",
        default=False,
        help="Reverse audio in time",
    )

    parser.add_argument(
        "--invert",
        action="store_true",
        default=False,
        help="Invert audio phase (multiply by -1)",
    )

    parser.add_argument(
        "--lowpass",
        type=float,
        default=None,
        metavar="HZ",
        help="Apply low-pass filter with cutoff frequency in Hz",
    )

    parser.add_argument(
        "--highpass",
        type=float,
        default=None,
        metavar="HZ",
        help="Apply high-pass filter with cutoff frequency in Hz",
    )

    parser.add_argument(
        "--bandpass",
        type=str,
        default=None,
        metavar="LOW,HIGH",
        help="Apply band-pass filter (e.g., 20,20000)",
    )

    parser.add_argument(
        "--envelope",
        type=str,
        default=None,
        metavar="A,D,S,R",
        help="Apply ADSR envelope (e.g., 0.1,0.2,0.7,0.3 for attack,decay,sustain,release)",
    )

    parser.add_argument(
        "--width",
        type=float,
        default=None,
        metavar="WIDTH",
        help="Stereo width (0.0=mono, 1.0=original, >1.0=wider). Stereo only.",
    )

    parser.add_argument(
        "--pan",
        type=float,
        default=None,
        metavar="PAN",
        help="Pan position (-1.0=left, 0.0=center, 1.0=right)",
    )

    parser.add_argument(
        "--tremolo",
        type=str,
        default=None,
        metavar="RATE,DEPTH",
        help="Amplitude modulation (tremolo). E.g., 5,0.5",
    )

    parser.add_argument(
        "--info",
        type=Path,
        default=None,
        metavar="FILE",
        help="Show detailed info about an existing audio file",
    )

    parser.add_argument(
        "--bitcrush",
        type=int,
        default=None,
        metavar="BITS",
        help="Bitcrushing (1-24 bits). Lower = more lo-fi.",
    )

    parser.add_argument(
        "--dither",
        type=int,
        default=None,
        metavar="BITS",
        help="Apply dithering for target bit depth (e.g., 16)",
    )

    parser.add_argument(
        "--compressor",
        type=str,
        default=None,
        metavar="THRESH,RATIO",
        help="Apply dynamic range compression (e.g., -20,4)",
    )

    parser.add_argument(
        "--rms",
        type=float,
        default=None,
        metavar="DBFS",
        help="RMS-normalize to target level in dBFS (e.g., -18)",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Show detailed audio statistics after generation",
    )

    parser.add_argument(
        "--eq-viz",
        action="store_true",
        default=False,
        help="Show EQ frequency response plot when using filters",
    )

    parser.add_argument(
        "--spectrum",
        action="store_true",
        default=False,
        help="Show ASCII frequency spectrum visualization",
    )

    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        metavar="FILE",
        help="Save audio statistics as JSON file",
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        default=False,
        help="Generate files in parallel using multiple threads",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        metavar="N",
        help="Number of worker threads for parallel generation (default: CPU count)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be generated without creating files",
    )

    parser.add_argument(
        "--loop",
        action="store_true",
        default=False,
        help="Generate seamless looping noise (cross-fade start/end to avoid clicks)",
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        default=False,
        help="Generate noise continuously until interrupted (writes sequential files)",
    )

    return parser.parse_args(argv)


def _generate_one(
    noise_type: str,
    n_samples: int,
    n_channels: int,
    sample_rate: int,
    rng_seed: int | None,
    lufs_target: float | None,
    peak_target: float | None,
    apply_dc_block: bool,
    fade_in_sec: float | None,
    fade_out_sec: float | None,
    apply_reverse: bool,
    apply_invert: bool,
    output_dir: Path,
    bit_depth: int,
    formats: list[str],
    mix_weights: dict[str, float] | None = None,
    pattern: str | None = None,
) -> list[Path]:
    rng = np.random.default_rng(rng_seed) if rng_seed is not None else None
    if mix_weights is not None:
        data = mix_noise(n_samples, n_channels=n_channels, weights=mix_weights, rng=rng)
    else:
        data = NOISE_GENERATORS[noise_type](n_samples, n_channels=n_channels, rng=rng)

    if lufs_target is not None:
        data = lufs_normalize(data, target_lufs=lufs_target, sample_rate=sample_rate)

    if apply_dc_block:
        data = dc_blocker(data)
    if fade_in_sec is not None:
        data = fade_in(data, fade_in_sec, sample_rate)
    if fade_out_sec is not None:
        data = fade_out(data, fade_out_sec, sample_rate)
    if apply_reverse:
        data = reverse_audio(data)
    if apply_invert:
        data = invert_phase(data)

    if peak_target is not None:
        current_peak = float(np.max(np.abs(data)))
        if current_peak > 0:
            target_peak = 10.0 ** (peak_target / 20.0)
            data = data * (target_peak / current_peak)

    files: list[Path] = []
    for fmt in formats:
        if pattern:
            ch_label = "mono" if n_channels == 1 else "stereo"
            filename = pattern.format(
                type=noise_type,
                channels=ch_label,
                format=fmt,
                sr=sample_rate,
                bits=bit_depth,
                seed=rng_seed if rng_seed is not None else 0,
            )
        else:
            channel_label = "mono" if n_channels == 1 else ""
            suffix = f"_{channel_label}" if channel_label else ""
            filename = f"{noise_type}_noise{suffix}.{fmt}"
        filepath = output_dir / filename
        saver = FORMATS[fmt]
        saver(filepath, data, sample_rate=sample_rate, bit_depth=bit_depth)
        files.append(filepath)

    return files


def make_loopable(data: np.ndarray, crossfade_samples: int = 256) -> np.ndarray:
    """Apply a fade-in/fade-out at the boundaries to make noise seamless for looping.

    Uses a linear cross-fade between the end and beginning of the signal.

    Args:
        data: Audio array, shape (n_samples, n_channels).
        crossfade_samples: Number of samples for the crossfade region.

    Returns:
        Loopable audio (slightly shorter due to crossfade).
    """
    n = data.shape[0]
    if crossfade_samples >= n // 2:
        return data
    fade_up = np.linspace(0.0, 1.0, crossfade_samples).reshape(-1, 1)
    fade_down = np.linspace(1.0, 0.0, crossfade_samples).reshape(-1, 1)
    out = data.copy()
    out[:crossfade_samples] *= fade_up
    out[-crossfade_samples:] *= fade_down
    overlap = (data[:crossfade_samples] * fade_down + data[-crossfade_samples:] * fade_up) / 2
    out[-crossfade_samples:] += overlap * (1 - fade_down)
    out[:crossfade_samples] += overlap * (1 - fade_up)
    return out  # type: ignore[no-any-return]


def parse_mix_arg(mix_str: str) -> dict[str, float]:
    """Parse a mix argument string like 'pink=0.7,white=0.3' into a dict."""
    weights: dict[str, float] = {}
    for part in mix_str.split(","):
        part = part.strip()
        if "=" in part:
            noise_type, weight_str = part.split("=", 1)
            weights[noise_type.strip()] = float(weight_str.strip())
        else:
            weights[part] = 1.0
    return weights


def _run_benchmark(n_samples: int = 441000, sample_rate: int = 44100) -> None:
    """Run a performance benchmark of all noise generators."""
    import time

    rng = np.random.default_rng(42)
    from rich.table import Table

    from noise.ui import console

    results: list[tuple[str, float, float, float]] = []
    gen_funcs = {
        "white": generate_white_noise,
        "pink": generate_pink_noise,
        "brown": generate_brown_noise,
        "blue": generate_blue_noise,
        "violet": generate_violet_noise,
        "grey": generate_grey_noise,
    }

    console.print(
        f"[bold]Benchmark:[/] {n_samples} samples ({n_samples / sample_rate:.1f}s at {sample_rate} Hz)"
    )
    console.print()

    for name, func in gen_funcs.items():
        # Warmup
        func(1024, n_channels=2, rng=rng)

        # Benchmark
        start = time.perf_counter()
        for _ in range(5):
            func(n_samples, n_channels=2, rng=rng)
        elapsed = time.perf_counter() - start
        avg_time = elapsed / 5
        realtime_ratio = (n_samples / sample_rate) / avg_time

        data = func(n_samples, n_channels=2, rng=rng)
        loudness = measure_loudness(data, sample_rate)
        results.append((name, avg_time, realtime_ratio, loudness))

    table = Table(title="Generation Speed Benchmark")
    table.add_column("Noise Type", style="cyan")
    table.add_column("Avg Time (s)", style="yellow", justify="right")
    table.add_column("Real-time Ratio", style="green", justify="right")
    table.add_column("Loudness (LUFS)", style="magenta", justify="right")
    for name, t, ratio, loudness in results:
        table.add_row(name, f"{t:.4f}", f"{ratio:.1f}x", f"{loudness:.2f}")
    console.print(table)
    console.print("[dim]Higher real-time ratio = faster than real-time[/]")


def _generate_from_wizard(config: dict[str, Any]) -> None:
    noise_types = config["noise_types"]
    sample_rate = config["sample_rate"]
    duration = config["duration"]
    n_samples = int(sample_rate * duration)
    n_channels_list = config["n_channels"]
    formats = config["formats"]
    bit_depth = config["bit_depth"]
    lufs_target = config["lufs"]
    peak_target = config["peak"]
    seed = config["seed"]
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed) if seed is not None else None

    files_created: list[Path] = []
    progress = make_progress()
    total = len(noise_types) * len(n_channels_list) * len(formats)
    task = progress.add_task("Generating...", total=total)

    with progress:
        for noise_type in noise_types:
            for n_channels in n_channels_list:
                data = NOISE_GENERATORS[noise_type](n_samples, n_channels=n_channels, rng=rng)

                if config.get("dc_block"):
                    data = dc_blocker(data)
                if config.get("fade_in"):
                    data = fade_in(data, config["fade_in"], sample_rate)
                if config.get("fade_out"):
                    data = fade_out(data, config["fade_out"], sample_rate)
                if config.get("lowpass"):
                    data = lowpass(data, config["lowpass"], sample_rate)
                if config.get("highpass"):
                    data = highpass(data, config["highpass"], sample_rate)
                if config.get("width") is not None:
                    data = stereo_width(data, config["width"])
                if config.get("tremolo"):
                    parts = [float(x) for x in config["tremolo"].split(",")]
                    if len(parts) == 2:
                        data = modulate_amplitude(data, parts[0], parts[1], sample_rate)

                if lufs_target is not None:
                    data = lufs_normalize(data, target_lufs=lufs_target, sample_rate=sample_rate)
                if peak_target is not None:
                    peak = float(np.max(np.abs(data)))
                    if peak > 0:
                        target = 10.0 ** (peak_target / 20.0)
                        data = data * (target / peak)
                suffix = "_mono" if n_channels == 1 else ""
                for fmt in formats:
                    filename = f"{noise_type}_noise{suffix}.{fmt}"
                    filepath = output_dir / filename
                    FORMATS[fmt](filepath, data, sample_rate=sample_rate, bit_depth=bit_depth)
                    files_created.append(filepath)
                    progress.advance(task)

    print_results_table(files_created, output_dir)
    print_success(f"Done \u2014 {len(files_created)} file(s) saved to {output_dir}")


def _show_file_info(path: Path) -> None:
    """Display detailed information about an audio file."""
    import soundfile as sf

    data, sr = sf.read(str(path))
    stats = compute_stats(data, sr)
    size = path.stat().st_size

    from rich.table import Table

    table = Table(title=f"File Info: [cyan]{path.name}[/]", border_style="blue")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("Path", str(path.resolve()))
    table.add_row("Size", f"{size:,} bytes ({size / 1024:.1f} KB)")
    table.add_row("Format", str(path.suffix).upper())

    for prop, val in stats.to_table():
        table.add_row(prop, val)

    console.print(table)


def _main(argv: list[str] | None = None) -> None:
    import sys as _sys

    no_cli_args = (argv is None and len(_sys.argv) <= 1) or (argv is not None and len(argv) == 0)
    if no_cli_args:
        from noise.interactive import run_wizard

        wizard_config = run_wizard()
        _generate_from_wizard(wizard_config)
        return

    args = parse_args(argv)

    if args.info is not None:
        _show_file_info(args.info)
        return

    if args.benchmark:
        sample_rate = args.sample_rate
        n_samples = int(sample_rate * args.duration)
        _run_benchmark(n_samples=n_samples, sample_rate=sample_rate)
        return

    if args.example_config is not None:
        generate_example_config(args.example_config)
        print_success(f"Example config written to {args.example_config}")
        return

    if args.generate_completion is not None:
        print(SHELL_COMPLETION_SCRIPT)
        return

    fmt = "%(asctime)s %(levelname)s: %(message)s" if args.verbose else "%(levelname)s: %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if args.log_file is not None:
        args.log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(str(args.log_file)))
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format=fmt,
        handlers=handlers,
        datefmt="%H:%M:%S",
    )

    if not args.no_banner:
        print_banner()

    if args.list:
        print_noise_table(NOISE_DESCRIPTIONS)
        return

    if args.config is not None:
        config = load_config(args.config)
        args.type = config.noise_type
        args.duration = config.duration
        args.sample_rate = config.sample_rate
        args.format = "all"
        args.bit_depth = config.bit_depth
        args.lufs = config.lufs
        args.peak = config.peak
        args.seed = config.seed
        args.output_dir = Path(config.output_dir)

    if args.interactive:
        wizard_config = run_wizard()
        args.type = "custom"
        args.duration = wizard_config["duration"]
        args.sample_rate = wizard_config["sample_rate"]
        args.bit_depth = wizard_config["bit_depth"]
        args.lufs = wizard_config["lufs"]
        args.peak = wizard_config["peak"]
        args.seed = wizard_config["seed"]
        args.output_dir = Path(wizard_config["output_dir"])
        args.no_banner = True
        noise_types = wizard_config["noise_types"]
        channel_configs = wizard_config["n_channels"]
        format_configs = wizard_config["formats"]

    sample_rate = args.sample_rate
    n_samples = int(sample_rate * args.duration)
    seeds_to_use = [int(s.strip()) for s in args.seeds.split(",")] if args.seeds else [args.seed]
    rng = np.random.default_rng(args.seed) if args.seed is not None else None

    if not args.interactive:
        if args.mix is not None:
            noise_types = ["mixed"]
            mix_weights = parse_mix_arg(args.mix)
        else:
            noise_types = list(NOISE_GENERATORS.keys()) if args.type == "all" else [args.type]
            mix_weights = None
        channel_configs = (
            [1, 2] if not args.mono and not args.stereo else ([1] if args.mono else [2])
        )
        format_configs = ["wav", "flac"] if args.format == "all" else [args.format]
    else:
        mix_weights = None

    if args.dry_run:
        print_info("Dry run \u2014 no files will be created:")
        for noise_type in noise_types:
            for n_channels in channel_configs:
                label = "mono" if n_channels == 1 else "stereo"
                for fmt in format_configs:
                    if args.pattern:
                        filename = args.pattern.format(
                            type=noise_type,
                            channels=label,
                            format=fmt,
                            sr=sample_rate,
                            bits=args.bit_depth,
                            seed=args.seed if args.seed is not None else 0,
                        )
                    else:
                        suffix = "_mono" if n_channels == 1 else ""
                        filename = f"{noise_type}_noise{suffix}.{fmt}"
                    print_info(f"  {filename} ({label}, {n_samples} samples)")
        return

    if args.measure:
        print_info("Measuring loudness (no files will be saved):")
        for noise_type in noise_types:
            if mix_weights is not None:
                data = mix_noise(n_samples, n_channels=2, weights=mix_weights, rng=rng)
            else:
                data = NOISE_GENERATORS[noise_type](n_samples, n_channels=2, rng=rng)
            loudness = measure_loudness(data, sample_rate)
            console.print(
                f"  [yellow]{noise_type.capitalize():8}[/] noise: [bold]{loudness:>7.2f} LUFS[/]"
            )
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir = output_dir.resolve()

    files_created: list[Path] = []

    if args.parallel:
        seeds_to_use_par = (
            [int(s.strip()) for s in args.seeds.split(",")] if args.seeds else [args.seed]
        )
        n_workers = args.workers or None
        tasks: list[dict[str, Any]] = []
        for noise_type in noise_types:
            for n_channels in channel_configs:
                for seed_val in seeds_to_use_par:
                    tasks.append(
                        {
                            "noise_type": noise_type,
                            "n_samples": n_samples,
                            "n_channels": n_channels,
                            "sample_rate": sample_rate,
                            "rng_seed": seed_val,
                            "lufs_target": args.lufs,
                            "peak_target": args.peak,
                            "apply_dc_block": args.dc_block,
                            "fade_in_sec": args.fade_in,
                            "fade_out_sec": args.fade_out,
                            "apply_reverse": args.reverse,
                            "apply_invert": args.invert,
                            "output_dir": output_dir,
                            "bit_depth": args.bit_depth,
                            "formats": format_configs,
                            "mix_weights": mix_weights,
                            "pattern": args.pattern,
                        }
                    )

        print_info(f"Generating {len(tasks)} task(s) with parallel worker(s)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(_generate_one, **t) for t in tasks]
            for future in concurrent.futures.as_completed(futures):
                files_created.extend(future.result())

        print_results_table(files_created, output_dir)
        print_success(f"Done \u2014 {len(files_created)} file(s) saved to {output_dir}")
        return

    if args.continuous:
        print_info(f"Continuous generation mode \u2014 writing to {output_dir}")
        print_info("Press Ctrl+C to stop")
        counter = 0
        try:
            while True:
                for noise_type in noise_types:
                    for n_channels in channel_configs:
                        rng = np.random.default_rng()
                        if mix_weights is not None:
                            data = mix_noise(
                                n_samples, n_channels=n_channels, weights=mix_weights, rng=rng
                            )
                        else:
                            data = NOISE_GENERATORS[noise_type](
                                n_samples, n_channels=n_channels, rng=rng
                            )
                        if args.loop:
                            data = make_loopable(data)
                        if args.lufs is not None:
                            data = lufs_normalize(
                                data, target_lufs=args.lufs, sample_rate=sample_rate
                            )
                        for fmt in format_configs:
                            if args.pattern:
                                ch_label = "mono" if n_channels == 1 else "stereo"
                                filename = args.pattern.format(
                                    type=noise_type,
                                    channels=ch_label,
                                    format=fmt,
                                    sr=sample_rate,
                                    bits=args.bit_depth,
                                    seed=0,
                                )
                            else:
                                channel_label = "mono" if n_channels == 1 else ""
                                suffix = f"_{channel_label}" if channel_label else ""
                                filename = f"{noise_type}_noise{suffix}_{counter:04d}.{fmt}"
                            filepath = output_dir / filename
                            saver = FORMATS[fmt]
                            saver(filepath, data, sample_rate=sample_rate, bit_depth=args.bit_depth)
                        counter += 1
                if args.verbose:
                    print_info(f"Batch {counter} complete")
        except KeyboardInterrupt:
            print_success(
                f"Continuous generation stopped. {counter} batch(es) saved to {output_dir}"
            )
        return

    progress = make_progress()
    total_tasks = len(noise_types) * len(channel_configs) * len(format_configs) * len(seeds_to_use)
    task = progress.add_task("Generating...", total=total_tasks)

    with progress:
        for noise_type in noise_types:
            for n_channels in channel_configs:
                for seed_val in seeds_to_use:
                    rng = np.random.default_rng(seed_val) if seed_val is not None else None
                    if mix_weights is not None:
                        data = mix_noise(
                            n_samples, n_channels=n_channels, weights=mix_weights, rng=rng
                        )
                    else:
                        data = NOISE_GENERATORS[noise_type](
                            n_samples, n_channels=n_channels, rng=rng
                        )

                    if args.lufs is not None:
                        before = measure_loudness(data, sample_rate)
                        data = lufs_normalize(data, target_lufs=args.lufs, sample_rate=sample_rate)
                        after = measure_loudness(data, sample_rate)
                        logger.debug(
                            "Loudness: %.2f LUFS -> %.2f LUFS (target: %.1f LUFS)",
                            before,
                            after,
                            args.lufs,
                        )

                    if args.peak is not None:
                        current_peak = float(np.max(np.abs(data)))
                        if current_peak > 0:
                            target_peak = 10.0 ** (args.peak / 20.0)
                            data = data * (target_peak / current_peak)

                    if args.dc_block:
                        data = dc_blocker(data)
                    if args.fade_in is not None:
                        data = fade_in(data, args.fade_in, sample_rate)
                    if args.fade_out is not None:
                        data = fade_out(data, args.fade_out, sample_rate)
                    if args.reverse:
                        data = reverse_audio(data)
                    if args.invert:
                        data = invert_phase(data)
                    if args.lowpass is not None:
                        data = lowpass(data, args.lowpass, sample_rate)
                    if args.highpass is not None:
                        data = highpass(data, args.highpass, sample_rate)
                    if args.bandpass is not None:
                        parts = [float(x) for x in args.bandpass.split(",")]
                        if len(parts) == 2:
                            data = bandpass(data, parts[0], parts[1], sample_rate)
                    if args.envelope is not None:
                        parts = [float(x) for x in args.envelope.split(",")]
                        if len(parts) == 4:
                            data = apply_envelope(
                                data, parts[0], parts[1], parts[2], parts[3], sample_rate
                            )

                    if args.width is not None:
                        data = stereo_width(data, args.width)
                    if args.pan is not None:
                        data = pan(data, args.pan)
                    if args.tremolo is not None:
                        parts = [float(x) for x in args.tremolo.split(",")]
                        if len(parts) == 2:
                            data = modulate_amplitude(data, parts[0], parts[1], sample_rate)
                    if args.bitcrush is not None:
                        data = bitcrush(data, args.bitcrush)
                    if args.dither is not None:
                        data = dither(data, args.dither)
                    if args.compressor is not None:
                        parts = [float(x) for x in args.compressor.split(",")]
                        if len(parts) == 2:
                            data = compressor(data, parts[0], parts[1], sample_rate=sample_rate)
                    if args.rms is not None:
                        data = normalize_rms(data, args.rms)

                    if args.stats:
                        stats = compute_stats(data, sample_rate)
                        from rich.table import Table

                        table = Table(title=f"{noise_type.capitalize()} Noise - Audio Statistics")
                        table.add_column("Property", style="cyan")
                        table.add_column("Value", style="yellow")
                        for prop, val in stats.to_table():
                            table.add_row(prop, val)
                        console.print(table)

                    if args.spectrum:
                        nyquist = sample_rate / 2
                        console.print(
                            f"\n[bold cyan]Spectrum:[/] [yellow]{noise_type} noise[/] (0 \u2014 {nyquist:.0f} Hz)"
                        )
                        spec = ascii_spectrum(data, sample_rate, width=50, height=8)
                        console.print(spec)

                    if args.json is not None:
                        json_path = Path(args.json)
                        save_json_stats(data, sample_rate, json_path)
                        print_success(f"Statistics saved to {json_path}")

                    for fmt in format_configs:
                        if args.pattern:
                            ch_label = "mono" if n_channels == 1 else "stereo"
                            filename = args.pattern.format(
                                type=noise_type,
                                channels=ch_label,
                                format=fmt,
                                sr=sample_rate,
                                bits=args.bit_depth,
                                seed=seed_val if seed_val is not None else 0,
                            )
                        else:
                            channel_label = "mono" if n_channels == 1 else ""
                            suffix = f"_{channel_label}" if channel_label else ""
                            filename = f"{noise_type}_noise{suffix}.{fmt}"
                        filepath = output_dir / filename
                        saver = FORMATS[fmt]
                        saver(filepath, data, sample_rate=sample_rate, bit_depth=args.bit_depth)
                        files_created.append(filepath)
                        progress.advance(task)

            if args.play:
                try:
                    import sounddevice as sd

                    sd.play(data, samplerate=sample_rate)
                    sd.wait()
                except ImportError:
                    print_warning("Install sounddevice to play audio: pip install sounddevice")
                except Exception as e:
                    print_warning(f"Playback failed: {e}")

            if args.preview and n_channels in (1, 2):
                ch = 0
                wave = ascii_waveform(data, width=50, height=7, channel=ch)
                console.print(
                    f"\n[bold cyan]Waveform:[/] [yellow]{noise_type} noise[/] ({n_channels} ch)"
                )
                console.print(wave)

    print_results_table(files_created, output_dir)
    print_success(f"Done \u2014 {len(files_created)} file(s) saved to {output_dir}")


def main(argv: list[str] | None = None) -> None:
    try:
        _main(argv)
    except KeyboardInterrupt:
        print_warning("Interrupted by user")
        sys.exit(130)
    except Exception as exc:
        print_error(str(exc))
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
