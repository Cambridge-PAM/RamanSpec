from pathlib import Path
from datetime import datetime

def save_plot(fig, sample_name, plot_type, folder="outputs"):

    Path(folder).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{sample_name}__{plot_type}__{timestamp}.png"

    path = Path(folder) / filename

    fig.savefig(path, dpi=300, bbox_inches="tight")

    print(f"Saved: {path}")