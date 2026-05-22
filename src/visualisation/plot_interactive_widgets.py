import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider, CheckButtons
from src.visualisation.style import build_style_map
from src.processing.baseline import psalsa_baseline
from src.processing.smoothing import smooth
from src.processing.normalise import auc_normalise

def plot_interactive_with_widgets(df_raw, style_map=None, focus_range=None):
    # Initialize the figure and axes
    fig, ax = plt.subplots(figsize=(14, 8))  # Larger plot size
    plt.subplots_adjust(left=0.3, bottom=0.3)  # Leave space for widgets

    # Default to raw data
    current_df = df_raw.copy()
    show_baseline = False
    current_data_state = "Raw"

    if style_map is None:
        style_map = build_style_map(df_raw["Sample"].unique())

    # Store line objects and metadata
    lines = {}
    line_metadata = {sample: {"visible": True} for sample in df_raw["Sample"].unique()}

    # Processing parameters and toggles
    baseline_params = {"lam": 1e6, "p": 0.01}
    smoothing_params = {"window": 7, "poly": 3}
    processing_toggles = {"baseline": True, "smoothing": True, "normalization": True}

    # Function to apply processing dynamically
    def apply_processing():
        df = df_raw.copy()
        if current_data_state == "Processed":
            # Apply baseline correction if enabled
            if processing_toggles["baseline"]:
                df = psalsa_baseline(df, lam=baseline_params["lam"], p=baseline_params["p"])
            # Apply smoothing if enabled
            if processing_toggles["smoothing"]:
                df = smooth(df, window=smoothing_params["window"], poly=smoothing_params["poly"])
            # Apply normalization if enabled
            if processing_toggles["normalization"]:
                df = auc_normalise(df)
        return df

    # Function to plot data
    def plot_data(df, show_baseline=False):
        # Preserve zoom level
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        ax.clear()
        for sample, grp in df.groupby("Sample"):
            grp = grp.sort_values("RamanShift")
            x = grp["RamanShift"]
            y = grp["Intensity"]

            if focus_range:
                mask = (x >= focus_range[0]) & (x <= focus_range[1])
                x = x[mask]
                y = y[mask]

            style = style_map[sample]
            line, = ax.plot(
                x,
                y,
                label=sample,
                color=style["color"],
                linestyle=style["linestyle"],
                visible=line_metadata[sample]["visible"],  # Use stored visibility state
            )

            # Optionally plot baseline (only for raw data)
            if show_baseline and current_data_state == "Raw" and "Baseline" in grp.columns:
                ax.plot(
                    x,
                    grp["Baseline"][mask] if focus_range else grp["Baseline"],
                    '--',
                    color=style["color"],
                    alpha=0.5,
                )

            # Store metadata
            lines[sample] = line

        ax.set_xlabel("Raman shift (cm⁻¹)")
        ax.set_ylabel("Intensity")
        ax.set_title("Interactive Raman Spectra")
        ax.legend(loc="upper right")

        # Restore zoom level
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        fig.canvas.draw_idle()

    # Initial plot
    plot_data(current_df, show_baseline)

    # -----------------------
    # Widget Callbacks
    # -----------------------

    def toggle_spectrum(label):
        # Toggle visibility of a spectrum
        metadata = line_metadata[label]
        metadata["visible"] = not metadata["visible"]
        lines[label].set_visible(metadata["visible"])
        fig.canvas.draw_idle()

    def toggle_baseline(event):
        # Toggle the baseline visibility
        nonlocal show_baseline
        show_baseline = not show_baseline
        plot_data(current_df, show_baseline)

    def switch_data(label):
        # Switch between raw and processed data
        nonlocal current_df, current_data_state
        current_data_state = label
        current_df = apply_processing()
        plot_data(current_df, show_baseline)

    def update_baseline(val):
        # Update baseline parameters
        baseline_params["lam"] = baseline_slider.val
        baseline_params["p"] = baseline_slider_p.val
        if current_data_state == "Processed":
            switch_data("Processed")

    def update_smoothing(val):
        # Update smoothing parameters
        smoothing_params["window"] = int(smoothing_slider_window.val)
        smoothing_params["poly"] = int(smoothing_slider_poly.val)
        if current_data_state == "Processed":
            switch_data("Processed")

    def toggle_processing(label):
        # Toggle specific processing steps
        processing_toggles[label] = not processing_toggles[label]
        if current_data_state == "Processed":
            switch_data("Processed")

    # -----------------------
    # Add Widgets
    # -----------------------

    # RadioButtons for spectrum selection
    spectrum_ax = plt.axes([0.05, 0.6, 0.2, 0.3])  # Adjust position for RadioButtons
    spectrum_radio = RadioButtons(spectrum_ax, list(df_raw["Sample"].unique()))

    def on_spectrum_change(label):
        toggle_spectrum(label)

    spectrum_radio.on_clicked(on_spectrum_change)

    # Button for toggling baseline
    baseline_ax = plt.axes([0.05, 0.5, 0.2, 0.075])  # Adjust position
    baseline_button = Button(baseline_ax, "Toggle Baseline")
    baseline_button.on_clicked(toggle_baseline)

    # Radio buttons for switching data
    radio_ax = plt.axes([0.05, 0.4, 0.2, 0.075])  # Adjust position
    radio = RadioButtons(radio_ax, ["Raw", "Processed"])
    radio.on_clicked(switch_data)

    # Checkboxes for processing toggles
    processing_ax = plt.axes([0.05, 0.2, 0.2, 0.15])  # Adjust position
    processing_labels = ["baseline", "smoothing", "normalization"]
    processing_check = CheckButtons(processing_ax, processing_labels, [True, True, True])
    processing_check.on_clicked(toggle_processing)

    # Sliders for baseline parameters
    baseline_slider_ax = plt.axes([0.3, 0.25, 0.5, 0.03])  # Adjust position
    baseline_slider = Slider(baseline_slider_ax, "Baseline λ", 1e4, 1e7, valinit=baseline_params["lam"], valstep=1e4)
    baseline_slider.on_changed(update_baseline)

    baseline_slider_p_ax = plt.axes([0.3, 0.2, 0.5, 0.03])  # Adjust position
    baseline_slider_p = Slider(baseline_slider_p_ax, "Baseline p", 0.001, 0.1, valinit=baseline_params["p"], valstep=0.001)
    baseline_slider_p.on_changed(update_baseline)

    # Sliders for smoothing parameters
    smoothing_slider_window_ax = plt.axes([0.3, 0.15, 0.5, 0.03])  # Adjust position
    smoothing_slider_window = Slider(smoothing_slider_window_ax, "Smoothing Window", 3, 21, valinit=smoothing_params["window"], valstep=2)
    smoothing_slider_window.on_changed(update_smoothing)

    smoothing_slider_poly_ax = plt.axes([0.3, 0.1, 0.5, 0.03])  # Adjust position
    smoothing_slider_poly = Slider(smoothing_slider_poly_ax, "Smoothing Poly", 1, 5, valinit=smoothing_params["poly"], valstep=1)
    smoothing_slider_poly.on_changed(update_smoothing)

    plt.show()