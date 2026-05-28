import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from src.fitting.voigt import voigt

# -------------------------------------------------
# UTILITY: Extract XY from sample name
# -------------------------------------------------
def parse_xy(sample_name):
    try:
        x = float(sample_name.split("_X")[1].split("_")[0])
        y = float(sample_name.split("_Y")[1])
        return x, y
    except:
        return None, None


def get_base_sample_name(name):
    return name.split("_X")[0]


# -------------------------------------------------
# Map Builders
# -------------------------------------------------
def build_peak_param_map_from_df(df_peaks, peak, tolerance, mode):
    
    records = []

    for sample, grp in df_peaks.groupby("Sample"):

        x, y = parse_xy(sample)
        if x is None:
            continue

        grp = grp.copy()
        grp["diff"] = abs(grp["Peak"] - peak)

        closest = grp.loc[grp["diff"].idxmin()]

        if closest["diff"] > tolerance:
            val = np.nan
        else:
            val = closest.get(mode, np.nan)

        records.append([x, y, val])

    return np.array(records)


def build_ratio_map_from_df(df_peaks, ratio_pair, tolerance):
    
    p1, p2 = ratio_pair
    records = []

    for sample, grp in df_peaks.groupby("Sample"):

        x, y = parse_xy(sample)
        if x is None:
            continue

        grp = grp.copy()
        grp["diff1"] = abs(grp["Peak"] - p1)
        grp["diff2"] = abs(grp["Peak"] - p2)

        peak1 = grp.loc[grp["diff1"].idxmin()]
        peak2 = grp.loc[grp["diff2"].idxmin()]

        if peak1["diff1"] > tolerance or peak2["diff2"] > tolerance:
            val = np.nan
        elif peak2["PeakArea"] == 0:
            val = np.nan
        else:
            val = peak1["PeakArea"] / peak2["PeakArea"]

        records.append([x, y, val])

    return np.array(records)


# -------------------------------------------------
# PLOT SCATTER MAP (BASE)
# -------------------------------------------------

def plot_map(
    map_data,
    title,
    label="Value",
    cmap="viridis",
    plotmode="pixel",
    coord_type="XY"
):

    if map_data is None or len(map_data) == 0:
        print(title, " : ⚠️ No positional data available")
        return None

    x = map_data[:,0]
    y = map_data[:,1]
    z = map_data[:,2]

    # -----------------------
    # REMOVE NaNs
    # -----------------------
    valid = ~np.isnan(z)
    x, y, z = x[valid], y[valid], z[valid]

    if len(z) == 0:
        print(title, " : ⚠️ No valid values to plot")
        return None

    fig, ax = plt.subplots(figsize=(6,5))

    # Shared colour limits (important for consistency)
    vmin = np.nanmin(z)
    vmax = np.nanmax(z)

    # =====================================================
    # ✅ MODE 1: PIXEL GRID (default, best for Raman maps)
    # =====================================================
    if plotmode == "pixel":

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
    # ✅ MODE 4: HYBRID (interp + points overlay)
    # =====================================================
    elif plotmode == "hybrid":

        if len(x) > 3:
            xi = np.linspace(min(x), max(x), 150)
            yi = np.linspace(min(y), max(y), 150)

            XI, YI = np.meshgrid(xi, yi)

            ZI = griddata((x, y), z, (XI, YI), method='cubic')

            ax.imshow(
                ZI,
                extent=(min(x), max(x), min(y), max(y)),
                origin='lower',
                cmap=cmap,
                aspect='auto',
                alpha=0.6,
                vmin=vmin,
                vmax=vmax
            )

        sc = ax.scatter(
            x, y,
            c=z,
            cmap=cmap,
            s=60,
            edgecolors='k',
            linewidth=0.3,
            vmin=vmin,
            vmax=vmax
        )

        plt.colorbar(sc, ax=ax, label=label)

    else:
        raise ValueError(f"Unknown plotting mode: {plotmode}")

    # -----------------------
    # AXES
    # -----------------------
    
    if coord_type == "XY":
        ax.set_xlabel("X (µm)")
        ax.set_ylabel("Y (µm)")
    elif coord_type == "RZ":
        ax.set_xlabel("R (µm)")
        ax.set_ylabel("Z (µm)")
        ax.invert_yaxis()
        
    ax.set_title(title)
    ax.set_aspect('equal')

    plt.tight_layout()

    return fig



# -------------------------------------------------
# PEAK RATIO MAP
# -------------------------------------------------
def build_ratio_map(fit_outputs, ratio_pair, tolerance):
    
    p1, p2 = ratio_pair
    records = []

    for fit in fit_outputs:

        sample = fit["Sample"]

        # -----------------------
        # Extract XY
        # -----------------------
        try:
            x_pos = float(sample.split("_X")[1].split("_")[0])
            y_pos = float(sample.split("_Y")[1])
        except:
            continue  # skip non-positional

        params = fit["params"]
        peaks = fit["peaks"]

        # -----------------------
        # Get peak areas
        # -----------------------
        def get_peakarea(target):
            print('Find peaks: ', target, peaks)
            # ✅ ALWAYS pick closest fitted peak
            idx = np.argmin([abs(p - target) for p in peaks])

            a, c, s, g = params[idx*4:(idx+1)*4]

            x_local = np.linspace(c - 10, c + 10, 200)
            y_local = voigt(x_local, a, c, s, g)

            return np.trapz(y_local, x_local)


        peakarea1 = get_peakarea(p1)
        peakarea2 = get_peakarea(p2)

        if peakarea2 == 0 or np.isnan(peakarea1) or np.isnan(peakarea2):
            ratio = np.nan
        else:
            ratio = peakarea1 / peakarea2

        records.append([x_pos, y_pos, ratio])

    if len(records) == 0:
        return np.array([])

    return np.array(records)


# -------------------------------------------------
# RAW INTENSITY MAP
# -------------------------------------------------
def build_intensity_map(dfMain):

    records = []

    for sample, grp in dfMain.groupby("Sample"):

        if "X_um" not in grp.columns:
            continue

        x_pos, y_pos = parse_xy(sample)
        if x_pos is None:
            continue

        x = grp["RamanShift"].values
        y = grp["Intensity"].values

        # ✅ SORT BY X (critical fix)
        order = np.argsort(x)
        x = x[order]
        y = y[order]

        total_intensity = np.trapz(y, x)

        records.append([x_pos, y_pos, total_intensity])

    return np.array(records)
