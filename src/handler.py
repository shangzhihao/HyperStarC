from numpy.typing import NDArray
import numpy as np
from pathlib import Path
import logging
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

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
    except:
        logging.error("cannot load file")
        return None
    if len(res.shape) == 2:
        return res[:, 0]
    return res


def gen_hist(data: NDArray)->Figure:
    fig, ax = plt.subplots()
    ax.hist(data, bins=100, color='red', alpha=0.6, density=True, label='samples-200 steps')
    ax.set_xlabel("samples")
    ax.set_ylabel("histogram")
    ax.legend()
    return fig
