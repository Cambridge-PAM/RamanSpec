import matplotlib.pyplot as plt
from src.visualisation.style import build_style_map




def plot(df, style_map = None, focus_range=None):

    fig, ax = plt.subplots(figsize=(10,5))

    if style_map is None:
        style_map = build_style_map(df["Sample"].unique())

    for sample, grp in df.groupby("Sample"):

        grp = grp.sort_values("RamanShift")

        x = grp["RamanShift"]
        y = grp["Intensity"]

        if focus_range:
            mask = (x >= focus_range[0]) & (x <= focus_range[1])
            x = x[mask]
            y = y[mask]
            
        style = style_map[sample]

        ax.plot(
            x,
            y,
            label=sample,
            color=style["color"],
            linestyle=style["linestyle"]
        )

    ax.set_xlabel("Raman shift (cm⁻¹)")
    ax.set_ylabel("Intensity")
    ax.legend()

    return fig, style_map


def plot_with_baseline(df, style_map=None, focus_range=None):
    
    fig, ax = plt.subplots(figsize=(10,5))
    
    if style_map is None:
        style_map = build_style_map(df["Sample"].unique())

    for sample, grp in df.groupby("Sample"):

        grp = grp.sort_values("RamanShift")

        x = grp["RamanShift"]
        y = grp["RawIntensity"]

        baseline = grp.get("Baseline")

        if focus_range:
            mask = (x >= focus_range[0]) & (x <= focus_range[1])
            x = x[mask]
            y = y[mask]
            if baseline is not None:
                baseline = baseline[mask]
                
        style = style_map[sample]

        ax.plot(x, y, label=f"{sample} (corrected)", color=style["color"], linestyle=style["linestyle"])

        if baseline is not None:
            ax.plot(x, baseline, alpha=0.4, color=style["color"], linestyle=style["linestyle"])

    ax.legend()

    return fig, style_map


