from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np

from noise import __version__
from noise.analysis import ascii_spectrum, compute_stats, save_json_stats
from noise.completion import SHELL_COMPLETION_SCRIPT, add_completion_args
from noise.config import generate_example_config, load_config
from noise.effects import dc_blocker, fade_in, fade_out, invert_phase
from noise.effects import reverse as reverse_audio
from noise.generator import (
    generate_blue_noise,
    generate_brown_noise,
    generate_grey_noise,
    generate_pink_noise,
    generate_violet_noise,
    generate_white_noise,
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
        choices=["all", "wav", "flac"],
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
        "--stats",
        action="store_true",
        default=False,
        help="Show detailed audio statistics after generation",
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
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be generated without creating files",
    )

    return parser.parse_args(argv)


def _main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

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

    sample_rate = args.sample_rate
    n_samples = int(sample_rate * args.duration)
    rng = np.random.default_rng(args.seed) if args.seed is not None else None

    noise_types = list(NOISE_GENERATORS.keys()) if args.type == "all" else [args.type]
    channel_configs = [1, 2] if not args.mono and not args.stereo else ([1] if args.mono else [2])
    format_configs = ["wav", "flac"] if args.format == "all" else [args.format]

    if args.dry_run:
        print_info("Dry run \u2014 no files will be created:")
        for noise_type in noise_types:
            for n_channels in channel_configs:
                label = "mono" if n_channels == 1 else "stereo"
                for fmt in format_configs:
                    suffix = "_mono" if n_channels == 1 else ""
                    print_info(f"  {noise_type}_noise{suffix}.{fmt} ({label}, {n_samples} samples)")
        return

    if args.measure:
        print_info("Measuring loudness (no files will be saved):")
        for noise_type in noise_types:
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

    progress = make_progress()
    total_tasks = len(noise_types) * len(channel_configs) * len(format_configs)
    task = progress.add_task("Generating...", total=total_tasks)

    with progress:
        for noise_type in noise_types:
            for n_channels in channel_configs:
                data = NOISE_GENERATORS[noise_type](n_samples, n_channels=n_channels, rng=rng)

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

                channel_label = "mono" if n_channels == 1 else ""
                suffix = f"_{channel_label}" if channel_label else ""

                for fmt in format_configs:
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
