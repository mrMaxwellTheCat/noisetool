from __future__ import annotations

from typing import Any

from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from noise.ui import console, print_banner

NOISE_PRESETS: dict[str, tuple[str, str]] = {
    "1": ("white", "Flat"),
    "2": ("pink", "1/f"),
    "3": ("brown", "1/f\u00b2"),
    "4": ("blue", "Rising"),
    "5": ("violet", "Sharp"),
    "6": ("grey", "Psychoacoustic"),
}

FORMAT_PRESETS: dict[str, dict[str, Any]] = {
    "1": {
        "label": "WAV",
        "formats": ["wav"],
        "default_quality": 24,
        "quality_label": "Bit depth",
        "quality_range": "16/24/32",
    },
    "2": {
        "label": "FLAC",
        "formats": ["flac"],
        "default_quality": 5,
        "quality_label": "Compression",
        "quality_range": "0-8",
    },
    "3": {
        "label": "OGG",
        "formats": ["ogg"],
        "default_quality": 5,
        "quality_label": "Quality",
        "quality_range": "-1 to 10",
    },
    "4": {
        "label": "MP3",
        "formats": ["wav"],
        "default_quality": 256,
        "quality_label": "Bitrate",
        "quality_range": "kbps",
    },
    "5": {
        "label": "WAV+FLAC",
        "formats": ["wav", "flac"],
        "default_quality": 24,
        "quality_label": "Bit depth",
        "quality_range": "16/24/32",
    },
}

CHANNEL_PRESETS: dict[str, str] = {"1": "Stereo", "2": "Mono", "3": "Both"}


def _noise_table() -> Table:
    t = Table(box=None, show_header=False, padding=(0, 1))
    t.add_column("#", style="dim cyan", width=2)
    t.add_column("Type", style="white", width=8)
    t.add_column("Desc", style="dim", width=16)
    for k, (name, desc) in NOISE_PRESETS.items():
        t.add_row(k, name, desc)
    return t


def _quick_wizard() -> dict[str, Any]:
    from noise.cli import PRESETS

    console.print("[bold yellow]Quick Setup[/]")
    names = list(PRESETS.keys())
    for i, n in enumerate(names, 1):
        console.print(f"  [dim]{i}.[/] {n}")
    choice = Prompt.ask(
        "[yellow]Preset[/]",
        choices=[str(i) for i in range(1, len(names) + 1)],
        default="1",
    )
    preset_name = names[int(choice) - 1]
    preset = dict(PRESETS[preset_name])
    output_dir = Prompt.ask("[yellow]Output folder[/]", default="audio")
    noise_type = preset.get("type", "all")
    config: dict[str, Any] = {
        "noise_types": [v[0] for v in NOISE_PRESETS.values()]
        if noise_type == "all"
        else [noise_type],
        "n_channels": [1] if preset.get("mono") else ([2] if preset.get("stereo") else [1, 2]),
        "duration": preset.get("duration", 30),
        "sample_rate": preset.get("sample_rate", 44100),
        "formats": ["wav", "flac"]
        if preset.get("format") == "all"
        else [preset.get("format", "wav")],
        "quality_value": preset.get("bit_depth", 24),
        "lufs": preset.get("lufs"),
        "output_dir": output_dir,
    }
    console.print(f"[green]\u2713[/] Preset [bold]{preset_name}[/]")
    return config


def run_wizard() -> dict[str, Any]:
    print_banner()

    console.print()
    quick = Prompt.ask(
        "[yellow]Setup mode[/]",
        choices=["quick", "custom"],
        default="custom",
    )
    if quick == "quick":
        return _quick_wizard()

    config: dict[str, Any] = {}
    sep = "\u2500" * 38

    console.print()
    console.print("[bold cyan]noisetool[/] [dim]interactive[/]")

    # --- Noise Types ---
    console.print(f"[dim]{sep}[/]")
    console.print("[bold yellow]Noise Types[/]")
    console.print(_noise_table())
    raw = Prompt.ask(
        "[yellow]Select[/] (numbers/comma, or [i]all[/])",
        default="all",
    )
    if raw.strip().lower() == "all":
        config["noise_types"] = [v[0] for v in NOISE_PRESETS.values()]
    else:
        selected = [
            NOISE_PRESETS[s.strip()][0] for s in raw.split(",") if s.strip() in NOISE_PRESETS
        ]
        config["noise_types"] = selected if selected else [v[0] for v in NOISE_PRESETS.values()]

    # --- Channels ---
    console.print(f"[dim]{sep}[/]")
    console.print("[bold yellow]Channels[/]")
    for k, v in CHANNEL_PRESETS.items():
        console.print(f"  [dim]{k}.[/] {v}")
    ch = Prompt.ask("[yellow]Choose[/]", choices=["1", "2", "3"], default="3")
    config["n_channels"] = {"1": [2], "2": [1], "3": [1, 2]}[ch]

    # --- Duration ---
    console.print(f"[dim]{sep}[/]")
    console.print("[dim]Set [i]0[/i] seconds for continuous generation[/]")
    raw_dur = Prompt.ask(
        "[yellow]Length[/] (seconds, or [i]0[/] for continuous)",
        default="30",
    )
    dur = float(raw_dur)
    config["duration"] = dur if dur > 0 else 30.0
    config["continuous"] = dur == 0

    # --- Format ---
    console.print(f"[dim]{sep}[/]")
    console.print("[bold yellow]Format[/]")
    for k, fp in FORMAT_PRESETS.items():
        console.print(f"  [dim]{k}.[/] {fp['label']:<8} [dim]({fp['quality_range']})[/]")
    fmt = Prompt.ask("[yellow]Choose[/]", choices=list(FORMAT_PRESETS.keys()), default="5")
    fp = FORMAT_PRESETS[fmt]
    config["formats"] = fp["formats"]
    config["quality_value"] = IntPrompt.ask(
        f"[yellow]{fp['quality_label']}[/] ({fp['quality_range']})",
        default=fp["default_quality"],
    )

    # --- Sample Rate ---
    config["sample_rate"] = int(
        Prompt.ask(
            "[yellow]Sample rate[/]",
            choices=["44100", "48000", "96000", "192000"],
            default="44100",
        )
    )

    # --- Loudness ---
    console.print(f"[dim]{sep}[/]")
    console.print("[bold yellow]Loudness[/]")
    loud = Prompt.ask(
        "[yellow]Target[/]",
        choices=["none", "streaming -14", "broadcast -23", "podcast -16", "custom"],
        default="streaming -14",
    )
    if loud == "none":
        config["lufs"] = None
    elif loud == "custom":
        config["lufs"] = float(Prompt.ask("  LUFS target", default="-14"))
    else:
        config["lufs"] = float(loud.split()[-1])

    # --- Output ---
    console.print(f"[dim]{sep}[/]")
    config["output_dir"] = Prompt.ask("[yellow]Output folder[/]", default="audio")

    # --- Summary ---
    console.print()
    console.print(f"[dim]{sep}[/]")
    n_types = len(config["noise_types"])
    ch_map = {1: "mono only", 2: "stereo only", 3: "stereo+mono"}
    ch_label = ch_map.get(len(config["n_channels"]), "stereo+mono")
    fmt_label: str = fp["label"]
    mode = "continuous" if config.get("continuous") else f"{config['duration']}s"
    lufs_label = f"{config['lufs']} LUFS" if config.get("lufs") else "none"
    console.print(
        f"[green]\u2713[/] [bold]{n_types} type(s)[/] | {ch_label} | {mode} | "
        f"{fmt_label} | {config['sample_rate']}Hz | LUFS: {lufs_label}"
    )
    console.print()

    return config
