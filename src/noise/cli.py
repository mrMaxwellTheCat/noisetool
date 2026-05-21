from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np

from noise import __version__
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
        description="Generate high-quality noise audio files (white, pink, brown).",
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
        help="Generate mono audio only (default: stereo)",
    )

    parser.add_argument(
        "--stereo",
        action="store_true",
        default=False,
        help="Generate stereo audio only (default: both unless --mono specified)",
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
        "--list",
        action="store_true",
        default=False,
        help="List available noise types with descriptions and exit",
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

    return parser.parse_args(argv)


def _setup_logging(verbose: bool, log_file: Path | None = None) -> None:
    fmt = "%(asctime)s %(levelname)s: %(message)s" if verbose else "%(levelname)s: %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(str(log_file)))
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format=fmt,
        handlers=handlers,
        datefmt="%H:%M:%S",
    )


def _make_output_dir(output_dir: Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir.resolve()


def _generate(
    noise_type: str,
    n_samples: int,
    n_channels: int,
    rng: np.random.Generator | None,
) -> np.ndarray:
    generator = NOISE_GENERATORS[noise_type]
    return generator(n_samples, n_channels=n_channels, rng=rng)


def _main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    _setup_logging(args.verbose, args.log_file)

    if args.list:
        logger.info("Available noise types:")
        for name in NOISE_GENERATORS:
            logger.info("  %-8s %s", name, NOISE_DESCRIPTIONS[name])
        return

    sample_rate = args.sample_rate
    n_samples = int(sample_rate * args.duration)

    rng = np.random.default_rng(args.seed) if args.seed is not None else None

    noise_types = list(NOISE_GENERATORS.keys()) if args.type == "all" else [args.type]

    if not args.mono and not args.stereo:
        channel_configs = [1, 2]
    elif args.mono:
        channel_configs = [1]
    else:
        channel_configs = [2]

    format_configs = ["wav", "flac"] if args.format == "all" else [args.format]

    if args.measure:
        logger.info("Measuring loudness (no files will be saved):")
        for noise_type in noise_types:
            logger.info("  Generating %s noise...", noise_type)
            data = _generate(noise_type, n_samples, 2, rng)
            loudness = measure_loudness(data, sample_rate)
            logger.info(
                "    %s noise (%d ch, %d Hz): %.2f LUFS",
                noise_type.capitalize(),
                2,
                sample_rate,
                loudness,
            )
        return

    output_dir = _make_output_dir(args.output_dir)
    files_created: list[Path] = []

    for noise_type in noise_types:
        logger.info("Generating %s noise...", noise_type)
        for n_channels in channel_configs:
            data = _generate(noise_type, n_samples, n_channels, rng)

            if args.peak is not None:
                current_peak = float(np.max(np.abs(data)))
                if current_peak > 0:
                    target_peak = 10.0 ** (args.peak / 20.0)
                    data = data * (target_peak / current_peak)

            if args.lufs is not None:
                before = measure_loudness(data, sample_rate)
                data = lufs_normalize(data, target_lufs=args.lufs, sample_rate=sample_rate)
                after = measure_loudness(data, sample_rate)
                logger.debug(
                    "  Loudness: %.2f LUFS -> %.2f LUFS (target: %.1f LUFS)",
                    before,
                    after,
                    args.lufs,
                )

            channel_label = "mono" if n_channels == 1 else ""
            suffix = f"_{channel_label}" if channel_label else ""

            for fmt in format_configs:
                filename = f"{noise_type}_noise{suffix}.{fmt}"
                filepath = output_dir / filename

                saver = FORMATS[fmt]
                saver(filepath, data, sample_rate=sample_rate, bit_depth=args.bit_depth)
                files_created.append(filepath)

                logger.info("  Created: %s", filepath)

    logger.info("Done. %d file(s) saved to: %s", len(files_created), output_dir)
    logger.info("Use 'noisetool --measure' to check loudness without saving.")


def main(argv: list[str] | None = None) -> None:
    try:
        _main(argv)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(130)
    except Exception as exc:
        logger.exception("Fatal error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
