from pathlib import Path
import yaml
import pandas as pd
import matplotlib.pyplot as plt

from src.io.loader import load_files
from src.processing.pipeline import Pipeline
from src.processing.baseline import psalsa_baseline
from src.processing.normalise import auc_normalise

from src.visualisation.spectra import plot
from src.visualisation.peaks import plot_all_peaks
from src.visualisation.ratios import plot_ratios
from src.visualisation.save import save_plot
from src.visualisation.fitting_peaks import plot_peak_fit


from src.fitting.peak_fitter import fit_peak_range
from src.analysis.ratios import compute_ratios

# -----------------------
# LOAD CONFIG
# -----------------------
with open("config/config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# -----------------------
# INPUT SETTINGS
# -----------------------
input_config = config["input"]

data_folder = input_config["folder"]
indices = input_config.get("indices")
rename = input_config.get("rename")

experiment_name = Path(data_folder).name

# -----------------------
# LOAD DATA
# -----------------------
print(f"\n=== Loading data: {experiment_name} ===")

df = load_files(data_folder, indices, rename)

# -----------------------
# RAW PLOT
# -----------------------
print("Plotting raw data...")

fig_raw = plot(df)
#plt.title("Raw Spectra")
#plt.show()

save_plot(fig_raw, experiment_name, "raw_spectra")

# -----------------------
# PROCESSING PIPELINE
# -----------------------
print("Applying processing pipeline...")

pipe = Pipeline()

processing = config.get("processing", {})

if processing.get("baseline", False):
    print(" - Baseline correction")
    pipe.add(psalsa_baseline)

if processing.get("normalize", False):
    print(" - Normalisation")
    pipe.add(auc_normalise)

df_proc = pipe.run(df)

# -----------------------
# PROCESSED PLOT
# -----------------------
print("Plotting processed data...")

fig_proc = plot(df_proc)
#plt.title("Processed Spectra")
#plt.show()

save_plot(fig_proc, experiment_name, "processed_spectra")

# -----------------------
# PEAK FITTING
# -----------------------
print("Fitting peaks...")

all_results = []

fit_plot_counter = 0

for name, r in config["peaks"]["ranges"].items():

    print(f" - Fitting {name}: {r['bounds']}")

    results, fit_outputs = fit_peak_range(
        df_proc,
        r["bounds"],
        r["peaks"],
        config["peaks"]["tolerance"]
    )

    all_results.extend(results)

    # -----------------------
    # PLOT FITS (NEW)
    # -----------------------
    for fit in fit_outputs:

        fig = plot_peak_fit(
            df_proc,
            fit["params"],
            fit["peaks"],
            fit["bounds"],
            fit["Sample"]
        )

        if fig is not None:

            #plt.show()

            plot_name = f"{name}_{fit['Sample']}"
            save_plot(fig, experiment_name, f"fit_{plot_name}")


df_peaks = pd.DataFrame(all_results)

# -----------------------
# PEAK AREA PLOT
# -----------------------
print("Plotting peak areas...")

fig_peak = plot_all_peaks(df_peaks)
#plt.title("Peak Areas")
#plt.show()

save_plot(fig_peak, experiment_name, "peak_areas")

# -----------------------
# RATIOS
# -----------------------
print("Computing ratios...")

df_ratios = compute_ratios(
    df_peaks,
    config["ratios"]
)

print("\n=== RATIOS ===")
print(df_ratios)

# -----------------------
# RATIO PLOT
# -----------------------
print("Plotting ratios...")

fig_ratio = plot_ratios(df_ratios)
#plt.title("Peak Ratios")
#plt.show()

save_plot(fig_ratio, experiment_name, "ratios")

# -----------------------
# SAVE DATA
# -----------------------
output_folder = Path("outputs") / experiment_name
output_folder.mkdir(parents=True, exist_ok=True)

# df_proc.to_csv(output_folder / f"{experiment_name}_processed.csv", index=False)
# df_peaks.to_csv(output_folder / f"{experiment_name}_peaks.csv", index=False)
# df_ratios.to_csv(output_folder / f"{experiment_name}_ratios.csv", index=False)

print(f"\n✅ All outputs saved to: {output_folder}")
