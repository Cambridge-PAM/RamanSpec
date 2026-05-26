import panel as pn
import matplotlib.pyplot as plt

pn.extension()

from src.visualisation.style import build_style_map
from src.processing.baseline import psalsa_baseline
from src.processing.smoothing import smooth
from src.processing.normalise import auc_normalise, vector_normalise, snv_normalise


def build_app(df_raw, style_map=None, focus_range=None):

    if style_map is None:
        style_map = build_style_map(df_raw["Sample"].unique())

    NORMALISERS = {
        "AUC": auc_normalise,
        "Vector": vector_normalise,
        "SNV": snv_normalise,
    }

    # -----------------------
    # STATE
    # -----------------------
    baseline_params = {"lam": 1e6, "p": 0.01}
    smoothing_params = {"window": 7, "poly": 3}

    x_min = df_raw["RamanShift"].min()
    x_max = df_raw["RamanShift"].max()
    norm_range = [x_min, x_max]

    toggles = ["baseline", "smoothing", "normalisation"]

    # -----------------------
    # WIDGETS
    # -----------------------
    mode = pn.widgets.RadioButtonGroup(name="Mode", options=["Raw", "Processed"])

    baseline_method = pn.widgets.Select(name="Baseline", options=["PSALSA"])

    lam = pn.widgets.FloatInput(name="λ", value=1e6)
    p = pn.widgets.FloatInput(name="p", value=0.01)

    window = pn.widgets.IntInput(name="Window", value=7)
    poly = pn.widgets.IntInput(name="Poly", value=3)

    norm_method = pn.widgets.Select(name="Normalisation", options=["AUC", "Vector", "SNV"])

    norm_min = pn.widgets.FloatInput(name="Norm Min", value=x_min)
    norm_max = pn.widgets.FloatInput(name="Norm Max", value=x_max)

    processing = pn.widgets.CheckBoxGroup(
        name="Processing",
        value=toggles,
        options=["baseline", "smoothing", "normalisation"]
    )

    sample_selector = pn.widgets.MultiChoice(
        name="Samples",
        value=list(df_raw["Sample"].unique()),
        options=list(df_raw["Sample"].unique())
    )

    show_baseline = pn.widgets.Checkbox(name="Show Baseline", value=False)

    # -----------------------
    # PROCESSING
    # -----------------------
    def apply_processing():
        df = df_raw.copy()

        if mode.value == "Processed":

            if "baseline" in processing.value:
                df = psalsa_baseline(df, lam=lam.value, p=p.value)

            if "smoothing" in processing.value:
                df = smooth(df, window=window.value, poly=poly.value)

            if "normalisation" in processing.value:
                df = NORMALISERSdf,
                    subset=(norm_min.value, norm_max.value)
                

        return df

    # -----------------------
    # PLOT
    # -----------------------
    @pn.depends(
        mode, lam, p, window, poly,
        norm_method, norm_min, norm_max,
        processing, sample_selector, show_baseline
    )
    def plot():
        df = apply_processing()

        fig, ax = plt.subplots(figsize=(8, 5))

        for sample, grp in df.groupby("Sample"):
            if sample not in sample_selector.value:
                continue

            grp = grp.sort_values("RamanShift")
            x = grp["RamanShift"]
            y = grp["Intensity"]

            ax.plot(x, y, label=sample)

            if show_baseline.value and "Baseline" in grp.columns:
                ax.plot(x, grp["Baseline"], "--", alpha=0.4)

        ax.set_xlabel("Raman shift (cm⁻¹)")
        ax.set_ylabel("Intensity")
        ax.set_title(
            f"Norm range: {norm_min.value:.1f}–{norm_max.value:.1f}"
        )
        ax.legend()

        return fig

    # -----------------------
    # LAYOUT (Panel UI)
    # -----------------------
    sidebar = pn.Column(
        "## Controls",

        pn.Card(mode, sample_selector, title="Data", collapsible=True),

        pn.Card(
            baseline_method,
            lam,
            p,
            title="Baseline",
            collapsible=True
        ),

        pn.Card(
            window,
            poly,
            title="Smoothing",
            collapsible=True
        ),

        pn.Card(
            norm_method,
            norm_min,
            norm_max,
            processing,
            title="Normalisation",
            collapsible=True
        ),

        pn.Card(
            show_baseline,
            title="Display",
            collapsible=True
        ),
        width=300
    )

    return pn.Row(sidebar, plot)
