from pathlib import Path
import yaml
import pandas as pd
import matplotlib.pyplot as plt

from src.io.loader import load_files
from src.processing.pipeline import Pipeline
from src.processing.baseline import psalsa_baseline
from src.processing.normalise import auc_normalise
from src.processing.smoothing import smooth

from src.visualisation.spectra import plot
from src.visualisation.peaks import plot_all_peaks
from src.visualisation.ratios import plot_ratios
from src.visualisation.save import save_plot
from src.visualisation.fitting_peaks import plot_peak_fit
from src.visualisation.peak_ratio_comparison import plot_peak_ratio_comparison

from src.fitting.peak_fitter import fit_peak_range
from src.analysis.ratios import compute_ratios


from src.visualisation.mapping import (
    build_ratio_map_from_df,
    build_peak_param_map_from_df,
    build_intensity_map,
    plot_map
)


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
analysis_type = config["analysistype"]
map_mode = config["plotting"].get("mappingmode", "pixel")

# -----------------------
# LOAD DATA
# -----------------------
print(f"\n=== Loading data: {experiment_name} ===")

df = load_files(data_folder, indices, rename)

isPositional = any(col in df.columns for col in ["X_um", "Y_um", "R_um", "Z_um"])
if not isPositional and analysis_type == "positional":
    print("⚠️  Warning: Data does not contain positional information but analysis type is set to 'positional'. Proceeding with non-positional analysis.")   
    analysis_type = "non-positional"
    
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
    
if processing.get("smoothing", False):
    print(" - Smoothing")
    pipe.add(smooth)

df_proc = pipe.run(df)

# -----------------------
# PEAK FITTING
# -----------------------
print("Fitting peaks...")

all_results = []
all_fit_outputs = []

for range_name, r in config["peaks"]["ranges"].items():

    print(f"\n--- Fitting {range_name} ({r['bounds']}) ---")

    results, fit_outputs = fit_peak_range(
        df_proc,
        r["bounds"],
        r["peaks"],
        config["peaks"]["tolerance"]
    )

    all_results.extend(results)
    all_fit_outputs.extend(fit_outputs) 

    # ✅ LOOP OVER EVERY SAMPLE FIT
    if analysis_type == "non-positional":
        for fit in fit_outputs:

            sample = fit["Sample"]
            
            fig = plot_peak_fit(
                df_proc,
                fit["params"],
                fit["peaks"],
                fit["bounds"],
                sample
            )

            if fig is None:
                print('none')
                continue

            # ✅ UNIQUE NAME PER FIT
            plot_name = f"{range_name}__{sample}"

            save_plot(fig, experiment_name, f"fit_{plot_name}")

# -----------------------
# RATIOS
# -----------------------
df_peaks = pd.DataFrame(all_results)
print("Computing ratios...")

df_ratios = compute_ratios(
    df_peaks,
    config["ratios"]
)

#print("\n=== RATIOS ===")
#print(df_ratios)


if analysis_type == "non-positional":
    # -----------------------
    # RAW PLOT
    # -----------------------
    print("Plotting raw data...")
    fig_raw, style_map = plot(df)
    plt.title("Raw Spectra")

    save_plot(fig_raw, experiment_name, "raw_spectra")

    # -----------------------
    # PROCESSED PLOT
    # -----------------------
    print("Plotting processed data...")

    offset_step = None
    if config["plotting"]["offset"].get("enabled", False):
        offset_step = config["plotting"]["offset"].get("step", None)

    fig_proc, style_map = plot(df_proc, style_map=style_map, offset_step=offset_step)
    #plt.title("Processed Spectra")
    #plt.show()

    save_plot(fig_proc, experiment_name, "processed_spectra")
    
    # -----------------------
    # COMPARE KEY PEAKS
    # -----------------------

    print("Plotting fitted peak comparisons...")

    fig_compare, style_map = plot_peak_ratio_comparison(
        all_fit_outputs,
        config["ratios"],
        config["peaks"]["tolerance"],
        style_map=style_map
    )

    save_plot(fig_compare, experiment_name, "peak_ratio_comparison")

    # -----------------------
    # PEAK INTENSITY PLOT
    # -----------------------
    print("Plotting peak intensities...")

    fig_peak = plot_all_peaks(df_peaks)
    #plt.title("Peak Intensities")
    #plt.show()

    save_plot(fig_peak, experiment_name, "peak_area")

    # -----------------------
    # RATIO PLOTS
    # -----------------------
    print("Plotting ratios")
    fig_ratio, style_map = plot_ratios(df_ratios, style_map=style_map)
    #plt.title("Peak Ratios")
    #plt.show()

    save_plot(fig_ratio, experiment_name, "ratios")

elif analysis_type == "positional":
    
    print("\n=== Generating positional maps ===")

    tol = config["peaks"]["tolerance"]

    # -----------------------
    # GROUP BY BASE SAMPLE
    # -----------------------
    sample_groups = {}

    for sample_name in df["Sample"].unique():

        # Base sample = everything before coordinate suffix
        if "_X" in sample_name:
            base = sample_name.split("_X")[0]
        elif "_R" in sample_name:
            base = sample_name.split("_R")[0]
        else:
            base = sample_name

        if base not in sample_groups:
            sample_groups[base] = []

        sample_groups[base].append(sample_name)

    # -----------------------
    # LOOP: sample → maps
    # -----------------------
    for sample_name, sample_labels in sample_groups.items():

        print(f"\n ==> Processing sample: {sample_name}")

        # -----------------------
        # RATIO MAPS
        # -----------------------
        for ratio_pair in config["ratios"]:
        
            df_sample = df_peaks[df_peaks["Sample"].isin(sample_labels)]
            coord_type = df_sample["CoordType"].iloc[0] if "CoordType" in df_sample.columns else "XY"

            map_data = build_ratio_map_from_df(
                df_sample,
                ratio_pair,
                tol
            )
            
            print(f" [-] {sample_name}, {ratio_pair} → map points:", len(map_data))
            
            fig = plot_map(
                map_data,
                title=f"{sample_name}: {ratio_pair[0]} / {ratio_pair[1]} Raman Shift (cm⁻¹) Peak Ratio",
                label="Ratio",
                plotmode=map_mode,
                coord_type=coord_type
            )


            if fig:
                save_plot(
                    fig,
                    experiment_name,
                    f"{sample_name}_ratio_map_{ratio_pair[0]}_{ratio_pair[1]}"
                )


        # -----------------------
        # PEAK PARAMETER MAPS
        # -----------------------
        print(f" => Generating peak parameter maps for {sample_name}...")

        target_peaks = sorted(set([p for pair in config["ratios"] for p in pair]))

        for peak in target_peaks:

            for mode in ["Amplitude", "Center", "Sigma", "Gamma", "PeakArea"]:

                df_sample = df_peaks[df_peaks["Sample"].isin(sample_labels)]
                coord_type = df_sample["CoordType"].iloc[0] if "CoordType" in df_sample.columns else "XY"

                map_data = build_peak_param_map_from_df(
                    df_sample,
                    peak,
                    tol,
                    mode
                )

                fig = plot_map(
                    map_data,
                    title=f"{sample_name}: {peak} cm⁻¹ ({mode})",
                    label=mode,
                    plotmode=map_mode,
                    coord_type=coord_type
                )

                if fig:
                    save_plot(
                        fig,
                        experiment_name,
                        f"{sample_name}_{mode}_map_{peak}"
                    )


        # -----------------------
        # RAW INTENSITY MAP
        # -----------------------
        print(f" => Generating intensity map for {sample_name}...")

        # ✅ filter df for this sample only
        df_subset = df[df["Sample"].isin(sample_labels)]
        coord_type = df_subset["CoordType"].iloc[0] if "CoordType" in df_subset.columns else "XY"

        map_data = build_intensity_map(df_subset)

        fig = plot_map(
            map_data,
            title=f"{sample_name}: Integrated Intensity",
            label="AUC",
            plotmode=map_mode,
            coord_type=coord_type
        )

        if fig:
            save_plot(
                fig,
                experiment_name,
                f"{sample_name}_intensity_map"
            )

# -----------------------
# SAVE DATA
# -----------------------
output_folder = Path("outputs") / experiment_name
output_folder.mkdir(parents=True, exist_ok=True)

# df_proc.to_csv(output_folder / f"{experiment_name}_processed.csv", index=False)
# df_peaks.to_csv(output_folder / f"{experiment_name}_peaks.csv", index=False)
# df_ratios.to_csv(output_folder / f"{experiment_name}_ratios.csv", index=False)

print(f"\n✅ All outputs saved to: {output_folder}")
