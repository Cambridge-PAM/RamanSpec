import numpy as np
import pandas as pd

from src.fitting.voigt import voigt


def spectra_data(df, offset_step=None, focus_range=None):
    """Long-format table of the spectra drawn by visualisation.spectra.plot."""
    frames = []
    for i, (sample, grp) in enumerate(df.groupby("Sample")):
        grp = grp.sort_values("RamanShift")
        if focus_range:
            grp = grp[
                (grp["RamanShift"] >= focus_range[0])
                & (grp["RamanShift"] <= focus_range[1])
            ]
        out = pd.DataFrame(
            {
                "Sample": sample,
                "RamanShift": grp["RamanShift"].values,
                "Intensity": grp["Intensity"].values,
            }
        )
        if offset_step is not None:
            out["PlottedIntensity"] = out["Intensity"] + i * offset_step
        frames.append(out)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def peak_fit_data(df, fit_params, peak_centers, bounds, sample_name):
    """Data, individual peaks, total fit and residuals for one fit plot."""
    grp = df[df["Sample"] == sample_name].sort_values("RamanShift")
    mask = (grp["RamanShift"] >= bounds[0]) & (grp["RamanShift"] <= bounds[1])
    x = grp["RamanShift"].values[mask.values]
    y = grp["Intensity"].values[mask.values]

    total_fit = np.zeros_like(x, dtype=float)
    for i in range(len(peak_centers)):
        total_fit += voigt(x, *fit_params[i * 4 : (i + 1) * 4])

    data = pd.DataFrame(
        {
            "Sample": sample_name,
            "RamanShift": x,
            "Intensity": y,
            "TotalFit": total_fit,
            "Residual": y - total_fit,
        }
    )

    x_dense = np.linspace(bounds[0], bounds[1], 1000)
    dense = pd.DataFrame({"Sample": sample_name, "RamanShift": x_dense})
    total_dense = np.zeros_like(x_dense)
    for i, peak in enumerate(peak_centers):
        y_peak = voigt(x_dense, *fit_params[i * 4 : (i + 1) * 4])
        dense[f"Peak_{peak:.0f}"] = y_peak
        total_dense += y_peak
    dense["TotalFit"] = total_dense

    # Measured points and the dense fit curves share one file, distinguished by Grid
    data["Grid"] = "data"
    dense["Grid"] = "fit_curve"
    return pd.concat([data, dense], ignore_index=True)


def peak_comparison_data(fit_outputs, ratio_pairs, tolerance):
    """Fitted peak shapes drawn by plot_peak_ratio_comparison."""
    peaks_to_plot = sorted({p for pair in ratio_pairs for p in pair})
    frames = []
    for peak_target in peaks_to_plot:
        for fit in fit_outputs:
            bounds = fit["bounds"]
            x_dense = np.linspace(bounds[0], bounds[1], 500)
            for i, p in enumerate(fit["peaks"]):
                if abs(p - peak_target) <= tolerance:
                    frames.append(
                        pd.DataFrame(
                            {
                                "Sample": fit["Sample"],
                                "TargetPeak": peak_target,
                                "RamanShift": x_dense,
                                "Intensity": voigt(
                                    x_dense, *fit["params"][i * 4 : (i + 1) * 4]
                                ),
                            }
                        )
                    )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def map_data_frame(map_data, coord_type, value_name):
    """Convert a map array (x[, y], value) into a labelled table."""
    if map_data is None or len(map_data) == 0:
        return pd.DataFrame()
    names = {
        "XY": ["X_um", "Y_um"],
        "RZ": ["R_um", "Z_um"],
        "Distance": ["Distance"],
    }[coord_type]
    return pd.DataFrame(np.asarray(map_data), columns=names + [value_name])
