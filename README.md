# Noise Generator

Generates high-quality **white noise**, **pink noise**, and **brown noise** audio files in WAV (24-bit) and FLAC format.

## Files

### Audio (estéreo y mono, 30s, 44100 Hz, 24-bit)

| Archivo | Tipo | Canales |
|---|---|---|
| `white_noise.wav` / `white_noise.flac` | White noise | Estéreo |
| `white_noise_mono.wav` / `white_noise_mono.flac` | White noise | Mono |
| `pink_noise.wav` / `pink_noise.flac` | Pink noise (1/f) | Estéreo |
| `pink_noise_mono.wav` / `pink_noise_mono.flac` | Pink noise (1/f) | Mono |
| `brown_noise.wav` / `brown_noise.flac` | Brown noise (1/f²) | Estéreo |
| `brown_noise_mono.wav` / `brown_noise_mono.flac` | Brown noise (1/f²) | Mono |

### Código

- `code/generate_noise.py` — Script de generación programática.

## Algoritmos

- **White noise**: muestras aleatorias uniformes en [-1, 1]. Espectro plano.
- **Pink noise (1/f)**: transformada de Fourier de ruido blanco, filtro `1/√f` en frecuencia, inversa de Fourier. Espectro decae 3 dB/octava.
- **Brown noise (1/f²)**: suma acumulativa (integración) de ruido blanco. Espectro decae 6 dB/octava.

## Requisitos

- Python 3
- `numpy`
- `scipy`
- `soundfile`

Instalación:

```bash
pip install numpy scipy soundfile
```

## Regenerar

```bash
python3 code/generate_noise.py
```

Los archivos se generan en el directorio raíz del proyecto.
