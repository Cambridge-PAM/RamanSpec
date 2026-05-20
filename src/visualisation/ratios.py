import matplotlib.pyplot as plt
import numpy as np
from src.visualisation.style import build_style_map
from src.visualisation.style import parse_sample_name


def plot_ratios(df, style_map=None):

    fig, ax = plt.subplots(figsize=(10,5))
    
    if style_map is None:
        style_map = build_style_map(df["Sample"].unique())

    # -----------------------
    # Parse sample structure
    # -----------------------
    df = df.copy()

    df["Prefix"], df["Index"] = zip(*df["Sample"].map(parse_sample_name))

    prefixes = sorted(df["Prefix"].unique())
    indices = sorted(df["Index"].unique())

    n_groups = len(indices)
    n_prefix = len(prefixes)

    # -----------------------
    # Bar positioning
    # -----------------------
    bar_width = 0.8 / n_prefix
    x = np.arange(n_groups)

    # -----------------------
    # Plot bars
    # -----------------------
    for i, prefix in enumerate(prefixes):

        subset = df[df["Prefix"] == prefix]

        values = []
        colors = []

        for idx in indices:

            row = subset[subset["Index"] == idx]

            if not row.empty:
                values.append(row["Ratio"].values[0])
                sample_name = row["Sample"].values[0]
                colors.append(style_map[sample_name]["color"])
            else:
                values.append(np.nan)
                colors.append("grey")

        xpos = x + i * bar_width

        ax.bar(
            xpos,
            values,
            width=bar_width,
            label=prefix,
            color=colors,
            edgecolor='black'
        )

    # -----------------------
    # Formatting
    # -----------------------
    ax.set_xticks(x + bar_width * (n_prefix - 1) / 2)
    ax.set_xticklabels([str(i) for i in indices])

    ax.set_xlabel("Position Index")
    ax.set_ylabel("Peak Ratio")

    ax.legend(title="Sample Type")

    return fig, style_map