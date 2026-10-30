from pathlib import Path
from datetime import datetime


def save_plot(
    fig,
    experiment_name,
    plot_type,
    base_folder="outputs",
    file_prefix=None,
    data=None,
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

    if data is not None:
        data.to_csv(filepath.with_suffix(".csv"), index=False)

    print(f"{plot_type} : Saved")
