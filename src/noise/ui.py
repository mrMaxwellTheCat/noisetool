from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

console = Console(stderr=True)
err_console = Console(stderr=True)


def print_banner() -> None:
    """Print a branded banner."""
    banner = Text()
    banner.append("noisetool", style="bold cyan")
    banner.append("  —  ", style="dim white")
    banner.append("High-quality noise generator", style="green")
    console.print(Panel(banner, border_style="blue"))


def print_noise_table(noise_types: dict[str, str]) -> None:
    """Print available noise types as a rich table."""
    table = Table(title="Available Noise Types", border_style="cyan")
    table.add_column("Type", style="bold yellow", width=10)
    table.add_column("Description", style="white")
    table.add_column("Spectrum", style="dim")
    for name, desc in noise_types.items():
        table.add_row(name, desc, "")
    console.print(table)


def print_results_table(files: list[Path], output_dir: Path) -> None:  # noqa: ARG001
    """Print a results table of generated files."""
    table = Table(title="Generated Files", border_style="green")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="yellow", justify="right")
    table.add_column("Type", style="dim")
    for f in files:
        size = f.stat().st_size if f.exists() else 0
        size_str = f"{size:,} bytes" if size > 0 else "\u2014"
        fmt = f.suffix.lstrip(".").upper()
        table.add_row(f.name, size_str, fmt)
    console.print(table)


def make_progress() -> Progress:
    """Create a progress bar for generation tasks."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=err_console,
    )


def print_loudness(name: str, before: float, after: float, target: float) -> None:
    """Print loudness normalization info."""
    before_str = f"{before:.2f} LUFS"
    after_str = f"{after:.2f} LUFS"
    target_str = f"{target:.1f} LUFS"
    text = Text()
    text.append(f"  {name}: ", style="bold")
    text.append(before_str, style="yellow")
    text.append(" \u2192 ", style="dim")
    text.append(after_str, style="green")
    text.append(f"  (target: {target_str})", style="dim")
    console.print(text)


def print_info(msg: str) -> None:
    """Print an info message."""
    console.print(f"[bold blue]\u2022[/] {msg}")


def print_success(msg: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]\u2713[/] {msg}")


def print_warning(msg: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]![/] {msg}")


def print_error(msg: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]\u2717[/] {msg}")
