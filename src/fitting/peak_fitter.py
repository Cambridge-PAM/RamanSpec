import numpy as np
from scipy.optimize import curve_fit
from .voigt import voigt

def build_voigt_model(n_peaks):

    def model(x, *params):
        result = np.zeros_like(x)

        for i in range(n_peaks):
            a, c, s, g = params[i*4:(i+1)*4]
            result += voigt(x, a, c, s, g)

        return result

    return model

def fit_peak_range(df, bounds, peak_centers, tolerance):
    
    results = []
    fit_outputs = []

    for sample, grp in df.groupby("Sample"):        

        grp = grp.sort_values("RamanShift")

        x = np.asarray(grp["RamanShift"], dtype=float)
        y = np.asarray(grp["Intensity"], dtype=float)

        finite_mask = np.isfinite(x) & np.isfinite(y)
        x = x[finite_mask]
        y = y[finite_mask]

        if len(x) == 0:
            for p in peak_centers:
                results.append({
                    "Sample": sample,
                    "Amplitude": 0.0,
                    "Peak": p,
                    "Center": 0.0,
                    "Sigma": 0.0,
                    "Gamma": 0.0,
                    "PeakArea": 0.0
                })
            continue

        mask = (x >= bounds[0]) & (x <= bounds[1])
        x_fit = x[mask]
        y_fit = np.nan_to_num(y[mask], nan=0.0, posinf=0.0, neginf=0.0)

        if len(x_fit) < 10 or not np.all(np.isfinite(y_fit)):
            for p in peak_centers:
                results.append({
                    "Sample": sample,
                    "Amplitude": 0.0,
                    "Peak": p,
                    "Center": 0.0,
                    "Sigma": 0.0,
                    "Gamma": 0.0,
                    "PeakArea": 0.0
                })
            continue

        model = build_voigt_model(len(peak_centers))

        guess = []
        lower = []
        upper = []

        for p in peak_centers:
            amp = max(y_fit) if np.max(y_fit) > 0 else 0.0

            guess += [amp, p, 4, 3]
            lower += [0, p - tolerance, 1, 0.5]
            upper += [np.inf, p + tolerance, 20, 15]

        try:
            
            popt, _ = curve_fit(
                model,
                x_fit,
                y_fit,
                p0=guess,
                bounds=(lower, upper),
                maxfev=30000
            )

            for i, p in enumerate(peak_centers):

                a, c, s, g = popt[i*4:(i+1)*4]

                x_dense = np.linspace(bounds[0], bounds[1], 500)
                y_peak = voigt(x_dense, a, c, s, g)

                area = np.trapz(y_peak, x_dense)

                results.append({
                    "Sample": sample,
                    "Amplitude": a,
                    "Peak": p,
                    "Center": c,
                    "Sigma": s,
                    "Gamma": g,
                    "PeakArea": float(np.nan_to_num(area, nan=0.0, posinf=0.0, neginf=0.0))
                })

            fit_outputs.append({
                "Sample": sample,
                "params": popt,
                "bounds": bounds,
                "peaks": peak_centers
            })

        except (RuntimeError, ValueError):
            for p in peak_centers:
                results.append({
                    "Sample": sample,
                    "Amplitude": 0.0,
                    "Peak": p,
                    "Center": 0.0,
                    "Sigma": 0.0,
                    "Gamma": 0.0,
                    "PeakArea": 0.0
                })
            continue

    return results, fit_outputs
