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
    seed: int | None = None
    output_dir: str = "audio"


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
        seed=raw.get("seed"),
        output_dir=raw.get("output_dir", "audio"),
    )


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
