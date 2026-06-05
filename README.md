# HAMLET — Music-to-Movement Style Analyzer

A CLAP-based engine that scores music tracks against textual choreographic prompts and traditional genre schemes, producing time-aligned probability trajectories that can drive dance/movement synthesis pipelines.

## Features

- **Time-window analysis** of any audio file (MP3 / WAV)
- **CLAP zero-shot scoring** against arbitrary text prompts
- **Configurable schemes** via YAML (no code changes needed)
- **Multi-panel Seaborn plots** of probability trajectories
- **Gradio web UI** + **CLI** + **Python API**

## Installation

```bash
git clone https://github.com/your-org/hamlet-music-analyzer.git
cd hamlet-music-analyzer
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Quick Start

### 1. Launch the web UI

```bash
python app.py
```

Open `http://localhost:7860` in your browser.

### 2. Command-line analysis

```bash
python -m hamlet.cli.run_cli examples/sample_track.mp3 \
    --window 4.0 \
    --temperature 3.0 \
    --output-json my_analysis.json \
    --output-plot my_analysis.png
```

### 3. Programmatic use

```bash
python examples/example_usage.py
```

## Configuration

All schemes (choreographic vocabularies, genres, emotional probes) live in
`config/schemes.yaml`. Runtime defaults (model id, window size, temperature)
live in `config/settings.yaml`. Edit these YAML files freely — no code changes
are required.

## Repository Structure

```
hamlet/
├── backend/      # CLAP engine, plotter, config loader
├── frontend/     # Gradio UI
└── cli/          # Command-line interface
config/           # YAML configs (schemes + settings)
examples/         # Sample usage scripts
```

## License

MIT
