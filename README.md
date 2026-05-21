# Noise Generator

Generates high-quality **white noise**, **pink noise**, and **brown noise** audio files in WAV (24-bit) and FLAC format.

## Files

### Audio (estéreo y mono, 30s, 44100 Hz, 24-bit)

| Archivo | Tipo | Canales |
|---|---|---|
Todos los archivos de audio se encuentran en la subcarpeta `audio/`.

| Archivo | Tipo | Canales |
|---|---|---|
| `audio/white_noise.wav` / `audio/white_noise.flac` | White noise | Estéreo |
| `audio/white_noise_mono.wav` / `audio/white_noise_mono.flac` | White noise | Mono |
| `audio/pink_noise.wav` / `audio/pink_noise.flac` | Pink noise (1/f) | Estéreo |
| `audio/pink_noise_mono.wav` / `audio/pink_noise_mono.flac` | Pink noise (1/f) | Mono |
| `audio/brown_noise.wav` / `audio/brown_noise.flac` | Brown noise (1/f²) | Estéreo |
| `audio/brown_noise_mono.wav` / `audio/brown_noise_mono.flac` | Brown noise (1/f²) | Mono |

### Código

- `code/generate_noise.py` — Script de generación programática.
- `requirements.txt` — Dependencias de Python.

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
pip install -r requirements.txt
```

## Regenerar

```bash
python3 code/generate_noise.py
```

Los archivos se generan en la carpeta `audio/`.
