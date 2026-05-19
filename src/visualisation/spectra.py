import matplotlib.pyplot as plt

def plot(df, stacked=False):

    for i, (sample, grp) in enumerate(df.groupby("Sample")):

        x = grp["RamanShift"]
        y = grp["Intensity"]

        if stacked:
            y = y + i * 0.0002

        plt.plot(x, y, label=sample)

    plt.xlabel("Raman shift (cm⁻¹)")
    plt.ylabel("Intensity")
    plt.legend()
    plt.show()