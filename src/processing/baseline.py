import pybaselines as pbl

def psalsa_baseline(df, lam=1e6, p=0.01, return_baseline=False):
    baselineFitter = pbl.Baseline()
    baselines = {}

    def apply(grp):
        y = grp["Intensity"].values

        # Use the provided lam and p values
        baseline, _ = baselineFitter.psalsa(y, lam=lam, p=p)

        grp = grp.copy()

        grp["RawIntensity"] = y
        grp["Baseline"] = baseline  # ✅ store baseline

        y_corr = y - baseline
        y_corr[y_corr < 0] = 0

        grp["Intensity"] = y_corr

        return grp

    df_out = df.groupby("Sample", group_keys=False).apply(apply)

    return df_out
