import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from . import config

logger = logging.getLogger(__name__)
# generate a histogram of given samples
def gen_hist(samples: NDArray) -> Figure|None:
    if not np.squeeze(samples).ndim == 1:
        logger.error("samples must be 1-dimentional")
        return None
    fig, ax = plt.subplots()
    ax.hist(samples, bins=config.hist_bins, color="red", alpha=0.6, density=True)
    left, right = None, None
    if config.min_x != 0:
        left = config.min_x
    if config.max_x != 0:
        right = config.max_x
    ax.set_xlim(left=left, right=right)
    ax.set_xlabel("samples")
    ax.set_ylabel("histogram", color="red")
    # ax.legend(f"{num_sample} samples")
    plt.tight_layout()
    return fig


# replot histogram, number of samples may change
def replot_click() -> Figure | None:
    if config.samples is None:
        return None
    return gen_hist(config.samples)

# event handler for histogram bins
def bins_num_change(num):
    config.hist_bins = num

# event handler for max x in plotting
def max_x_change(num):
    config.max_x = num

# event handler for min x in plotting
def min_x_change(num):
    config.min_x = num