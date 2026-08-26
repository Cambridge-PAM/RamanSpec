import numpy as np
import pandas as pd

from src.visualisation.mapping import build_ratio_map_from_df


def test_build_ratio_map_from_df_uses_positional_coordinates_not_spectrum_arrays():
    df_peaks = pd.DataFrame(
        [
            {"Sample": "A_X1.00_Y2.00", "Peak": 681.0, "PeakArea": 5.0},
            {"Sample": "A_X1.00_Y2.00", "Peak": 1720.0, "PeakArea": 10.0},
        ]
    )

    df_spectrum = pd.DataFrame(
        {
            "Sample": ["A_X1.00_Y2.00"] * 4,
            "RamanShift": [600.0, 650.0, 1700.0, 1750.0],
            "Intensity": [100.0, 200.0, 300.0, 400.0],
        }
    )

    map_data, coord_type = build_ratio_map_from_df(
        df_peaks,
        ratio_pair=(1720.0, 681.0),
        tolerance=2.0,
        df_spectrum=df_spectrum,
        intensity_threshold=100,
    )

    assert coord_type == "XY"
    assert map_data.shape == (1, 3)
    assert np.allclose(map_data[0, :2], [1.0, 2.0])
    assert np.isclose(map_data[0, 2], 2.0)
