from scipy.signal import savgol_filter

def smooth(df, window=7, poly=3):

    def apply(grp):
        grp = grp.sort_values("RamanShift")
        grp["Intensity"] = savgol_filter(
            grp["Intensity"], window, poly
        )
        return grp

    return df.groupby("Sample", group_keys=False).apply(apply)