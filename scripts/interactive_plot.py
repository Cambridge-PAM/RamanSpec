from pathlib import Path
import yaml
import matplotlib.pyplot as plt

from src.io.loader import load_files
from src.processing.pipeline import Pipeline
from src.processing.baseline import psalsa_baseline
from src.processing.normalise import auc_normalise
from src.processing.smoothing import smooth

from src.visualisation.spectra import plot,plot_with_baseline

# -----------------------
# LOAD CONFIG
# -----------------------
with open("config/config.yaml") as f:
    config = yaml.safe_load(f)

# -----------------------
# INPUT SETTINGS
# -----------------------
experiment_path = config["input"]["folder"]
experiment_name = Path(experiment_path).name

FOCUS_RANGE = config.get("plotting", {}).get("focus_range", None)

# -----------------------
# LOAD DATA
# -----------------------
print(f"\n=== Interactive Plot: {experiment_name} ===")

df = load_files(
    experiment_path,
    config["input"].get("indices"),
    config["input"].get("rename")
)

# -----------------------
# BUILD PIPELINE
# -----------------------
pipe = Pipeline()

processing = config.get("processing", {})

if processing.get("baseline", False):
    print("Applying baseline correction")
    pipe.add(psalsa_baseline)

if processing.get("normalize", False):
    print("Applying normalisation")
    pipe.add(auc_normalise)

if processing.get("smoothing", False):
    print("Applying smoothing")
    pipe.add(
        smooth,
        window=processing.get("smooth_window", 7),
        poly=processing.get("smooth_poly", 3)
    )

# -----------------------
# PROCESS DATA
# -----------------------
df_proc = pipe.run(df)

# -----------------------
# RAW PLOT
# -----------------------
print("Plotting raw data...")

if config["processing"].get("show_baseline", True):
    fig_base, color_map = plot_with_baseline(df_proc, focus_range=FOCUS_RANGE)
    plt.title("Baseline Correction")
else:
    fig_raw, color_map = plot(df, focus_range=FOCUS_RANGE)
    plt.title("Raw Spectra")
    
# -----------------------
# PROCESSED PLOT
# -----------------------
print("Plotting processed data...")

fig_proc = plot(df_proc, focus_range=FOCUS_RANGE)
plt.title("PROCESSED DATA")

plt.show()   # ✅ interactive window