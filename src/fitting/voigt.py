import numpy as np
from scipy.special import wofz

def voigt(x, amp, cen, sigma, gamma):
    z = ((x - cen) + 1j*gamma) / (sigma*np.sqrt(2))
    return amp * np.real(wofz(z)) / (sigma*np.sqrt(2*np.pi))