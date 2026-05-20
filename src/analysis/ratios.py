import pandas as pd
from .integration import integrate_region

def compute_ratios(df_peaks, ratio_pairs):
    
    import pandas as pd

    results = []

    for sample, grp in df_peaks.groupby("Sample"):

        for p1, p2 in ratio_pairs:

            area1 = grp[grp["Peak"] == p1]["Area"]
            area2 = grp[grp["Peak"] == p2]["Area"]

            if len(area1) and len(area2):

                ratio = area1.values[0] / area2.values[0]

                results.append({
                    "Sample": sample,
                    "Peak1": p1,
                    "Peak2": p2,
                    "Ratio": ratio
                })

    return pd.DataFrame(results)
