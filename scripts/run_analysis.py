from src.io.loader import load_files
from src.processing.pipeline import Pipeline
from src.processing.baseline import psalsa_baseline
from src.processing.normalize import auc_normalise
from src.visualization.spectra import plot
from src.analysis.ratios import compute_ratio
from src.visualization.peaks import peak_comparison
from src.visualization.ratios import plot_ratios
from src.visualization.save import save_plot


# -----------------------
# SETTINGS
# -----------------------
folder = "data/raw"
indices = [20,21,22]
rename = ["mat1", "mat2", "mat3"]

peak1 = (1700, 1740)
peak2 = (670, 695)

# -----------------------
# LOAD
# -----------------------
df = load_files(folder, indices, rename)

plot(df)

# -----------------------
# PROCESS
# -----------------------
pipe = Pipeline()
pipe.add(psalsa_baseline)
pipe.add(auc_normalise)

df_proc = pipe.run(df)

plot(df_proc, stacked=True)


fig_peaks = peak_comparison(df_proc, peak1, peak2)
save_plot(fig_peaks, "experiment", "peak_comparison")


# -----------------------
# ANALYSIS
# -----------------------
ratios = compute_ratio(df_proc, peak1, peak2)

print(ratios)