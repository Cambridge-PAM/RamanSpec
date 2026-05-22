from pathlib import Path
import yaml
import matplotlib.pyplot as plt

from src.io.loader import load_files
from src.processing.pipeline import Pipeline
from src.processing.baseline import psalsa_baseline
from src.processing.normalise import auc_normalise
from src.processing.smoothing import smooth

from src.visualisation.plot_interactive_widgets import plot_interactive_with_widgets

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

df_raw = load_files(
    experiment_path,
    config["input"].get("indices"),
    config["input"].get("rename")
)

# Plot interactively
plot_interactive_with_widgets(df_raw)