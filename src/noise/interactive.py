from __future__ import annotations

from typing import Any

from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table

from noise.ui import console, print_banner


def run_wizard() -> dict[str, Any]:
    """Run the interactive configuration wizard.

    Returns a dict of settings suitable for passing to the generation functions.
    """
    print_banner()
    console.print()
    console.print("[bold cyan]Interactive Mode[/]  —  Press [dim]Enter[/] to accept defaults")
    console.print()

    config: dict[str, Any] = {}

    # Noise types
    console.print("[bold yellow]Noise Types[/]")
    types_table = Table(box=None, show_header=False)
    types_table.add_column("Key", style="cyan", width=2)
    types_table.add_column("Type", style="white", width=10)
    types_table.add_column("Description", style="dim")
    for i, (name, desc) in enumerate(
        [
            ("white", "Flat spectrum"),
            ("pink", "1/f spectrum"),
            ("brown", "1/f\u00b2 spectrum"),
            ("blue", "Rising spectrum"),
            ("violet", "Steep rising"),
            ("grey", "Equal loudness"),
        ],
        1,
    ):
        types_table.add_row(str(i), name, desc)
    console.print(types_table)
    selected = Prompt.ask(
        "[yellow]Types[/] (comma-separated, or [bold]all[/])",
        default="all",
    )
    if selected.lower() == "all":
        config["noise_types"] = ["white", "pink", "brown", "blue", "violet", "grey"]
    else:
        config["noise_types"] = [t.strip() for t in selected.split(",")]

    # Channels
    console.print()
    channel_choice = Prompt.ask(
        "[yellow]Channels[/]",
        choices=["stereo+mono", "stereo", "mono"],
        default="stereo+mono",
    )
    if channel_choice == "stereo":
        config["n_channels"] = [2]
    elif channel_choice == "mono":
        config["n_channels"] = [1]
    else:
        config["n_channels"] = [1, 2]

    # Format
    fmt_choice = Prompt.ask(
        "[yellow]Format[/]",
        choices=["wav+flac", "wav", "flac", "ogg", "aiff", "raw"],
        default="wav+flac",
    )
    if fmt_choice == "wav+flac":
        config["formats"] = ["wav", "flac"]
    else:
        config["formats"] = [fmt_choice]

    # Duration
    config["duration"] = FloatPrompt.ask(
        "[yellow]Duration[/] (seconds)",
        default=30.0,
    )

    # Sample rate
    config["sample_rate"] = IntPrompt.ask(
        "[yellow]Sample rate[/] (Hz)",
        default=44100,
    )

    # Bit depth
    config["bit_depth"] = IntPrompt.ask(
        "[yellow]Bit depth[/]",
        choices=["16", "24", "32"],
        default=24,
    )

    # LUFS normalization
    console.print()
    if Confirm.ask("[yellow]Apply LUFS normalization?[/]", default=False):
        config["lufs"] = FloatPrompt.ask(
            "  Target LUFS",
            default=-14.0,
        )
    else:
        config["lufs"] = None

    # Peak normalize
    if Confirm.ask("[yellow]Apply peak normalization?[/]", default=False):
        config["peak"] = FloatPrompt.ask(
            "  Target peak level (dBFS)",
            default=-1.0,
        )
    else:
        config["peak"] = None

    # Seed
    if Confirm.ask("[yellow]Use fixed seed for reproducibility?[/]", default=False):
        config["seed"] = IntPrompt.ask("  Seed value", default=42)
    else:
        config["seed"] = None

    # Output directory
    config["output_dir"] = Prompt.ask(
        "[yellow]Output directory[/]",
        default="audio",
    )

    # Effects section
    console.print()
    console.print("[bold yellow]Effects & Processing[/]")

    if Confirm.ask("[yellow]Apply DC block filter?[/]", default=False):
        config["dc_block"] = True
    else:
        config["dc_block"] = False

    if Confirm.ask("[yellow]Apply fade in?[/]", default=False):
        config["fade_in"] = FloatPrompt.ask("  Fade-in duration (seconds)", default=0.1)
    else:
        config["fade_in"] = None

    if Confirm.ask("[yellow]Apply fade out?[/]", default=False):
        config["fade_out"] = FloatPrompt.ask("  Fade-out duration (seconds)", default=0.3)
    else:
        config["fade_out"] = None

    if Confirm.ask("[yellow]Apply low-pass filter?[/]", default=False):
        config["lowpass"] = FloatPrompt.ask("  Cutoff frequency (Hz)", default=5000)
    else:
        config["lowpass"] = None

    if Confirm.ask("[yellow]Apply high-pass filter?[/]", default=False):
        config["highpass"] = FloatPrompt.ask("  Cutoff frequency (Hz)", default=80)
    else:
        config["highpass"] = None

    if Confirm.ask("[yellow]Apply stereo width adjustment?[/]", default=False):
        config["width"] = FloatPrompt.ask("  Width (0=mono, 1=original, >1=wider)", default=1.0)
    else:
        config["width"] = None

    if Confirm.ask("[yellow]Apply amplitude modulation (tremolo)?[/]", default=False):
        rate = FloatPrompt.ask("  Rate (Hz)", default=5.0)
        depth = FloatPrompt.ask("  Depth (0.0-1.0)", default=0.5)
        config["tremolo"] = f"{rate},{depth}"
    else:
        config["tremolo"] = None

    console.print()
    console.print("[bold green]\u2713[/] Configuration complete. Generating...")
    console.print()

    return config
