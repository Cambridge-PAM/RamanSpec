import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons, RadioButtons
from scipy.signal import find_peaks
from src.visualisation.style import build_style_map


def plot(
    df,
    offset_step=None,
    style_map=None,
    focus_range=None,
    detect_peaks=False,
    peak_prominence=None,
    peak_distance=5,
):

    fig, ax = plt.subplots(figsize=(10, 5))

    if style_map is None:
        style_map = build_style_map(df["Sample"].unique())

    for i, (sample, grp) in enumerate(df.groupby("Sample")):

        grp = grp.sort_values("RamanShift")

        x = grp["RamanShift"]
        y = grp["Intensity"]

        if focus_range:
            mask = (x >= focus_range[0]) & (x <= focus_range[1])
            x = x[mask]
            y = y[mask]

        style = style_map[sample]

        # ✅ apply offset
        if offset_step is not None:
            y = y + i * offset_step

        ax.plot(x, y, label=sample, color=style["color"], linestyle=style["linestyle"])

        if detect_peaks:
            import numpy as np

            y_values = np.asarray(y, dtype=float)
            if peak_prominence is None:
                prominence = 0.05 * (y_values.max() - y_values.min())
            else:
                prominence = peak_prominence

            peak_indices, _ = find_peaks(
                y_values,
                prominence=prominence,
                distance=peak_distance,
            )
            for peak_index in peak_indices:
                peak_x = x.iloc[peak_index]
                peak_y = y.iloc[peak_index]
                ax.plot(peak_x, peak_y, marker="o", markersize=3, color=style["color"])
                ax.annotate(
                    f"{peak_x:.0f}",
                    (peak_x, peak_y),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color=style["color"],
                )

    ax.set_xlabel("Raman shift (cm⁻¹)")
    ax.set_ylabel("Intensity")
    ax.legend()

    return fig, style_map


def plot_with_baseline(df, style_map=None, focus_range=None):

    fig, ax = plt.subplots(figsize=(10, 5))

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

        ax.plot(
            x,
            y,
            label=f"{sample} (corrected)",
            color=style["color"],
            linestyle=style["linestyle"],
        )

        if baseline is not None:
            ax.plot(
                x,
                baseline,
                alpha=0.4,
                color=style["color"],
                linestyle=style["linestyle"],
            )

    ax.legend()

    return fig, style_map
