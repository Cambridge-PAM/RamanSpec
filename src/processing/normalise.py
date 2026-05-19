import numpy as np

def auc_normalise(df):

    def apply(grp):
        y = grp["Intensity"].values
        grp["Intensity"] = y / np.sum(y)
        return grp

    return df.groupby("Sample", group_keys=False).apply(apply)