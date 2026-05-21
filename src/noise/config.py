from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class NoiseConfig:
    noise_type: str = "all"
    duration: float = 30.0
    sample_rate: int = 44100
    channels: list[int] = field(default_factory=lambda: [1, 2])
    formats: list[str] = field(default_factory=lambda: ["wav", "flac"])
    bit_depth: int = 24
    lufs: float | None = None
    peak: float | None = None
    rms: float | None = None
    seed: int | None = None
    seeds: str | None = None
    output_dir: str = "audio"
    mono: bool = False
    stereo: bool = False
    mix: str | None = None
    pattern: str | None = None
    loop: bool = False
    parallel: bool = False
    workers: int | None = None
    continuous: bool = False
    dc_block: bool = False
    fade_in: float | None = None
    fade_out: float | None = None
    reverse: bool = False
    invert: bool = False
    lowpass: float | None = None
    highpass: float | None = None
    bandpass: str | None = None
    envelope: str | None = None
    width: float | None = None
    pan: float | None = None
    tremolo: str | None = None
    bitcrush: int | None = None
    dither: int | None = None
    compressor: str | None = None
    preview: bool = False
    spectrum: bool = False
    eq_viz: bool = False
    stats: bool = False
    play: bool = False
    dry_run: bool = False
    silent: bool = False
    progress: str = "rich"


def load_config(path: Path) -> NoiseConfig:
    """Load a generation config from a JSON file (YAML support optional)."""
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML config files. Install with: pip install pyyaml"
            ) from None
        raw: dict[str, Any] = yaml.safe_load(text)
    else:
        raw = json.loads(text)

    return NoiseConfig(
        noise_type=raw.get("type", "all"),
        duration=raw.get("duration", 30.0),
        sample_rate=raw.get("sample_rate", 44100),
        channels=raw.get("channels", [1, 2]),
        formats=raw.get("formats", ["wav", "flac"]),
        bit_depth=raw.get("bit_depth", 24),
        lufs=raw.get("lufs"),
        peak=raw.get("peak"),
        rms=raw.get("rms"),
        seed=raw.get("seed"),
        seeds=raw.get("seeds"),
        output_dir=raw.get("output_dir", "audio"),
        mono=raw.get("mono", False),
        stereo=raw.get("stereo", False),
        mix=raw.get("mix"),
        pattern=raw.get("pattern"),
        loop=raw.get("loop", False),
        parallel=raw.get("parallel", False),
        workers=raw.get("workers"),
        continuous=raw.get("continuous", False),
        dc_block=raw.get("dc_block", False),
        fade_in=raw.get("fade_in"),
        fade_out=raw.get("fade_out"),
        reverse=raw.get("reverse", False),
        invert=raw.get("invert", False),
        lowpass=raw.get("lowpass"),
        highpass=raw.get("highpass"),
        bandpass=raw.get("bandpass"),
        envelope=raw.get("envelope"),
        width=raw.get("width"),
        pan=raw.get("pan"),
        tremolo=raw.get("tremolo"),
        bitcrush=raw.get("bitcrush"),
        dither=raw.get("dither"),
        compressor=raw.get("compressor"),
        preview=raw.get("preview", False),
        spectrum=raw.get("spectrum", False),
        eq_viz=raw.get("eq_viz", False),
        stats=raw.get("stats", False),
        play=raw.get("play", False),
        dry_run=raw.get("dry_run", False),
        silent=raw.get("silent", False),
        progress=raw.get("progress", "rich"),
    )


def config_to_args(config: NoiseConfig) -> dict[str, Any]:
    """Convert NoiseConfig to an args dict suitable for setattr on Namespace."""
    return {
        "type": config.noise_type,
        "duration": config.duration,
        "sample_rate": config.sample_rate,
        "bit_depth": config.bit_depth,
        "lufs": config.lufs,
        "peak": config.peak,
        "rms": config.rms,
        "seed": config.seed,
        "seeds": config.seeds,
        "output_dir": Path(config.output_dir),
        "mono": config.mono,
        "stereo": config.stereo,
        "mix": config.mix,
        "pattern": config.pattern,
        "loop": config.loop,
        "parallel": config.parallel,
        "workers": config.workers,
        "continuous": config.continuous,
        "dc_block": config.dc_block,
        "fade_in": config.fade_in,
        "fade_out": config.fade_out,
        "reverse": config.reverse,
        "invert": config.invert,
        "lowpass": config.lowpass,
        "highpass": config.highpass,
        "bandpass": config.bandpass,
        "envelope": config.envelope,
        "width": config.width,
        "pan": config.pan,
        "tremolo": config.tremolo,
        "bitcrush": config.bitcrush,
        "dither": config.dither,
        "compressor": config.compressor,
        "preview": config.preview,
        "spectrum": config.spectrum,
        "eq_viz": config.eq_viz,
        "stats": config.stats,
        "play": config.play,
        "dry_run": config.dry_run,
        "silent": config.silent,
        "progress": config.progress,
        "format": "all" if len(config.formats) > 1 else config.formats[0],
        "no_banner": True,
    }


def generate_example_config(path: Path) -> None:
    """Write an example config file."""
    config = {
        "type": "all",
        "duration": 30.0,
        "sample_rate": 44100,
        "channels": [1, 2],
        "formats": ["wav", "flac"],
        "bit_depth": 24,
        "lufs": -14.0,
        "peak": -1.0,
        "seed": 42,
        "output_dir": "audio",
        "mix": "pink=0.7,white=0.3",
        "loop": False,
        "parallel": False,
        "dc_block": False,
        "fade_in": 0.1,
        "fade_out": 0.3,
        "reverse": False,
        "invert": False,
        "lowpass": None,
        "highpass": None,
        "bandpass": None,
        "envelope": None,
        "width": None,
        "pan": None,
        "tremolo": None,
        "bitcrush": None,
        "dither": None,
        "compressor": None,
        "preview": False,
        "spectrum": False,
        "stats": False,
        "silent": False,
        "progress": "rich",
    }
    if path.suffix in (".yaml", ".yml"):
        try:
            import yaml

            text = yaml.dump(config, default_flow_style=False)
        except ImportError:
            text = str(config)
    else:
        text = json.dumps(config, indent=2)
    path.write_text(text, encoding="utf-8")
