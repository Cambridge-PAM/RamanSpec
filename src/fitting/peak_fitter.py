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

        x = grp["RamanShift"].values
        y = grp["Intensity"].values

        mask = (x >= bounds[0]) & (x <= bounds[1])
        x_fit = x[mask]
        y_fit = y[mask]

        if len(x_fit) < 10:
            continue

        model = build_voigt_model(len(peak_centers))

        guess = []
        lower = []
        upper = []

        for p in peak_centers:
            amp = max(y_fit)

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
                    "Peak": p,
                    "Center": c,
                    "Sigma": s,
                    "Gamma": g,
                    "Area": area
                })

            # ✅ ADD THIS BLOCK
            fit_outputs.append({
                "Sample": sample,
                "params": popt,
                "bounds": bounds,
                "peaks": peak_centers
            })

        except RuntimeError:
            continue

    return results, fit_outputs
