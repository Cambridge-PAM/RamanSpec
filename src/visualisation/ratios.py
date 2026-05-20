import matplotlib.pyplot as plt

def plot_ratiosRun" in df.columns:def plot_ratios(df):
        groups = df.groupby("Run")
    else:
        groups = [("Single", df)]

    for name, group in groups:
        ax.scatter(group["Sample"], group["Ratio"], label=name)

    ax.set_ylabel("Peak Ratio")
    ax.set_xlabel("Sample")

    ax.legend()
    plt.xticks(rotation=45)

    return fig

    fig, ax = plt.subplots(figsize=(8,5))

