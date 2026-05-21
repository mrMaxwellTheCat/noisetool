# Noise Generator

Generate high-quality **white noise**, **pink noise (1/f)**, and **brown noise (1/f^2)** audio files with LUFS loudness normalization.

## Features

- Three noise types: white, pink (1/f), brown (1/f^2)
- Stereo and mono output
- WAV and FLAC formats with selectable bit depth (16, 24, 32-bit)
- ITU-R BS.1770-4 LUFS loudness measurement
- Target loudness normalization for streaming/broadcast standards
- Reproducible output with configurable random seed
- Configurable sample rate and duration
- Parallel processing support

## Installation

```bash
pip install noisetool
```

Or install from source:

```bash
git clone https://github.com/mrMaxwellTheCat/noise.git
cd noise
pip install -e ".[dev]"
```

## Usage

```bash
# Generate all noise types (defaults: 30s, stereo+mono, both WAV+FLAC)
noisetool

# Generate white noise only, mono, WAV, normalized to -14 LUFS
noisetool --type white --mono -f wav --lufs -14

# Generate pink noise at 96 kHz, 60 seconds, with seed for reproducibility
noisetool --type pink --duration 60 --sample-rate 96000 --seed 42

# Measure loudness without saving files
noisetool --measure

# Generate brown noise normalized to broadcast standard (-23 LUFS)
noisetool --type brown --lufs -23

# Verbose output for debugging
noisetool -v
```

### Command-line options

| Argument | Description | Default |
|----------|-------------|---------|
| `-t, --type` | Noise type: `all`, `white`, `pink`, `brown` | `all` |
| `-d, --duration` | Duration in seconds | `30` |
| `-r, --sample-rate` | Sample rate in Hz | `44100` |
| `--mono` | Mono output only | stereo + mono |
| `--stereo` | Stereo output only | stereo + mono |
| `-o, --output-dir` | Output directory | `audio/` |
| `-f, --format` | Format: `all`, `wav`, `flac` | `all` |
| `--bit-depth` | Bit depth: `16`, `24`, `32` | `24` |
| `--lufs` | Target LUFS loudness | off |
| `--measure` | Measure loudness, no file output | off |
| `--seed` | Random seed for reproducibility | random |
| `-v, --verbose` | Verbose/debug logging | off |

## Algorithms

- **White noise**: uniform random samples in [-1, 1]. Flat power spectrum.
- **Pink noise (1/f)**: FFT-based frequency-domain filtering. White noise is transformed to frequency domain, multiplied by a `1/√f` filter, then inverse-transformed. Spectrum decays 3 dB/octave.
- **Brown noise (1/f²)**: cumulative sum (integration) of white noise. Spectrum decays 6 dB/octave.

## Loudness (LUFS)

This tool implements ITU-R BS.1770-4 for integrated loudness measurement. Use `--lufs TARGET` to normalize:

- **-14 LUFS**: Streaming standard (YouTube, Spotify, Apple Music)
- **-23 LUFS**: Broadcast standard (EBU R128, ATSC A/85)
- **-16 LUFS**: Podcast standard

## Output files

Generated audio files follow this naming convention:

```
audio/
├── white_noise.wav / white_noise.flac        (stereo)
├── white_noise_mono.wav / white_noise_mono.flac  (mono)
├── pink_noise.wav / pink_noise.flac
├── pink_noise_mono.wav / pink_noise_mono.flac
├── brown_noise.wav / brown_noise.flac
└── brown_noise_mono.wav / brown_noise_mono.flac
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint and format
ruff check .
ruff format .

# Type check
mypy src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files

# Build distribution packages
python -m build
```

## License

MIT
