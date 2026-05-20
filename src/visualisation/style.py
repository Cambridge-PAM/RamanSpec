
import re
import matplotlib.cm as cm
import numpy as np

def parse_sample_name(name):
    """
    Extract:
    - prefix (e.g. 'mat', 'wg')
    - number (e.g. 1, 2)
    """

    match = re.match(r"([a-zA-Z]+)[ _]?(\d+)", name)

    if match:
        prefix = match.group(1)
        number = int(match.group(2))
    else:
        prefix = name
        number = 0

    return prefix, number

def build_style_map(samples):
    parsed = [parse_sample_name(s) for s in samples]

    prefixes = sorted(set(p[0] for p in parsed))
    numbers = sorted(set(p[1] for p in parsed))

    # -----------------------
    # COLOURS → numbers
    # -----------------------
    cmap = cm.viridis(np.linspace(0, 1, len(prefixes)))

    number_color = dict(zip(prefixes, cmap))

    # -----------------------
    # MARKERS → prefixes
    # -----------------------
    markers = ['o', '^', 's', 'D', 'v', '*']

    prefix_marker = {
        p: markers[i % len(markers)]
        for i, p in enumerate(numbers)
    }

    # -----------------------
    # LINESTYLES → prefixes (optional)
    # -----------------------
    linestyles = ['-', ':', '--', '-.']

    prefix_linestyle = {
        p: linestyles[i % len(linestyles)]
        for i, p in enumerate(numbers)
    }

    # -----------------------
    # BUILD FINAL MAP
    # -----------------------
    style_map = {}

    for s in samples:

        prefix, number = parse_sample_name(s)

        style_map[s] = {
            "color": number_color[prefix],
            "marker": prefix_marker[number],
            "linestyle": prefix_linestyle[number]
        }

    return style_map

