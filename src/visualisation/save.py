from pathlib import Path
from datetime import datetime

def save_plot(fig, experiment_name, plot_type, base_folder="outputs"):

    # Create experiment-specific subfolder
    output_folder = Path(base_folder) / experiment_name
    output_folder.mkdir(parents=True, exist_ok=True)

    # Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Filename
    filename = f"{experiment_name}__{plot_type}__{timestamp}.png"

    filepath = output_folder / filename

    fig.savefig(filepath, dpi=300, bbox_inches="tight")

    print(f"Saved: {filepath}")
