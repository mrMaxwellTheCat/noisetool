# noisetool

[![CI](https://github.com/mrMaxwellTheCat/noise/actions/workflows/ci.yml/badge.svg)](https://github.com/mrMaxwellTheCat/noise/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/noisetool)](https://pypi.org/project/noisetool/)
[![Python versions](https://img.shields.io/pypi/pyversions/noisetool)](https://pypi.org/project/noisetool/)
[![License](https://img.shields.io/pypi/l/noisetool)](https://github.com/mrMaxwellTheCat/noise/blob/master/LICENSE)
[![Codecov](https://codecov.io/gh/mrMaxwellTheCat/noise/branch/master/graph/badge.svg)](https://codecov.io/gh/mrMaxwellTheCat/noise)

**High-quality noise generator** — Generate white, pink, brown, blue, violet, and grey noise audio files with LUFS loudness normalization, audio effects, analysis tools, and parallel batch processing.

## Features

- **6 noise types** — White, pink (1/f), brown (1/f²), blue (√f), violet (f), grey (psychoacoustic)
- **Multi-format output** — WAV, FLAC, AIFF, OGG Vorbis, and raw PCM, in any combination
- **Stereo & mono** — Generate both simultaneously or pick one
- **ITU-R BS.1770-4 LUFS** — Loudness measurement and normalization to streaming/broadcast/podcast targets
- **Peak & RMS normalization** — Target peak dB level or RMS dBFS
- **16 audio effects** — DC blocker, fade-in/out, reverse, phase invert, low/high/band-pass filter, ADSR envelope, stereo width, pan, tremolo, bitcrush, dither, compressor
- **Analysis tools** — ASCII waveform preview, ASCII spectrum, EQ visualization, detailed stats table, JSON/CSV export
- **Audio playback** — Play generated audio through system output
- **File analysis** — Inspect existing audio files with `--info`
- **Custom blends** — Mix multiple noise types with weighted ratios
- **Loop mode** — Generate seamless looping noise with crossfade
- **Parallel generation** — Multi-threaded batch processing for all types/formats/channels
- **Continuous mode** — Generate noise indefinitely until Ctrl+C
- **Reproducible** — Set `--seed` or `--seeds` (comma-separated) for deterministic output
- **Custom filename patterns** — Use `{type}`, `{channels}`, `{format}`, `{sr}`, `{bits}`, `{seed}` variables
- **Interactive wizard** — Step-by-step UI with quick presets or full custom configuration
- **Config files** — JSON and YAML configs for repeatable batch generation
- **Shell completion** — Tab-completion for bash, zsh, fish
- **Dry-run mode** — Preview file list without writing anything
- **Benchmark** — Measure noise generator performance
- **Doctor** — System diagnostics (`--doctor`)
- **Docker** — Containerized execution
- **Rich terminal UI** — Color-coded output, progress bars, banners, and tables

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

### Wizard mode (no arguments — interactive)

```bash
noisetool
```

Launches an interactive wizard. Choose **quick mode** (pick a preset: streaming, broadcast, podcast, quick, loop) or **custom mode** (select noise types, channels, duration, format, sample rate, loudness target, output folder).

### CLI mode

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

# Generate all types in parallel with multiple workers
noisetool --parallel --workers 4

# Mix two noise types
noisetool --mix pink=0.7,white=0.3

# Inspect an existing audio file
noisetool --info audio/pink_noise.wav

# Run benchmark
noisetool --benchmark

# System diagnostics
noisetool --doctor
```

## Full CLI Reference

### Noise Generation

| Argument | Description | Default |
|----------|-------------|---------|
| `-t, --type` | Noise type: `all`, `white`, `pink`, `brown`, `blue`, `violet`, `grey` | `all` |
| `-d, --duration` | Duration in seconds | `30` |
| `-r, --sample-rate` | Sample rate in Hz | `44100` |
| `--mono` | Generate mono audio only | stereo + mono |
| `--stereo` | Generate stereo audio only | stereo + mono |
| `--mix` | Mix multiple noise types with weights (e.g., `pink=0.7,white=0.3`) | off |
| `--seed` | Random seed for reproducible generation | random |
| `--seeds` | Generate with multiple seeds, comma-separated (e.g., `42,123,456`) | off |
| `--pattern` | Custom filename pattern (variables: `{type}`, `{channels}`, `{format}`, `{sr}`, `{bits}`, `{seed}`) | default naming |
| `-o, --output-dir` | Output directory | `audio/` |

### Audio Format

| Argument | Description | Default |
|----------|-------------|---------|
| `-f, --format` | Output format: `all`, `wav`, `flac`, `aiff`, `ogg`, `raw` | `all` (wav + flac) |
| `--bit-depth` | Bit depth: `16`, `24`, `32` | `24` |
| `--loop` | Generate seamless looping noise (cross-fade start/end to avoid clicks) | off |

### Loudness & Level

| Argument | Description | Default |
|----------|-------------|---------|
| `--lufs TARGET` | Target loudness in LUFS (e.g., `-14` for streaming, `-23` for broadcast) | off |
| `--peak LEVEL` | Peak normalize to target level in dB (e.g., `-1.0` to prevent clipping) | off |
| `--normalize TARGET` | Convenience: set loudness target (e.g., `-14`, `-23`, `-16`). Sets `--lufs` and `--peak -1` | off |
| `--rms DBFS` | RMS-normalize to target level in dBFS (e.g., `-18`) | off |
| `--measure` | Measure and display loudness of generated noise without saving files | off |

### Effects & Processing

Effects are applied in this order: LUFS normalization → peak normalization → DC blocker → fade-in → fade-out → reverse → phase invert → lowpass → highpass → bandpass → ADSR envelope → loop crossfade → stereo width → pan → tremolo → bitcrush → dither → compressor → RMS normalization.

| Argument | Description | Format |
|----------|-------------|--------|
| `--dc-block` | Remove DC offset using a high-pass IIR filter (α = 0.995) | flag |
| `--fade-in SECONDS` | Linear fade-in at start | float |
| `--fade-out SECONDS` | Linear fade-out at end | float |
| `--reverse` | Reverse audio in time | flag |
| `--invert` | Invert phase (multiply by -1) | flag |
| `--lowpass HZ` | Low-pass filter cutoff frequency (FFT brickwall) | float |
| `--highpass HZ` | High-pass filter cutoff frequency (FFT brickwall) | float |
| `--bandpass LOW,HIGH` | Band-pass filter (e.g., `20,20000`) | `low,high` |
| `--envelope A,D,S,R` | ADSR envelope (e.g., `0.1,0.2,0.7,0.3`) | `attack,decay,sustain,release` |
| `--width WIDTH` | Stereo width (0=mono, 1=original, >1=wider) | float |
| `--pan PAN` | Pan position (-1=left, 0=center, 1=right) | float |
| `--tremolo RATE,DEPTH` | Amplitude modulation (e.g., `5,0.5`) | `rate_hz,depth` |
| `--bitcrush BITS` | Bitcrushing (1-24 bits) | int |
| `--dither BITS` | Dithering for target bit depth (e.g., `16`), with noise shaping | int |
| `--compressor THRESH,RATIO` | Dynamic range compression (e.g., `-20,4`) | `threshold_db,ratio` |

### Output & Analysis

| Argument | Description |
|----------|-------------|
| `--preview` | Show ASCII waveform preview of generated audio |
| `--spectrum` | Show ASCII frequency spectrum visualization (FFT-based, Hanning windowed) |
| `--eq-viz` | Show EQ filter response plot |
| `--stats` | Show detailed audio statistics (duration, samples, channels, sample rate, bit depth, peak, peak dBFS, RMS, RMS dBFS, crest factor, DC offset) |
| `--json FILE` | Save audio statistics as JSON |
| `--csv FILE` | Save audio statistics as CSV |
| `--play` | Play audio through system output (requires `sounddevice`) |
| `--info FILE` | Show detailed info about an existing audio file |
| `--list` | List available noise types with descriptions and exit |
| `--benchmark` | Run performance benchmark of all noise generators and exit |
| `--dry-run` | Show what would be generated without creating files |

### Operation Mode

| Argument | Description | Default |
|----------|-------------|---------|
| `--parallel` | Generate files in parallel using multiple threads | off |
| `--workers N` | Number of worker threads for parallel generation | CPU count |
| `--continuous` | Generate noise continuously until Ctrl+C interrupted | off |
| `-i, --interactive` | Force interactive wizard mode | auto if no args |

### Configuration

| Argument | Description |
|----------|-------------|
| `--config FILE` | Load generation config from JSON or YAML file |
| `--example-config FILE` | Write an example config file (JSON or YAML, inferred from extension) and exit |
| `--generate-completion SHELL` | Generate shell completion script: `bash`, `zsh`, or `fish` |
| `--preset NAME` | Apply a preset configuration: `streaming`, `broadcast`, `podcast`, `quick`, `loop` |

### Logging & Display

| Argument | Description | Default |
|----------|-------------|---------|
| `-v, --verbose` | Enable verbose / debug output | off |
| `--silent` | Suppress all terminal output except errors | off |
| `--progress` | Progress display style: `rich`, `simple`, `none` | `rich` |
| `--log-file FILE` | Write log output to a file in addition to stderr | off |
| `--no-banner` | Suppress the startup banner | off |
| `--doctor` | Run system diagnostics and exit | off |
| `--version` | Show version and exit | off |

## Noise Types

| Type | Description | Spectrum | Generation Method |
|------|-------------|----------|-------------------|
| `white` | Flat power spectrum across all frequencies | Flat | Uniform random samples in [-1, 1] |
| `pink` | Power decreases 3 dB/octave (1/f spectrum) | −3 dB/octave | FFT frequency-domain filtering with `1/√f` filter |
| `brown` | Power decreases 6 dB/octave (1/f² spectrum) | −6 dB/octave | Cumulative sum (integration) of white noise |
| `blue` | Power increases 3 dB/octave (rising spectrum) | +3 dB/octave | FFT frequency-domain filtering with `√f` filter |
| `violet` | Power increases 6 dB/octave (rising spectrum) | +6 dB/octave | FFT frequency-domain filtering with `f` filter |
| `grey` | Psychoacoustic equal-loudness noise | Perceptually flat | FFT filtering with `1/(1+(f/2000)²)` filter |

## Interactive Wizard

Running `noisetool` with no arguments launches the interactive wizard.

### Quick mode

Select from 5 presets:

| Preset | Type | Duration | Sample Rate | Bit Depth | LUFS | Format |
|--------|------|----------|-------------|-----------|------|--------|
| `streaming` | all | 30s | 48000 | 24 | -14 | all |
| `broadcast` | all | 30s | 48000 | 24 | -23 | all |
| `podcast` | pink | 10s | 44100 | 16 | -16 | wav (mono) |
| `quick` | pink | 5s | 44100 | 16 | — | wav (mono) |
| `loop` | pink | 10s | 44100 | 24 | — | flac |

Then choose an output folder.

### Custom mode

Step through every option:

1. **Noise Types** — Select by number (1=white, 2=pink, 3=brown, 4=blue, 5=violet, 6=grey), comma-separated, or `all`
2. **Channels** — Stereo, Mono, or Both
3. **Duration** — Seconds (set `0` for continuous generation)
4. **Format** — WAV, FLAC, OGG, MP3 (saved as WAV), or WAV+FLAC, with quality/bit-depth/compression setting
5. **Sample Rate** — 44100, 48000, 96000, or 192000 Hz
6. **Loudness** — None, streaming (-14 LUFS), broadcast (-23 LUFS), podcast (-16 LUFS), or custom
7. **Output Folder** — Default `audio/`

## LUFS Loudness Normalization

Implements **ITU-R BS.1770-4** for integrated loudness measurement using K-weighting (pre-filter + RLB weighting) with two IIR filter stages.

### Common targets

| Target | Standard | Use Case |
|--------|----------|----------|
| **−14 LUFS** | Streaming | YouTube, Spotify, Apple Music, Tidal |
| **−16 LUFS** | Podcasts | Podcast loudness standard |
| **−23 LUFS** | Broadcast | EBU R128, ATSC A/85 (TV, radio) |
| **−18 LUFS** | Film | Cinema trailer and film mixing |

If normalization causes clipping, the signal is automatically limited to prevent distortion.

## Config File Example

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
    "rms": null,
    "seed": 42,
    "seeds": null,
    "output_dir": "audio",
    "mono": false,
    "stereo": false,
    "mix": "pink=0.7,white=0.3",
    "pattern": null,
    "loop": false,
    "parallel": false,
    "workers": null,
    "continuous": false,
    "dc_block": false,
    "fade_in": 0.1,
    "fade_out": 0.3,
    "reverse": false,
    "invert": false,
    "lowpass": null,
    "highpass": null,
    "bandpass": null,
    "envelope": null,
    "width": null,
    "pan": null,
    "tremolo": null,
    "bitcrush": null,
    "dither": null,
    "compressor": null,
    "preview": false,
    "spectrum": false,
    "eq_viz": false,
    "stats": false,
    "play": false,
    "dry_run": false,
    "silent": false,
    "progress": "rich"
}
```

YAML configs are also supported (requires `pyyaml`):

```bash
noisetool --example-config config.yaml
noisetool --config config.yaml
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

## Output Files

Generated audio files follow this naming convention (default pattern):

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

Use `--pattern` for custom filenames, e.g.:

```bash
noisetool --pattern "{type}_{channels}_{format}_{sr}hz_{bits}bit"
```

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

# Run with Docker diagnostics
docker run --rm noisetool --doctor
```

The Docker image uses a multi-stage build for minimal size (slim Python image + libsndfile1).

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

### Project structure

```
src/noise/
├── __init__.py          # Version
├── cli.py               # CLI argument parsing and main orchestration
├── interactive.py       # Interactive wizard (quick + custom modes)
├── generator.py         # 6 noise generators + mix function
├── effects.py           # 16 audio effects
├── formats.py           # AIFF, OGG, RAW savers
├── utils.py             # WAV, FLAC savers, constants
├── lufs.py              # ITU-R BS.1770-4 loudness measurement + normalization
├── analysis.py          # AudioStats, ASCII spectrum, JSON/CSV export
├── preview.py           # ASCII waveform visualization
├── config.py            # Config file loading (JSON/YAML)
├── completion.py        # Shell completion script
└── ui.py                # Rich terminal output components
```

## CI/CD

The project runs on GitHub Actions across **Python 3.10–3.14**:

- **Lint**: `ruff check` with selected rules (E, F, I, N, W, UP, B, SIM, ARG, C4)
- **Format**: `ruff format --check`
- **Type check**: `mypy` strict mode
- **Test**: `pytest` with coverage (pytest-cov)
- **Coverage**: Uploaded to Codecov
- **Publish**: On tagged releases, builds and publishes to PyPI via `pypa/gh-action-pypi-publish`

## License

MIT
