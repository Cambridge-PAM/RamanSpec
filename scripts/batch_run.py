
from pathlib import Path
import yaml

from src.io.loader import load_files
from src.processing.pipeline import Pipeline
from src.processing.baseline import psalsa_baseline
from src.processing.normalise import auc_normalise
from src.visualisation.spectra import plot_spectra
from src.visualisation.save import save_plot
from src.visualisation.peaks import plot_peak_comparison
from src.visualisation.ratios import plot_ratios
from src.analysis.ratios import compute_ratio

import pandas as pd

def run_batch(config_path):

    with open(config_path) as f:
        config = yaml.safe_load(f)

    base_folder = Path(config["input"]["folder"])

    all_runs = list(base_folder.iterdir())

    results_all = []

    for run in all_runs:
    
        if not run.is_dir():
            continue

        experiment_name = run.name

        print(f"\n=== Processing: {experiment_name} ===")

        df = load_files(run)

        # ---------------------
        # RAW PLOT
        # ---------------------
        fig_raw = plot_spectra(df)
        save_plot(fig_raw, experiment_name, "raw")

        # ---------------------
        # PROCESS
        # ---------------------
        df_proc = pipe.run(df)

        fig_proc = plot_spectra(df_proc)
        save_plot(fig_proc, experiment_name, "processed")

        # ---------------------
        # PEAK COMPARISON
        # ---------------------
        fig_peaks = plot_peak_comparison(
            df_proc,
            config["peaks"]["ranges"]["range1"]["bounds"],
            config["peaks"]["ranges"]["range2"]["bounds"]
        )

        save_plot(fig_peaks, experiment_name, "peak_comparison")
    
    
    df_all = pd.concat(results_all)

    fig_ratio = plot_ratios(df_all)

    save_plot(fig_ratio, "ALL_EXPERIMENTS", "ratios")

    return results_all


if __name__ == "__main__":
    results = run_batch("config/config.yaml")

    import pandas as pd
    df = pd.concat(results)

    print("\n=== ALL RESULTS ===")
    print(df)


