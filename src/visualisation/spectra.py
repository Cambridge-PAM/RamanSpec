import matplotlib.pyplot as plt

 fig, ax = plt.subplots(figsize=(10,5))def plot(df, stacked=False):

    for i, (sample, grp) in enumerate(df.groupby("Sample")):

        grp = grp.sort_values("RamanShift")

        x = grp["RamanShift"]
        y = grp["Intensity"]

        if stacked:
            y = y + i * 0.0002

        ax.plot(x, y, label=sample)

    ax.set_xlabel("Raman shift (cm⁻¹)")
    ax.set_ylabel("Intensity")
    ax.legend()

    return fig
``

