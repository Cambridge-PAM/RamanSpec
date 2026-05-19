
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
            delim_whitespace=True,
            engine="python"
        )

        if data.shape[1] == 2:
            data.columns = ["RamanShift", "Intensity"]

        elif data.shape[1] >= 4:
            data.columns = ["X_um", "Y_um", "RamanShift", "Intensity"]
            data["X_um"] -= data["X_um"].min()
            data["Y_um"] -= data["Y_um"].max()

        else:
            raise ValueError(f"Unexpected format: {file}")

        sample_name = rename[i] if rename else file

        data["Sample"] = sample_name
        df_all = pd.concat([df_all, data], ignore_index=True)

    return df_all
