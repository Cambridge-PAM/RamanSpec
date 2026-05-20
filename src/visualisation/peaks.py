import matplotlib.pyplot as plt

def peak_comparison(df axes = plt.subplots(1, 3, figsize=(15,5))def peak_comparison(df, peak1, peak2, padding=40):

    for sample, grp in df.groupby("Sample"):

        grp = grp.sort_values("RamanShift")

        x = grp["RamanShift"]
        y = grp["Intensity"]

        # --- Peak 1 ---
        mask1 = (x >= peak1[0]-padding) & (x <= peak1[1]+padding)
        axes[0].plot(x[mask1], y[mask1], label=sample)
        axes[0].axvspan(*peak1, color='red', alpha=0.1)

        # --- Peak 2 ---
        mask2 = (x >= peak2[0]-padding) & (x <= peak2[1]+padding)
        axes[1].plot(x[mask2], y[mask2], label=sample)
        axes[1].axvspan(*peak2, color='blue', alpha=0.1)

        # --- Overlay comparison ---
        axes[2].plot(x[mask1], y[mask1] / y[mask1].max(), '--')
        axes[2].plot(x[mask2], y[mask2] / y[mask2].max(), '-')

    axes[0].set_title("Peak 1")
    axes[1].set_title("Peak 2")
    axes[2].set_title("Normalised Comparison")

    for ax in axes:
        ax.set_xlabel("Raman shift")
        ax.set_ylabel("Intensity")

    axes[0].legend()

    plt.tight_layout()

    return fig

