from scipy.optimize import curve_fit
import numpy as np
from .voigt import voigt

def fit_voigt_4peak(x, y):

    def model(x,
              a1, c1, s1, g1,
              a2, c2, s2, g2,
              a3, c3, s3, g3,
              a4, c4, s4, g4):

        return (
            voigt(x, a1, c1, s1, g1) +
            voigt(x, a2, c2, s2, g2) +
            voigt(x, a3, c3, s3, g3) +
            voigt(x, a4, c4, s4, g4)
        )

    # your constraints reused
    guess = [max(y), 650, 4, 3] * 4

    popt, _ = curve_fit(model, x, y, p0=guess, maxfev=20000)

    return popt