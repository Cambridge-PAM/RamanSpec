from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt


def save_plot(
    fig,
    experiment_name,
    plot_type,
    base_folder="outputs",
    file_prefix=None,
    data=None,
    pdf=False,
):

    # Create experiment-specific subfolder
    output_folder = Path(base_folder) / experiment_name
    output_folder.mkdir(parents=True, exist_ok=True)

    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Filename
    filename = f"{file_prefix or experiment_name}__{plot_type}.png"

    filepath = output_folder / filename

    fig.savefig(filepath, dpi=300, bbox_inches="tight")

    if pdf:
        # fonttype 42 embeds text as real fonts so it stays editable in Illustrator/Inkscape
        with plt.rc_context({"pdf.fonttype": 42}):
            fig.savefig(filepath.with_suffix(".pdf"), bbox_inches="tight")

    if data is not None:
        data.to_csv(filepath.with_suffix(".csv"), index=False)

    print(f"{plot_type} : Saved")
