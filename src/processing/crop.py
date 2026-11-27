import numpy as np
import pandas as pd

from src.visualisation.mapping import get_base_sample_name


def crop_map_edges(df, pixels=1):
    """
    Remove the outer `pixels` rows/columns of a positional map (grid) for each
    base sample in `df`, based on unique X/Y (or R/Z) coordinate values.
    """
    if pixels <= 0:
        return df

    coord_cols = None
    for c1, c2 in (("X_um", "Y_um"), ("R_um", "Z_um")):
        if c1 in df.columns and c2 in df.columns:
            coord_cols = (c1, c2)
            break

    if coord_cols is None:
        return df

    c1, c2 = coord_cols
    base_samples = df["Sample"].map(get_base_sample_name)

    kept_groups = []
    for base in base_samples.unique():
        grp = df[base_samples == base]
        unique_c1 = np.sort(grp[c1].unique())
        unique_c2 = np.sort(grp[c2].unique())

        if len(unique_c1) <= 2 * pixels or len(unique_c2) <= 2 * pixels:
            print(
                f"⚠️  Skipping edge crop for {base}: map too small to crop {pixels} pixel(s) per side."
            )
            kept_groups.append(grp)
            continue

        keep_c1 = unique_c1[pixels : len(unique_c1) - pixels]
        keep_c2 = unique_c2[pixels : len(unique_c2) - pixels]

        kept_groups.append(grp[grp[c1].isin(keep_c1) & grp[c2].isin(keep_c2)])

    return pd.concat(kept_groups, ignore_index=True)
