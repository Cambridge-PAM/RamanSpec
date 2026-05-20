import numpy as np
import matplotlib.pyplot as plt
from src.fitting.voigt import voigt
from src.visualisation.style import build_style_map


def plot_peak_ratio_comparison(fit_outputs, ratio_pairs, tolerance, style_map = None):
    """
    Plot fitted peak shapes for ratio peaks across all samples.

    Parameters:
        fit_outputs: list of dicts from fitting step
        ratio_pairs: list of [peak1, peak2]
    """

    # -----------------------
    # Extract ALL peaks used in ratios
    # -----------------------
    peaks_to_plot = set()
    for p1, p2 in ratio_pairs:
        peaks_to_plot.add(p1)
        peaks_to_plot.add(p2)

    peaks_to_plot = sorted(list(peaks_to_plot))

    # -----------------------
    # Get all samples
    # -----------------------
    samples = [f["Sample"] for f in fit_outputs]
    if style_map is None:
        style_map = build_style_map(set(samples))

    # -----------------------
    # Create subplots
    # -----------------------
    n_peaks = len(peaks_to_plot)
    fig, axes = plt.subplots(1, n_peaks, figsize=(5*n_peaks, 4), sharey=True)

    if n_peaks == 1:
        axes = [axes]

    # -----------------------
    # LOOP OVER PEAKS
    # -----------------------
    for ax, peak_target in zip(axes, peaks_to_plot):

        for fit in fit_outputs:

            sample = fit["Sample"]
            params = fit["params"]
            peak_centers = fit["peaks"]
            bounds = fit["bounds"]

            # Create dense x
            x_dense = np.linspace(bounds[0], bounds[1], 500)

            # Find this peak in model
            for i, p in enumerate(peak_centers):
                if abs(p - peak_target) <= tolerance:
                    

                    a, c, s, g = params[i*4:(i+1)*4]

                    y_peak = voigt(x_dense, a, c, s, g)

                    # Normalise for comparison
                    # y_peak = y_peak / np.max(y_peak)
                    
                    style = style_map[sample]

                    ax.plot(
                        x_dense,
                        y_peak,
                        color=style["color"],
                        linestyle=style["linestyle"],
                        label=sample
                    )

        ax.set_title(f"{peak_target} cm⁻¹")
        ax.set_xlabel("Raman shift")

    axes[0].set_ylabel("Normalised Intensity")

    # -----------------------
    # GLOBAL LEGEND
    # -----------------------
    handles, labels = axes[0].get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc="upper right")

    plt.tight_layout()

    return fig, style_map
