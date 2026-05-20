import matplotlib.pyplot as plt

def plot_ratios(df):
    
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8,5))

    for key, grp in df.groupby(["Peak1", "Peak2"]):

        label = f"{key[0]}/{key[1]}"

        ax.scatter(grp["Sample"], grp["Ratio"], label=label)

    ax.legend()
    return fig
