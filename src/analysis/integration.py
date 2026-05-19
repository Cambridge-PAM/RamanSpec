import numpy as np

def integrate_region(df, region):

    results = []

    for sample, grp in df.groupby("Sample"):

        grp = grp.sort_values("RamanShift")

        mask = (grp["RamanShift"] >= region[0]) & \
               (grp["RamanShift"] <= region[1])

        x = grp["RamanShift"][mask]
        y = grp["Intensity"][mask]

        area = np.trapz(y, x) if len(x) else 0

        results.append({"Sample": sample, "Area": area})

    return results