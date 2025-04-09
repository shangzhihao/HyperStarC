import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from . import config


def upload_samples(filepath: str)->Figure|None:
    samples = read_samples(filepath)
    if samples is None:
        return None
    return gen_hist(samples)

def read_samples(filepath: str)->NDArray|None:
    if not Path(filepath).is_file():
        logging.error("file not found")
        return None

    try:
        res = np.loadtxt(filepath)
    except (IOError, OSError) as e:
        logging.error(f"Error loading file: {e}")
        return None
    except ValueError as e:
        logging.error(f"Error in file format: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    
    if len(res.shape) == 2:
        res = res[:, 0]
    config.samples = res
    return res


def gen_hist(data: NDArray)->Figure:
    fig, ax = plt.subplots()
    ax.hist(data, bins=100, color='red', alpha=0.6, density=True, label='samples-200 steps')
    ax.set_xlabel("samples")
    ax.set_ylabel("histogram")
    ax.legend()
    return fig
