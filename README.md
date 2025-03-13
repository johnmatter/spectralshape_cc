# Spectral Shape CC for Coldtype Animations

A pipeline for creating responsive typography animations in [Coldtype](https://coldtype.xyz) driven by audio data.

## Overview

This repository demonstrates a complete pipeline for:

1. Extracting spectral features from audio files using [FLUCOMA](https://www.flucoma.org/) and [SuperCollider](https://supercollider.github.io/)
2. Converting these features to MIDI Control Change (CC) messages
3. Using the MIDI data to drive dynamic typography animations in Coldtype
4. Visualizing the extracted features for analysis

## Audio Source
Example audio file in this repository:
- `media/wren.wav` - Wren bird song from [BBC Sound Effects](https://sound-effects.bbcrewind.co.uk/search?q=NHU05104304)

## Pipeline Components

### 1. Feature Extraction & MIDI Creation

The `write_spectral_shape_cc.sh` script:
- Takes an audio file as input
- Uses SuperCollider with FLUCOMA to extract spectral shape features (centroid, spread, skewness, kurtosis, etc.)
- Normalizes these features to MIDI CC range (0-127)
- Writes them as a properly formatted MIDI file with embedded parameter names

### 2. Visualization (Diagnostic Tool)

The `plot_cc.py` script:
- Visualizes MIDI CC values from the generated MIDI file
- Shows how parameters change over time
- Reads parameter names embedded in the MIDI file
- Useful for analyzing which features might work best for animation

### 3. Coldtype Animation

The `ct_spectralshape.py` script:
- Reads the MIDI file containing CC data representing spectral features
- Maps MIDI CC to animation parameters

## Requirements

- [Coldtype](https://coldtype.xyz)
- [SuperCollider](https://supercollider.github.io/)
- [FLUCOMA](https://www.flucoma.org/) for SuperCollider
- Python libraries: `mido`, `matplotlib`
- Command-line tools: `csvmidi` (part of [midifile tools](https://www.fourmilab.ch/webtools/midicsv/); available through [homebrew](https://formulae.brew.sh/formula/midicsv))

## Usage

### 1. Extract Spectral Features

```bash
./write_spectral_shape_cc.sh input_audio.wav [output_midi.midi]
```

If no output file is specified, it will use the same name as the input with a `.midi` extension.

### 2. Visualize Features (Optional)

```bash
python plot_cc.py your_file.midi
```

### 3. Create Animation

Edit the `ct_spectralshape.py` script to customize the animation, then run:

```bash
coldtype ct_spectralshape.py
```

## License
- This project: GNU GPL v3
- [FLUCOMA](https://www.flucoma.org/): BSD 3-Clause