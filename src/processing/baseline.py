import pybaselines as pbl

def psalsa_baseline(df):

    baselineFitter = pbl.Baseline()

    def apply(grp):
        y = grp["Intensity"].values
        baseline, _ = baselineFitter.psalsa(y, lam=1e6, p=0.01)

        y_corr = y - baseline
        y_corr[y_corr < 0] = 0

        grp["Intensity"] = y_corr
        return grp

    return df.groupby("Sample", group_keys=False).apply(apply)