import matplotlib.pyplot as plt
import pandas as pd

from src.visualisation.spectra import plot


def test_plot_skips_peak_detection_when_focus_range_is_empty():
    df = pd.DataFrame(
        {
            "Sample": ["sample", "sample"],
            "RamanShift": [100.0, 200.0],
            "Intensity": [1.0, 2.0],
        }
    )

    fig, _ = plot(df, focus_range=(300.0, 400.0), detect_peaks=True)

    plt.close(fig)
