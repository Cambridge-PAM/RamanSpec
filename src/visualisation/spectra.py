import matplotlib.pyplot as plt


def plot(df, focus_range=None):
    
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10,5))

    for sample, grp in df.groupby("Sample"):

        grp = grp.sort_values("RamanShift")
        x = grp["RamanShift"]
        y = grp["Intensity"]

        if focus_range:
            mask = (x >= focus_range[0]) & (x <= focus_range[1])
            x = x[mask]
            y = y[mask]

        ax.plot(x, y, label=sample)

    ax.legend()
    return fig