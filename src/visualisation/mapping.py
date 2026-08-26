import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from src.fitting.voigt import voigt


# -------------------------------------------------
# UTILITY: Extract coordinates (XY or RZ)
# -------------------------------------------------
def parse_coordinates(sample_name):
    """
    Supports:
    - XY → _X..._Y...
    - RZ → _R..._Z...
    Returns: (x, y, coord_type)
    """

    try:
        if "_X" in sample_name and "_Y" in sample_name:
            x = float(sample_name.split("_X")[1].split("_")[0])
            y = float(sample_name.split("_Y")[1])
            return x, y, "XY"

        elif "_R" in sample_name and "_Z" in sample_name:
            r = float(sample_name.split("_R")[1].split("_")[0])
            z = float(sample_name.split("_Z")[1])
            return r, z, "RZ"

    except:
        pass

    return None, None, None


def get_base_sample_name(name):
    if "_X" in name:
        return name.split("_X")[0]
    elif "_R" in name:
        return name.split("_R")[0]
    return name



# -------------------------------------------------
# Map Builders
# -------------------------------------------------
def build_peak_param_map_from_df(df_peaks, peak, tolerance, mode):
    """
    Build a peak parameter map from the DataFrame of peaks.
    Handles both 2D positional data (X, Y or R, Z) and 1D distance data.
    """
    records = []

    for sample, grp in df_peaks.groupby("Sample"):
        if "Distance" in grp.columns:
            x = grp["Distance"].iloc[0]
            y = None  # No y-coordinate for Distance
            coord_type = "Distance"
        else:
            x, y, coord_type = parse_coordinates(sample)
            if x is None:
                continue

        grp = grp.copy()
        grp["diff"] = abs(grp["Peak"] - peak)

        closest = grp.loc[grp["diff"].idxmin()]

        if closest["diff"] > tolerance:
            val = np.nan
        else:
            val = closest.get(mode, np.nan)

        records.append([x, y, val] if coord_type != "Distance" else [x, val])

    return np.array(records), coord_type


def build_ratio_map_from_df(df_peaks, ratio_pair, tolerance, df_spectrum, intensity_threshold=100):
    """
    Build a ratio map from the DataFrame of peaks, ensuring the total spectral integrated intensity is above a threshold.

    Parameters:
        df_peaks (pd.DataFrame): DataFrame containing peak information.
        ratio_pair (tuple): Pair of peaks for ratio calculation.
        tolerance (float): Tolerance for peak matching.
        df_spectrum (pd.DataFrame): DataFrame containing the full spectrum for each pixel.
        intensity_threshold (float): Minimum total spectral integrated intensity required to calculate the ratio.

    Returns:
        np.array: Array of ratio map data.
        str: Coordinate type (e.g., "Distance", "XY").
    """
    p1, p2 = ratio_pair
    records = []

    for sample, grp in df_peaks.groupby("Sample"):
        # Extract positional coordinates
        if "Distance" in grp.columns:
            x_pos = grp["Distance"].iloc[0]
            y_pos = None
            coord_type = "Distance"
        else:
            x_pos, y_pos, coord_type = parse_coordinates(sample)
            if x_pos is None:
                continue

        # Calculate total spectral integrated intensity for this sample
        spectrum_grp = df_spectrum[df_spectrum["Sample"] == sample]
        if spectrum_grp.empty:
            continue

        spectrum_x = spectrum_grp["RamanShift"].values
        spectrum_y = spectrum_grp["Intensity"].values
        order = np.argsort(spectrum_x)
        spectrum_x = spectrum_x[order]
        spectrum_y = spectrum_y[order]
        total_intensity = np.trapz(spectrum_y, spectrum_x)

        # Skip if total intensity is below the threshold
        if total_intensity < intensity_threshold:
            records.append([x_pos, y_pos, 0] if coord_type != "Distance" else [x_pos, 0])
            continue

        # Match peaks and calculate ratio
        grp = grp.copy()
        grp["diff1"] = abs(grp["Peak"] - p1)
        grp["diff2"] = abs(grp["Peak"] - p2)
        peak1 = grp.loc[grp["diff1"].idxmin()]
        peak2 = grp.loc[grp["diff2"].idxmin()]

        if peak1["diff1"] > tolerance or peak2["diff2"] > tolerance:
            val = 0.0
        elif not np.isfinite(peak1["PeakArea"]) or not np.isfinite(peak2["PeakArea"]) or peak2["PeakArea"] == 0:
            val = 0.0
        else:
            val = peak1["PeakArea"] / peak2["PeakArea"]
            if not np.isfinite(val) or abs(val) > 100:
                val = 0.0
            else:
                val = float(np.nan_to_num(val, nan=0.0, posinf=0.0, neginf=0.0))

        records.append([x_pos, y_pos, val] if coord_type != "Distance" else [x_pos, val])

    if len(records) == 0:
        return np.array([]), coord_type

    return np.array(records), coord_type


# -------------------------------------------------
# PLOT SCATTER MAP (BASE)
# -------------------------------------------------

def plot_map(
    map_data,
    title,
    label="Value",
    cmap="viridis",
    plotmode="pixel",
    coord_type="XY",
    vmin=None,
    vmax=None,
    depth_direction="positive" 
):
    if map_data is None or len(map_data) == 0:
        print(title, " : ⚠️ No positional data available")
        return None

    x = map_data[:, 0]
    z = map_data[:, -1]  # Intensity or value to plot

    # Handle 2D positional data
    y = map_data[:, 1] if coord_type != "Distance" else None

    # -----------------------
    # REMOVE NaNs
    # -----------------------
    valid = ~np.isnan(z)
    x, z = x[valid], z[valid]
    if y is not None:
        y = y[valid]
    if len(z) == 0:
        print(title, " : ⚠️ No valid values to plot")
        return None

    # -----------------------
    # SORT BY DISTANCE (if applicable)
    # -----------------------
    if coord_type == "Distance":
        sorted_indices = np.argsort(x)
        x = x[sorted_indices]
        z = z[sorted_indices]
        
    if vmin == None:
        vmin = np.nanmin(z)
    if vmax == None:
        vmax = np.nanmax(z)

    fig = plt.figure(figsize=(8, 6))
    
     # =====================================================
    # ✅ MODE 0: 2D LINE PLOT (Distance)
    # =====================================================
    if coord_type == "Distance":
        ax = fig.add_subplot(111)
        scatter = ax.scatter(x, z, c=z, cmap=cmap, vmin=vmin, vmax=vmax)
        plt.colorbar(scatter, ax=ax, label=label)
        ax.set_xlabel("Distance (µm)")
        ax.set_ylabel(label)
        
    # =====================================================
    # ✅ MODE: DEPTH PLOT
    # =====================================================
    elif plotmode == "depth":
        if coord_type != "RZ":
            raise ValueError("Depth plots require RZ coordinate data.")

        ax = fig.add_subplot(111)

        # Adjust depth direction
        if depth_direction == "negative":
            y = -y

        # Create scatter plot
        scatter = ax.scatter(
            z, y, c=x, cmap=cmap, s=100, edgecolors='k', linewidth=0.4
        )

        ax.set_xlabel(label)
        ax.set_ylabel("Depth (Z µm)")
        ax.set_title(title)
        ax.set_xlim([vmin, vmax])

        # Add legend for unique R-coordinates
        unique_r = np.unique(x)
        for r in unique_r:
            mask = x == r
            ax.scatter(
                z[mask], y[mask], label=f"R = {r:.2f} µm", s=100, edgecolors='k'
            )
        
    # =====================================================
    # ✅ MODE 1: PIXEL GRID (default, best for Raman maps)
    # =====================================================
    elif plotmode == "pixel":
        ax = fig.add_subplot(111)
        x_unique = np.sort(np.unique(x))
        y_unique = np.sort(np.unique(y))
        nx = len(x_unique)
        ny = len(y_unique)
        Z = np.full((ny, nx), np.nan)
        for xi, yi, zi in zip(x, y, z):
            ix = np.where(x_unique == xi)[0][0]
            iy = np.where(y_unique == yi)[0][0]
            Z[iy, ix] = zi
        im = ax.imshow(
            Z,
            extent=(x_unique.min(), x_unique.max(),
                    y_unique.min(), y_unique.max()),
            origin='lower',
            cmap=cmap,
            aspect='equal',
            vmin=vmin,
            vmax=vmax
        )
        plt.colorbar(im, ax=ax, label=label)

    # =====================================================
    # ✅ MODE 2: SCATTER ONLY
    # =====================================================
    elif plotmode == "scatter":
        ax = fig.add_subplot(111)
        sc = ax.scatter(
            x, y,
            c=z,
            cmap=cmap,
            s=80,
            edgecolors='k',
            linewidth=0.4,
            vmin=vmin,
            vmax=vmax
        )
        plt.colorbar(sc, ax=ax, label=label)

    # =====================================================
    # ✅ MODE 3: INTERPOLATED HEATMAP
    # =====================================================
    elif plotmode == "interp":
        if len(x) < 4:
            print("⚠️ Not enough points for interpolation")
            return None
        ax = fig.add_subplot(111)
        xi = np.linspace(min(x), max(x), 150)
        yi = np.linspace(min(y), max(y), 150)
        XI, YI = np.meshgrid(xi, yi)
        ZI = griddata((x, y), z, (XI, YI), method='cubic')
        im = ax.imshow(
            ZI,
            extent=(min(x), max(x), min(y), max(y)),
            origin='lower',
            cmap=cmap,
            aspect='auto',
            vmin=vmin,
            vmax=vmax
        )
        plt.colorbar(im, ax=ax, label=label)

    # =====================================================
    # ✅ MODE 4: 3D PLOT
    # =====================================================
    elif plotmode == "3d":
        ax = fig.add_subplot(111, projection='3d')
        sc = ax.scatter(
            x, y, z,
            c=z,
            cmap=cmap,
            s=50,
            edgecolors='k',
            linewidth=0.4,
            vmin=vmin,
            vmax=vmax
        )
        ax.set_xlabel("X (µm)" if coord_type == "XY" else "R (µm)")
        ax.set_ylabel("Y (µm)" if coord_type == "XY" else "Z (µm)")
        ax.set_zlabel(label)
        fig.colorbar(sc, ax=ax, label=label)

    # =====================================================
    # ✅ MODE 5: SLICE PLOT
    # =====================================================
    elif plotmode == "slice":
        ax = fig.add_subplot(111)
        if coord_type == "XY":
            ax.plot(x, z, 'o-', label="Y-Axis Slice")
            ax.set_xlabel("X (µm)")
            ax.set_ylabel(label)
        elif coord_type == "RZ":
            ax.plot(y, z, 'o-', label="Z-Axis Slice")
            ax.set_xlabel("R (µm)")
            ax.set_ylabel(label)
        ax.legend()

    else:
        raise ValueError(f"Unknown plotting mode: {plotmode}")

    # -----------------------
    # AXES
    # -----------------------
    if plotmode != "3d":
        if coord_type != "Distance":
            if coord_type == "XY":
                ax.set_xlabel("X (µm)")
                ax.set_ylabel("Y (µm)")
                ax.invert_yaxis()
            elif coord_type == "RZ":
                if plotmode != "depth":
                    ax.set_xlabel("R (µm)")
                    ax.set_ylabel("Z (µm)")
                    ax.invert_yaxis()

    ax.set_title(title)
    plt.tight_layout()
    return fig



# -------------------------------------------------
# PEAK RATIO MAP
# -------------------------------------------------
def build_ratio_map(fit_outputs, ratio_pair, tolerance, intensity_threshold=100):
    """
    Build a ratio map from the fitted outputs, ensuring the total spectral integrated intensity is above a threshold.

    Parameters:
        fit_outputs (list): List of fitted outputs containing peak parameters.
        ratio_pair (tuple): Pair of peaks for ratio calculation.
        tolerance (float): Tolerance for peak matching.
        intensity_threshold (float): Minimum total spectral integrated intensity required to calculate the ratio.

    Returns:
        np.array: Array of ratio map data.
        str: Coordinate type (e.g., "Distance", "XY").
    """
    p1, p2 = ratio_pair
    records = []

    for fit in fit_outputs:
        sample = fit["Sample"]

        # Extract positional coordinates
        x_pos, y_pos, coord_type = parse_coordinates(sample)
        if x_pos is None:
            continue

        params = fit["params"]
        peaks = fit["peaks"]

        # Calculate total spectral integrated intensity
        total_intensity = np.trapz(fit["Intensity"], fit["RamanShift"])

        # Skip if total intensity is below the threshold
        if total_intensity < intensity_threshold:
            records.append([x_pos, y_pos, np.nan])
            continue

        # Get peak areas
        def get_peakarea(target):
            idx = np.argmin([abs(p - target) for p in peaks])
            a, c, s, g = params[idx * 4:(idx + 1) * 4]
            x_local = np.linspace(c - 10, c + 10, 200)
            y_local = voigt(x_local, a, c, s, g)
            return np.trapz(y_local, x_local)

        peakarea1 = get_peakarea(p1)
        peakarea2 = get_peakarea(p2)

        # Calculate ratio if both peak areas are valid
        if peakarea2 == 0 or not np.isfinite(peakarea1) or not np.isfinite(peakarea2):
            ratio = 0.0
        else:
            ratio = peakarea1 / peakarea2
            if not np.isfinite(ratio) or abs(ratio) > 100:
                ratio = 0.0
            else:
                ratio = float(np.nan_to_num(ratio, nan=0.0, posinf=0.0, neginf=0.0))

        records.append([x_pos, y_pos, ratio])

    if len(records) == 0:
        return np.array([]), coord_type

    return np.array(records), coord_type


def build_intensity_map(dfsubset):
    """
    Build integrated intensity map data for plotting using np.trapz.
    Handles both 2D positional data (X, Y or R, Z) and 1D distance data.
    """
    records = []

    for sample, grp in dfsubset.groupby("Sample"):
        # Parse positional coordinates
        if "Distance" in grp.columns:
            x_pos = grp["Distance"].iloc[0]
            y_pos = None  # No y-coordinate for Distance
            coord_type = "Distance"
        elif "X_um" in grp.columns and "Y_um" in grp.columns:
            x_pos = grp["X_um"].iloc[0]
            y_pos = grp["Y_um"].iloc[0]
            coord_type = "XY"
        elif "R_um" in grp.columns and "Z_um" in grp.columns:
            x_pos = grp["R_um"].iloc[0]
            y_pos = grp["Z_um"].iloc[0]
            coord_type = "RZ"
        else:
            continue

        # Extract Raman shift (x) and intensity (y)
        x = grp["RamanShift"].values
        y = grp["Intensity"].values

        # ✅ SORT BY X (critical for integration)
        order = np.argsort(x)
        x = x[order]
        y = y[order]

        # Calculate integrated intensity using trapezoidal rule
        total_intensity = np.trapz(y, x)

        # Append results
        if coord_type == "Distance":
            records.append([x_pos, total_intensity])
        else:
            records.append([x_pos, y_pos, total_intensity])

    # Convert records to numpy array and return
    map_data = np.array(records)
    return map_data, coord_type
