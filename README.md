# Raman Cope Analysis

A modular, configurable Python framework for Raman spectroscopy analysis.

## Features

- Data loading for Raman spectra and spatial maps
- Baseline correction and normalization
- Config-driven peak selection
- Voigt peak fitting
- Residual analysis for fit quality
- Ratio calculations
- Batch processing
- Automatic plot saving

## Installation

```bash
conda env create -f environment.yml
conda activate raman-cope-env
```

## Usage

Run full analysis:

```bash
python scripts/run_analysis.py
```

Batch processing:

```bash
python scripts/batch_run.py
```

Interactive plotting:

```bash
python scripts/interactive_plot.py
```

## Config

All parameters are controlled in:

```
config/config.yaml
```

## Output

Results are stored in:

```
outputs/<experiment_name>/
```

Includes:
- Plots (raw, processed, fits, ratios)
- Processed data (CSV)
- Peak tables
- Ratio tables

## Author
Thomas Williamson
