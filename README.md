# Raman Cope Analysis

A Python codebase for analysising Raman spectroscopy data, both as point spectra and area/depth maps, particularly for analysing individual peaks, peak ratio and intensity variations. Used in the context of analysising spatial variation of composition in polymer films.

# 📌 Overview

This repository provides a complete pipeline for analysing Raman spectroscopy data, including config-driven scripts for:
  - Bulk analysis of experimental data, e.g. peak-fitting and mapping
  - Interactive plot to alter processing and observe variations

Functions include:
- Data loading (single spectra and spatial maps)
- Multi-peak Voigt fitting
- Peak parameter extraction
- Residual-based fit validation
- Fitted peak Ratio calculations
- Automated plotting and output organisation

# 📁 Repository Structure

```
raman-spec/
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
data/raw/expt_1/
    spectrum_001.txt
    spectrum_002.txt
```

Each folder represents a **single experiment**.

---

## ✅ Supported Data Formats

The loader assumes a 2- (shift, intensity) or 4- (x,y,shift,intensity or r,z,shift,intensity) column tab-separated file as generated from a Renishaw Invia Confocal Raman microscope.

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
OR

```
R    Z    RamanShift    Intensity
0    0    100           123
0    0    101           130
...
```

- Includes spatial coordinates (µm)
- Automatically normalised (e.g. X, Y shifted to origin)

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
  folder: data/raw/expt_1
  indices: [0,1,4,8] # extract just the files at these indices
  rename: ['Point 1', 'Point 2', 'Point 5', 'Point 9']
  
analysistype: 'non-positional' # 'positional' or 'non-positional'

plotting:
  focus_range: [300, 3000]
  offset:
      enabled: true
      step: 0.0012  # vertical offset between spectra
  mappingmode: "pixel" # "pixel", "scatter", "interp" or "hybrid"

processing:
  baseline: true
  normalize: true
  smoothing: false
  show_baseline: true

peaks:
  tolerance: 0.5

  ranges:
    range1:
      bounds: [700, 800]
      peaks: [710,756, 780]

    range2:
      bounds: [1680, 1750]
      peaks: [1715]

ratios:
  - [1715, 756]
```

---

# ▶️ Running the Analysis

## Load environment
```bash
git clone https://github.com/Cambridge-PAM/RamanSpec
cd RamanSpec
conda env create -f environment.yml
conda activate ramanspec-env
```
---

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

## Interactive plotting

```bash
python scripts/interactive_plot.py
```

Features:
- Raw vs processed comparison
- Linked zoom
- Pipeline debugging



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

# 👤 Author

Tom Williamson
