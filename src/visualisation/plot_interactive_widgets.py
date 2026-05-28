import matplotlib.pyplot as plt

import seaborn as sns
sns.set_theme(style="whitegrid")

from matplotlib.widgets import Button, RadioButtons, CheckButtons, TextBox

from src.visualisation.style import build_style_map
from src.processing.baseline import psalsa_baseline
from src.processing.smoothing import smooth
from src.processing.normalise import auc_normalise, vector_normalise, snv_normalise


def plot_interactive_with_widgets(df_raw, style_map=None):

    # -----------------------
    # FIGURE SETUP
    # -----------------------
    fig = plt.figure(figsize=(14, 8))

    ax_plot = fig.add_axes([0.32, 0.1, 0.65, 0.8])  # main plot

    if style_map is None:
        style_map = build_style_map(df_raw["Sample"].unique())

    # -----------------------
    # STATE
    # -----------------------
    state = {
        "mode": "Raw",
        "normalisation": "AUC",
        "show_baseline": False,
    }

    baseline_params = {"lam": 1e6, "p": 0.01}
    smoothing_params = {"window": 7, "poly": 3}

    x_min = df_raw["RamanShift"].min()
    x_max = df_raw["RamanShift"].max()
    norm_range = [x_min, x_max]

    toggles = {"baseline": True, "smoothing": True, "normalisation": True}
    visibility = {s: True for s in df_raw["Sample"].unique()}

    NORMALISERS = {
        "AUC": auc_normalise,
        "Vector": vector_normalise,
        "SNV": snv_normalise,
    }

    # -----------------------
    # PROCESSING
    # -----------------------
    last_params = {}

    def get_param_state():
        return (
            state["mode"],
            tuple(sorted(toggles.items())),
            tuple(sorted(baseline_params.items())),
            tuple(sorted(smoothing_params.items())),
            state["normalisation"],
            tuple(norm_range),
        )

    cached_df = None
    
    def process():
        global cached_df

        params = get_param_state()

        if params == last_params and cached_df is not None:
            return cached_df

        df = df_raw.copy()

        if state["mode"] == "Processed":

            if toggles["baseline"]:
                df = psalsa_baseline(df, **baseline_params)

            if toggles["smoothing"]:
                df = smooth(df, **smoothing_params)

            if toggles["normalisation"]:
                df = NORMALISERS[state["normalisation"]](
                    df,
                    subset=tuple(norm_range)
                )

        # update cache
        last_params.clear()
        last_params.update({i: p for i, p in enumerate(params)})
        cached_df = df

        return df

    # -----------------------
    # PLOT
    # -----------------------
    lines = {}
    
    def draw(preserve_zoom=True):
        # -----------------------
        # Store X zoom only
        # -----------------------
        if preserve_zoom:
            try:
                xlim = ax_plot.get_xlim()
            except:
                xlim = None
        else:
            xlim = None

        ax_plot.clear()
        df = process()

        visible_data = []

        for sample, grp in df.groupby("Sample"):
            if not visibility[sample]:
                continue

            grp = grp.sort_values("RamanShift")

            x = grp["RamanShift"].values
            y = grp["Intensity"].values

            sns.lineplot(x=x, y=y, ax=ax_plot, label=sample)

            visible_data.append((x, y))

            if state["show_baseline"] and "Baseline" in grp.columns:
                ax_plot.plot(x, grp["Baseline"], "--", alpha=0.4)

        # -----------------------
        # Restore / apply X zoom
        # -----------------------
        if xlim is not None:
            ax_plot.set_xlim(xlim)
        else:
            ax_plot.set_xlim(x_min, x_max)  # ✅ full spectrum fallback

        # -----------------------
        # Recompute Y range from visible X
        # -----------------------
        x0, x1 = ax_plot.get_xlim()

        y_vals = []

        for x, y in visible_data:
            mask = (x >= x0) & (x <= x1)
            if mask.any():
                y_vals.extend(y[mask])

        if y_vals:
            ymin = min(y_vals)
            ymax = max(y_vals)
            padding = 0.05 * (ymax - ymin if ymax > ymin else 1)

            ax_plot.set_ylim(ymin - padding, ymax + padding)

        # -----------------------
        # Labels
        # -----------------------
        ax_plot.set_title(
            f"{state['mode']} | Norm: {norm_range[0]:.1f}-{norm_range[1]:.1f}"
        )
        ax_plot.set_xlabel("Raman Shift (cm⁻¹)")
        ax_plot.set_ylabel("Intensity")

        fig.canvas.draw_idle()

        


    # -----------------------
    # CALLBACKS
    # -----------------------
    def set_mode(label):
        state["mode"] = label
        draw()

    def set_norm(label):
        state["normalisation"] = label
        draw()

    def toggle_proc(label):
        toggles[label] = not toggles[label]
        draw()

    def toggle_line(label):
        visibility[label] = not visibility[label]
        draw()

    def toggle_baseline(event):
        state["show_baseline"] = not state["show_baseline"]
        draw()

    def update_float(box, key, container, cond=lambda x: True):
        def f(text):
            try:
                val = float(text)
                if cond(val):
                    container[key] = val
                    box.ax.set_facecolor("#d4f7d4")
                    draw()
                else:
                    box.ax.set_facecolor("#f7d4d4")
            except:
                box.ax.set_facecolor("#f7d4d4")
            fig.canvas.draw_idle()
        return f

    def update_int(box, key, container, cond=lambda x: True):
        def f(text):
            try:
                val = int(text)
                if cond(val):
                    container[key] = val
                    box.ax.set_facecolor("#d4f7d4")
                    draw()
                else:
                    box.ax.set_facecolor("#f7d4d4")
            except:
                box.ax.set_facecolor("#f7d4d4")
            fig.canvas.draw_idle()
        return f

    # -----------------------
    # UI LAYOUT (simple grid)
    # -----------------------

    widgets = {}
    fig._widgets = widgets  # prevent GC

    # ---- MODE ----
    widgets["mode"] = RadioButtons(
        fig.add_axes([0.02, 0.75, 0.25, 0.15]),
        ["Raw", "Processed"]
    )
    widgets["mode"].on_clicked(set_mode)

    # ---- SAMPLES ----
    widgets["samples"] = RadioButtons(
        fig.add_axes([0.02, 0.5, 0.25, 0.25]),
        list(df_raw["Sample"].unique())
    )
    widgets["samples"].on_clicked(toggle_line)

    # ---- NORMALISATION ----
    widgets["norm"] = RadioButtons(
        fig.add_axes([0.02, 0.3, 0.12, 0.15]),
        ["AUC", "Vector", "SNV"]
    )
    widgets["norm"].on_clicked(set_norm)

    # norm range
    widgets["norm_min"] = TextBox(fig.add_axes([0.15, 0.35, 0.12, 0.05]), "min", initial=str(x_min))
    widgets["norm_max"] = TextBox(fig.add_axes([0.15, 0.3, 0.12, 0.05]), "max", initial=str(x_max))

    widgets["norm_min"].on_submit(
        update_float(widgets["norm_min"], 0, norm_range, lambda x: x < norm_range[1])
    )
    widgets["norm_max"].on_submit(
        update_float(widgets["norm_max"], 1, norm_range, lambda x: x > norm_range[0])
    )

    # ---- BASELINE ----
    widgets["lam"] = TextBox(fig.add_axes([0.02, 0.2, 0.12, 0.05]), "λ", initial="1e6")
    widgets["p"] = TextBox(fig.add_axes([0.15, 0.2, 0.12, 0.05]), "p", initial="0.01")

    widgets["lam"].on_submit(
        update_float(widgets["lam"], "lam", baseline_params, lambda x: x > 0)
    )
    widgets["p"].on_submit(
        update_float(widgets["p"], "p", baseline_params, lambda x: 0 < x < 1)
    )

    # ---- SMOOTHING ----
    widgets["win"] = TextBox(fig.add_axes([0.02, 0.1, 0.12, 0.05]), "win", initial="7")
    widgets["poly"] = TextBox(fig.add_axes([0.15, 0.1, 0.12, 0.05]), "poly", initial="3")

    widgets["win"].on_submit(
        update_int(widgets["win"], "window", smoothing_params,
                   lambda x: x > 1 and x % 2 == 1)
    )
    widgets["poly"].on_submit(
        update_int(widgets["poly"], "poly", smoothing_params,
                   lambda x: x >= 1)
    )

    # ---- PROCESS TOGGLES ----
    widgets["proc"] = CheckButtons(
        fig.add_axes([0.02, 0.02, 0.25, 0.07]),
        ["baseline", "smoothing", "normalisation"],
        [True, True, True]
    )
    widgets["proc"].on_clicked(toggle_proc)

    # ---- BASELINE BUTTON ----
    widgets["baseline_btn"] = Button(
        fig.add_axes([0.02, 0.9, 0.25, 0.05]),
        "Toggle Baseline"
    )
    widgets["baseline_btn"].on_clicked(toggle_baseline)

    # -----------------------
    # INIT DRAW
    # -----------------------
    draw(preserve_zoom=False)
    plt.show()