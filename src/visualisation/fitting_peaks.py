import numpy as np
import matplotlib.pyplot as plt
from src.fitting.voigt import voigt

def plot_peak_fit(
    df,
    fit_params,
    peak_centers,
    bounds,
    sample_name
):
    """
    Plot:
    - Top: data + individual peaks + total fit
    - Bottom: residuals (data - fit)
    """

    grp = df[df["Sample"] == sample_name].copy()
    grp = grp.sort_values("RamanShift")

    x = grp["RamanShift"].values
    y = grp["Intensity"].values

    # Restrict to fitting window
    mask = (x >= bounds[0]) & (x <= bounds[1])
    x_fit = x[mask]
    y_fit = y[mask]

    if len(x_fit) == 0:
        return None

    # Smooth plotting axis
    x_dense = np.linspace(bounds[0], bounds[1], 1000)

    # -----------------------
    # FIGURE WITH 2 PANELS
    # -----------------------
    fig, (ax_top, ax_res) = plt.subplots(
        2, 1,
        figsize=(6,5),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]}
    )

    # -----------------------
    # TOP: DATA + FIT
    # -----------------------
    ax_top.plot(x_fit, y_fit, 'k.', alpha=0.5, label="Data")

    total_dense = np.zeros_like(x_dense)

    for i, peak in enumerate(peak_centers):
        a, c, s, g = fit_params[i*4:(i+1)*4]

        y_peak_dense = voigt(x_dense, a, c, s, g)
        total_dense += y_peak_dense

        ax_top.plot(
            x_dense,
            y_peak_dense,
            '--',
            label=f"{peak:.0f} cm⁻¹"
        )

    # Total fit
    ax_top.plot(x_dense, total_dense, 'r-', label="Total Fit")

    ax_top.axvspan(bounds[0], bounds[1], color='grey', alpha=0.1)

    ax_top.set_ylabel("Intensity")
    ax_top.set_title(f"{sample_name} | {bounds[0]}–{bounds[1]} cm⁻¹")

    ax_top.legend(fontsize=8)

    # -----------------------
    # BOTTOM: RESIDUALS
    # -----------------------
    # Evaluate model on original x_fit
    total_fit = np.zeros_like(x_fit)

    for i in range(len(peak_centers)):
        a, c, s, g = fit_params[i*4:(i+1)*4]
        total_fit += voigt(x_fit, a, c, s, g)

    residuals = y_fit - total_fit

    ax_res.plot(x_fit, residuals, 'k-', linewidth=1)
    ax_res.axhline(0, color='red', linestyle='--')

    ax_res.set_ylabel("Residual")
    ax_res.set_xlabel("Raman shift (cm⁻¹)")

    # Optional: tighten residual limits
    ax_res.set_ylim(
        -1.2 * np.max(np.abs(residuals)),
         1.2 * np.max(np.abs(residuals))
    )

    # -----------------------
    # FINAL FORMAT
    # -----------------------
    plt.tight_layout()

    return fig