# noisetool

**High-quality noise generator** — Generate white, pink, brown, blue, violet, and grey noise audio files with LUFS loudness normalization, effects, and analysis.

[![CI](https://github.com/mrMaxwellTheCat/noise/actions/workflows/ci.yml/badge.svg)](https://github.com/mrMaxwellTheCat/noise/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/noisetool)](https://pypi.org/project/noisetool/)
[![Python](https://img.shields.io/pypi/pyversions/noisetool)](https://pypi.org/project/noisetool/)
[![License](https://img.shields.io/pypi/l/noisetool)](LICENSE)

## Features

- **6 noise types**: white, pink (1/f), brown (1/f²), blue (1/f^0.5), violet (1/f), grey (psychoacoustic)
- **Stereo & mono** output for every noise type
- **WAV & FLAC** formats with selectable bit depth (16, 24, 32-bit)
- **ITU-R BS.1770-4 LUFS** loudness measurement and normalization
- **Peak normalization** to a target dB level
- **Audio effects**: DC blocking filter, linear fade-in/out, time reverse, phase invert
- **Analysis tools**: detailed stats, ASCII spectrum, ASCII waveform preview, JSON export
- **Audio playback** via system output (requires `sounddevice`)
- **Dry-run mode** to preview file list without writing
- **Config files** (JSON and YAML) for repeatable generation
- **Shell completion** (bash, zsh, fish)
- **Reproducible output** with configurable random seed
- **Parallel processing** for multi-type generation
- **Docker** support
- **Rich terminal UI** with banners, progress bars, and color tables

## Installation

### pip (recommended)

```bash
pip install noisetool
```

### pip with dev dependencies

```bash
pip install "noisetool[dev]"
```

### From source

```bash
git clone https://github.com/mrMaxwellTheCat/noise.git
cd noise
pip install -e ".[dev]"
```

### Docker

```bash
docker build -t noisetool .
```

See the [Docker section](#docker) below for usage.

## Quick Start

```bash
# Generate all noise types (defaults: 30s, stereo+mono, WAV+FLAC)
noisetool

# Generate white noise only, mono, WAV, normalized to -14 LUFS
noisetool --type white --mono -f wav --lufs -14

# Generate pink noise at 96 kHz, 60 seconds, with seed for reproducibility
noisetool --type pink --duration 60 --sample-rate 96000 --seed 42

# Measure loudness without saving files
noisetool --measure

# Generate brown noise normalized to broadcast standard (-23 LUFS)
noisetool --type brown --lufs -23

# Apply fade and reverse effect
noisetool --type pink --fade-in 2 --fade-out 2 --reverse

# Show stats and spectrum visualization
noisetool --type white --stats --spectrum --duration 5

# List available noise types
noisetool --list

# Dry run (preview what would be generated)
noisetool --dry-run

# Verbose output for debugging
noisetool -v
```

## Usage

### Basic Options

| Argument | Description | Default |
|----------|-------------|---------|
| `-t, --type` | Noise type: `all`, `white`, `pink`, `brown`, `blue`, `violet`, `grey` | `all` |
| `-d, --duration` | Duration in seconds | `30` |
| `-r, --sample-rate` | Sample rate in Hz | `44100` |
| `--mono` | Generate mono audio only | stereo + mono |
| `--stereo` | Generate stereo audio only | stereo + mono |
| `-o, --output-dir` | Output directory | `audio/` |
| `-f, --format` | Output format: `all`, `wav`, `flac` | `all` |
| `--bit-depth` | Bit depth: `16`, `24`, `32` | `24` |
| `--lufs` | Target LUFS loudness for normalization | off |
| `--peak` | Peak normalize to target dB level (e.g. `-1.0`) | off |
| `--seed` | Random seed for reproducible generation | random |
| `-v, --verbose` | Enable verbose/debug logging | off |
| `--list` | List available noise types with descriptions and exit | off |
| `--version` | Show version and exit | off |

### Noise Types

| Type | Description | Spectrum |
|------|-------------|----------|
| `white` | Flat power spectrum across all frequencies. Generated via uniform random samples. | Flat |
| `pink` | Power decreases 3 dB/octave (1/f spectrum). Generated via FFT frequency-domain filtering with a `1/√f` filter. | −3 dB/octave |
| `brown` | Power decreases 6 dB/octave (1/f² spectrum). Generated via cumulative sum (integration) of white noise. | −6 dB/octave |
| `blue` | Power increases 3 dB/octave (rising spectrum). Generated via FFT filtering with a `√f` filter. | +3 dB/octave |
| `violet` | Power increases 6 dB/octave (rising spectrum). Generated via FFT filtering with an `f` filter. | +6 dB/octave |
| `grey` | Psychoacoustic equal-loudness noise. Generated via FFT filtering with a `1/(1+(f/2000)²)` filter. | Perceptually flat |

### Effects

Effects are applied in the following order after generation: LUFS normalization, peak normalization, DC blocker, fade-in, fade-out, reverse, invert.

| Option | Description |
|--------|-------------|
| `--dc-block` | Remove DC offset using a high-pass IIR filter (α = 0.995) |
| `--fade-in SECONDS` | Apply linear fade-in at the start |
| `--fade-out SECONDS` | Apply linear fade-out at the end |
| `--reverse` | Reverse audio in time |
| `--invert` | Invert audio phase (multiply samples by -1) |
| `--peak LEVEL` | Peak-normalize to a target dB level (e.g., `-1.0`) |

### Analysis & Output

| Option | Description |
|--------|-------------|
| `--stats` | Show detailed audio statistics (duration, samples, channels, sample rate, bit depth, peak, RMS, crest factor, DC offset) |
| `--spectrum` | Show ASCII frequency spectrum visualization (FFT-based, with frequency labels) |
| `--preview` | Show ASCII waveform preview of generated audio |
| `--play` | Play generated audio through system output (requires `sounddevice`) |
| `--json FILE` | Save audio statistics as a JSON file |
| `--measure` | Measure and display loudness of generated noise types in LUFS without saving files |
| `--dry-run` | Show what files would be generated without creating any |

### Configuration

| Option | Description |
|--------|-------------|
| `--config FILE` | Load generation config from JSON or YAML file |
| `--example-config FILE` | Write an example config file (JSON or YAML, inferred from extension) and exit |
| `--log-file FILE` | Write log output to a file in addition to stderr |
| `--no-banner` | Suppress the startup banner |

### Example Config File

```json
{
    "type": "all",
    "duration": 30.0,
    "sample_rate": 44100,
    "channels": [1, 2],
    "formats": ["wav", "flac"],
    "bit_depth": 24,
    "lufs": -14.0,
    "peak": -1.0,
    "seed": 42,
    "output_dir": "audio"
}
```

YAML configs are also supported (requires `pyyaml`):

```bash
noisetool --example-config config.yaml
noisetool --config config.yaml
```

## LUFS Loudness Normalization

This tool implements **ITU-R BS.1770-4** for integrated loudness measurement using K-weighting (pre-filter + RLB weighting). Use `--lufs TARGET` to normalize output to a specific loudness level.

**Common targets:**

| Target | Standard | Use Case |
|--------|----------|----------|
| **−14 LUFS** | Streaming | YouTube, Spotify, Apple Music, Tidal |
| **−16 LUFS** | Podcasts | Podcast loudness standard |
| **−23 LUFS** | Broadcast | EBU R128, ATSC A/85 (TV, radio) |
| **−18 LUFS** | Film | Cinema trailer and film mixing |

If normalization causes clipping (samples exceeding ±1.0), the signal is automatically limited to prevent distortion.

## Output Files

Generated audio files follow this naming convention:

```
audio/
├── white_noise.wav / white_noise.flac          (stereo)
├── white_noise_mono.wav / white_noise_mono.flac  (mono)
├── pink_noise.wav / pink_noise.flac
├── pink_noise_mono.wav / pink_noise_mono.flac
├── brown_noise.wav / brown_noise.flac
├── brown_noise_mono.wav / brown_noise_mono.flac
├── blue_noise.wav / blue_noise.flac
├── blue_noise_mono.wav / blue_noise_mono.flac
├── violet_noise.wav / violet_noise.flac
├── violet_noise_mono.wav / violet_noise_mono.flac
├── grey_noise.wav / grey_noise.flac
└── grey_noise_mono.wav / grey_noise_mono.flac
```

## Shell Completion

```bash
# Bash
noisetool --generate-completion bash >> ~/.bashrc

# Zsh
noisetool --generate-completion zsh >> ~/.zshrc

# Fish
noisetool --generate-completion fish > ~/.config/fish/completions/noisetool.fish
```

Completion scripts provide tab-completion for all options, noise types, formats, bit depths, and file paths.

## Docker

```bash
# Build the image
docker build -t noisetool .

# List available noise types
docker run --rm noisetool --list

# Generate noise and save to host directory
docker run --rm -v "$PWD/audio:/audio" noisetool -o /audio

# Generate white noise, mono, WAV only
docker run --rm -v "$PWD/audio:/audio" noisetool --type white --mono -f wav -o /audio
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint with ruff
ruff check .
ruff format .

# Type check with mypy
mypy src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Build distribution packages
python -m build
```

### CI Pipeline

The project runs lint (ruff), type checking (mypy), and tests (pytest) across Python 3.10–3.13 via GitHub Actions. On tagged releases, packages are built and published to PyPI automatically.

## License

MIT
