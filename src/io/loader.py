
import os
import pandas as pd

def load_files(folder, indices=None, rename=None):

    files = [f for f in os.listdir(folder) if f.endswith(".txt")]

    if indices is not None:
        files = [files[i] for i in indices]

    df_all = pd.DataFrame()

    for i, file in enumerate(files):

        path = os.path.join(folder, file)

        data = pd.read_csv(
            path,
            sep='\s+',
            engine="python"
        )

        base_name = rename[i] if rename else file

        # Normalise column names (important!)
        data.columns = [col.strip().lower() for col in data.columns]

        # -------------------------------------------------
        # 1. NON-POSITIONAL DATA
        # -------------------------------------------------
        if len(data.columns) == 2:

            data.columns = ["ramanshift", "intensity"]
            data["Sample"] = base_name
            data["CoordType"] = "none"

        # -------------------------------------------------
        # 2. POSITIONAL DATA
        # -------------------------------------------------
        elif len(data.columns) >= 4:

            cols = data.columns
            # -----------------------
            # ✅ Detect X-Y
            # -----------------------
            if "x" in cols[0] and "y" in cols[1]:

                data.columns = ["X_um", "Y_um", "RamanShift", "Intensity"]

                data["X_um"] -= data["X_um"].min()
                data["Y_um"] -= data["Y_um"].max()

                data["Sample"] = data.apply(
                    lambda row: f"{base_name}_X{row['X_um']:.2f}_Y{row['Y_um']:.2f}",
                    axis=1
                )

                data["CoordType"] = "XY"
                print(f" -> Loaded {file} → as X/Y")

            # -----------------------
            # ✅ Detect R-Z (depth)
            # -----------------------
            elif "r" in cols[0] and "z" in cols[1]:

                data.columns = ["R_um", "Z_um", "RamanShift", "Intensity"]

                data["R_um"] -= data["R_um"].min()

                data["Sample"] = data.apply(
                    lambda row: f"{base_name}_R{row['R_um']:.2f}_Z{row['Z_um']:.2f}",
                    axis=1
                )

                data["CoordType"] = "RZ"
                print(f" -> Loaded {file} → as R/Z")

            # -------------------------------------------------
            # ⚠️ FALLBACK (assume XY)
            # -------------------------------------------------
            else:
                print(f"⚠️ Could not detect coordinate type for {file} → assuming X/Y")

                data.columns = ["X_um", "Y_um", "RamanShift", "Intensity"]

                data["X_um"] -= data["X_um"].min()
                data["Y_um"] -= data["Y_um"].max()

                data["Sample"] = data.apply(
                    lambda row: f"{base_name}_X{row['X_um']:.2f}_Y{row['Y_um']:.2f}",
                    axis=1
                )

                data["CoordType"] = "XY"

        else:
            raise ValueError(f"Unexpected format: {file}")

        df_all = pd.concat([df_all, data], ignore_index=True)

    return df_all