import pandas as pd
import numpy as np

def compute_ratios(df_peaks, ratio_pairs, df_spectrum, intensity_threshold=100):
    """
    Compute ratios of peak areas for given peak pairs, ensuring the total spectral integrated intensity is above a threshold.

    Parameters:
        df_peaks (pd.DataFrame): DataFrame containing peak information.
        ratio_pairs (list of tuples): List of peak pairs for ratio calculation.
        df_spectrum (pd.DataFrame): DataFrame containing the full spectrum for each pixel.
        intensity_threshold (float): Minimum total spectral integrated intensity required to calculate the ratio.

    Returns:
        pd.DataFrame: DataFrame containing the calculated ratios.
    """

    results = []


    for sample, grp in df_peaks.groupby("Sample"):
        # Get the total integrated intensity for this sample
        for p1, p2 in ratio_pairs:
            # Extract peak areas
            peak1 = grp[grp["Peak"] == p1]
            peak2 = grp[grp["Peak"] == p2]

            if len(peak1) and len(peak2):
                area1 = peak1["PeakArea"].values[0]
                area2 = peak2["PeakArea"].values[0]

                # Check if the total spectral integrated intensity is above the threshold
                if not np.isfinite(area1) or not np.isfinite(area2) or area2 == 0:
                    ratio = 0.0
                else:
                    ratio = area1 / area2
                    if not np.isfinite(ratio) or abs(ratio) > 100:
                        ratio = 0.0
        
                results.append({
                    "Sample": sample,
                    "Peak1": p1,
                    "Peak2": p2,
                    "Ratio": float(np.nan_to_num(ratio, nan=0.0, posinf=0.0, neginf=0.0)),
                    "Area1": float(np.nan_to_num(area1, nan=0.0, posinf=0.0, neginf=0.0)),
                    "Area2": float(np.nan_to_num(area2, nan=0.0, posinf=0.0, neginf=0.0))
                })

    return pd.DataFrame(results)