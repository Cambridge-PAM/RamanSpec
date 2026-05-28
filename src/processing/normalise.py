import numpy as np

def auc_normalise(df, subset=None):
    """
    Normalize the intensity values in the DataFrame by total area under the curve (AUC) for each sample. Assuming linear x-indices, this calculates 

    Parameters:
        df (pd.DataFrame): The input DataFrame with columns "RamanShift" and "Intensity".
        subset (tuple, optional): A tuple specifying the range of RamanShift (min, max) to use for normalization.

    Returns:
        pd.DataFrame: The normalized DataFrame.
    """
    def apply(grp):
        sample = grp.name
        y = grp["Intensity"].values
        if subset:
            # Apply subset mask
            mask = (grp["RamanShift"] >= subset[0]) & (grp["RamanShift"] <= subset[1])
            normalization_factor = np.sum(y[mask]) if np.any(mask) else 1  # Avoid division by zero
        else:
            normalization_factor = np.sum(y)
        grp["Intensity"] = y / normalization_factor
        return grp

    return df.groupby("Sample", group_keys=False).apply(apply)

def vector_normalise(df, subset=None):
    """
    Apply vector normalisation to intensity values.

    Parameters:
        df (pd.DataFrame): Input DataFrame with "RamanShift" and "Intensity".
        subset (tuple, optional): (min, max) RamanShift range for calculating norm.

    Returns:
        pd.DataFrame: Normalised DataFrame.
    """
    def apply(grp):
        sample = grp.name
        y = grp["Intensity"].values

        if subset:
            mask = (grp["RamanShift"] >= subset[0]) & (grp["RamanShift"] <= subset[1])
            norm_factor = np.linalg.norm(y[mask]) if np.any(mask) else 1
        else:
            norm_factor = np.linalg.norm(y)

        grp["Intensity"] = y / (norm_factor if norm_factor != 0 else 1)
        return grp

    return df.groupby("Sample", group_keys=False).apply(apply)

def snv_normalise(df, subset=None):
    """
    Apply Standard Normal Variate (SNV) normalisation.

    Parameters:
        df (pd.DataFrame): Input DataFrame.
        subset (tuple, optional): (min, max) RamanShift range for calculating mean/std.

    Returns:
        pd.DataFrame: Normalised DataFrame.
    """
    def apply(grp):
        sample = grp.name
        y = grp["Intensity"].values

        if subset:
            mask = (grp["RamanShift"] >= subset[0]) & (grp["RamanShift"] <= subset[1])
            if np.any(mask):
                mean = np.mean(y[mask])
                std = np.std(y[mask])
            else:
                mean = np.mean(y)
                std = np.std(y)
        else:
            mean = np.mean(y)
            std = np.std(y)

        grp["Intensity"] = (y - mean) / (std if std != 0 else 1)
        return grp

    return df.groupby("Sample", group_keys=False).apply(apply,include_groups=True)