import pybaselines as pbl
import numpy as np
import pandas as pd


def psalsa_baseline(df, lam=1e6, p=0.01, return_baseline=False):
    baselineFitter = pbl.Baseline()
    baselines = {}

    def apply(grp):
        sample = grp.name
        y = grp["Intensity"].values

        # Use the provided lam and p values
        # baseline, _ = baselineFitter.psalsa(y, lam=lam, p=p)
        baseline, _ = baselineFitter.airpls(y, lam=lam)
        baseline, _ = baselineFitter.arpls(y, lam=lam)

        grp = grp.copy()

        grp["RawIntensity"] = y
        grp["Baseline"] = baseline  # ✅ store baseline

        y_corr = y - baseline
        y_corr[y_corr < 0] = 0

        grp["Intensity"] = y_corr

        return grp

    # Explicit loop (not groupby.apply) so the Sample column is kept without a FutureWarning
    parts = []
    for name, grp in df.groupby("Sample"):
        grp = grp.copy()
        grp.name = name
        parts.append(apply(grp))

    return pd.concat(parts) if parts else df
