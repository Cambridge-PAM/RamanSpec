
from pathlib import Path
import yaml

from src.io.loader import load_files
from src.processing.pipeline import Pipeline
from src.processing.baseline import psalsa_baseline
from src.processing.normalize import auc_normalise
from src.visualization.spectra import plot
from src.visualization.save import save_plot
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

        print(f"\n=== Processing: {run.name} ===")

        df = load_files(
            run,
            config["input"].get("indices"),
            config["input"].get("rename")
        )

        # pipeline
        pipe = Pipeline()

        if config["processing"]["baseline"]:
            pipe.add(psalsa_baseline)

        if config["processing"]["normalize"]:
            pipe.add(auc_normalise)

        df_proc = pipe.run(df)

        # plot
        fig = plot(df_proc, stacked=True)

        save_plot(fig, run.name, "processed_spectra")

        # ratios
        ratios = compute_ratio(
            df_proc,
            config["peaks"]["peak1"],
            config["peaks"]["peak2"]
        )

        ratios["Run"] = run.name
        results_all.append(ratios)
    
    results_all = pd.concat(results)
    fig_ratio = plot_ratios(df_all)
    save_plot(fig_ratio, "batch", "ratio_comparison")


    return results_all


if __name__ == "__main__":
    results = run_batch("config/config.yaml")

    import pandas as pd
    df = pd.concat(results)

    print("\n=== ALL RESULTS ===")
    print(df)


