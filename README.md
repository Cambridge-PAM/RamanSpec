# Raman Cope Analysis

A modular, configurable Python framework for Raman spectroscopy analysis designed for reproducible, publication-quality workflows.

---

# 📌 Overview

This repository provides a complete pipeline for analysing Raman spectroscopy data, including:

- Data ingestion (single spectra and spatial maps)
- Config-driven preprocessing
- Multi-peak Voigt fitting
- Peak area and centre extraction
- Residual-based fit validation
- Ratio calculations
- Batch and interactive workflows
- Automated plotting and output organisation

---

# 📁 Repository Structure

```
raman-cope-analysis/
│
├── config/
│   └── config.yaml          # All settings for analysis
│
├── data/                    # (ignored by git)
│   └── raw/
│       └── experiment_name/
│           ├── file1.txt
│           ├── file2.txt
│           └── ...
│
├── outputs/
│   └── experiment_name/     # Automatically created
│
├── scripts/
│   ├── run_analysis.py
│   ├── batch_run.py
│   └── interactive_plot.py
│
├── src/
│   ├── io/
│   ├── processing/
│   ├── fitting/
│   ├── analysis/
│   └── visualisation/
│
├── environment.yml
└── README.md
```

---

# 📂 Adding Experimental Data

## ✅ Where to place data

All experimental data should be placed in:

```
data/raw/<experiment_name>/
```

### Example:

```
data/raw/expt_PS22/
    spectrum_001.txt
    spectrum_002.txt
```

Each folder represents a **single experiment**.

---

## ✅ Supported Data Formats

The loader automatically detects common Raman formats.

### 1. Single Spectra (2 columns)

```
RamanShift    Intensity
100           123
101           130
...
```

- First column → Raman shift (cm⁻¹)
- Second column → intensity

---

### 2. Spatial Mapping Data (4 columns)

```
X    Y    RamanShift    Intensity
0    0    100           123
0    0    101           130
...
```

- Includes spatial coordinates (µm)
- Automatically normalised (X, Y shifted to origin)

---

## ⚠️ Data Requirements

- Files must be `.txt`
- Columns separated by whitespace or tabs
- No headers required (auto-handled)
- Spectra should be continuous in Raman shift

---

# ⚙️ Configuration

All behaviour is defined in:

```
config/config.yaml
```

## Example

```yaml
input:
  folder: data/raw/expt_PS22
  indices: null
  rename: null

processing:
  baseline: true
  normalize: true
  smoothing: false

peaks:
  tolerance: 5

  ranges:
    range1:
      bounds: [630, 720]
      peaks: [650, 669, 681, 705]

    range2:
      bounds: [1700, 1750]
      peaks: [1720]

ratios:
  - [681, 669]
  - [1720, 681]

plotting:
  focus_range: null
```

---

# ▶️ Running the Analysis

## Full analysis

```bash
python scripts/run_analysis.py
```

This will:

1. Load data
2. Plot raw spectra
3. Apply processing pipeline
4. Plot processed spectra
5. Fit peaks (with residuals)
6. Extract peak parameters
7. Compute ratios
8. Save all outputs

---

## Batch processing

```bash
python scripts/batch_run.py
```

Processes all folders inside `data/raw/`.

---

## Interactive plotting

```bash
python scripts/interactive_plot.py
```

Features:
- Raw vs processed comparison
- Linked zoom
- Pipeline debugging

---

# 📊 Output Structure

```
outputs/
    expt_PS22/
        expt_PS22__raw_spectra__timestamp.png
        expt_PS22__processed_spectra__timestamp.png
        expt_PS22__peak_areas__timestamp.png
        expt_PS22__ratios__timestamp.png

        expt_PS22__fit_range1_sample1__timestamp.png
        expt_PS22__fit_range2_sample1__timestamp.png

        expt_PS22_processed.csv
        expt_PS22_peaks.csv
        expt_PS22_ratios.csv
```

---

# 🔬 Peak Fitting

- Uses Voigt functions (Gaussian + Lorentzian)
- Fits multiple peaks per region
- Applies centre constraints (± tolerance)

Each fit includes:
- Data points
- Individual peaks
- Total fit
- Residuals (fit quality check)

---

# 📈 Ratio Analysis

Ratios are computed from integrated peak areas:

```yaml
ratios:
  - [681, 669]
```

Outputs include:
- Table of ratios
- Comparison plots

---

# 🧠 Design Philosophy

- Reproducible (config-driven)
- Modular (easy to extend)
- Transparent (visual fit validation)
- Scalable (batch processing support)

---

# 🚀 Future Extensions

- GUI interface (Streamlit)
- Automatic peak detection
- Parallel processing
- Report generation (PDF/HTML)

---

# 👤 Author

Thomas Williamson
