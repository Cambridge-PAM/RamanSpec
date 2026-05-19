import pandas as pd

def compute_ratio(df, region1, region2):

    r1 = pd.DataFrame(integrate_region(df, region1))
    r2 = pd.DataFrame(integrate_region(df, region2))

    merged = r1.merge(r2, on="Sample", suffixes=("_1", "_2"))

    merged["Ratio"] = merged["Area_1"] / merged["Area_2"]

    return merged