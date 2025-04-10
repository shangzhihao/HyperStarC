import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from . import config
import gradio as gr

def upload_samples(filepath: str)->Figure|None:
    samples = _read_samples(filepath)
    if samples is None:
        return None
    return gen_hist(samples)

def _read_samples(filepath: str)->NDArray|None:
    if not Path(filepath).is_file():
        logging.error("file not found")
        return None

    try:
        res = np.squeeze(np.loadtxt(filepath))
    except (IOError, OSError) as e:
        logging.error(f"Error loading file: {e}")
        return None
    except ValueError as e:
        logging.error(f"Error in file format: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    if res.ndim != 1:
        raise ValueError("samples must be 1-dimentional")
    config.samples = res
    return res


def gen_hist(data: NDArray)->Figure:
    if not np.squeeze(data).ndim == 1:
        raise ValueError("samples must be 1-dimentional")
    data1d = np.squeeze(data)
    num_sample = config.sample_percent * data1d.size / 100
    num_sample = max(num_sample, config.total_sample)
    num_sample = min(num_sample, data1d.size)

    data1d = data1d[:int(num_sample)]
    fig, ax = plt.subplots()
    ax.hist(data1d, bins=config.hist_bins, color='red', alpha=0.6, density=True)
    ax.set_xlabel("samples")
    ax.set_ylabel("histogram")
    ax.legend()
    return fig

def replot_click()->Figure|None:
    if config.samples is None:
        return None
    return gen_hist(config.samples)


# Function to handle fitting logic (can be adapted based on your needs)
def fit_click(fitter, branch, reassignment, queue_opt, shuffles):
    return f"Fitted with {fitter}, branch={branch}, reassignment={reassignment}, queue_opt={queue_opt}, shuffles={shuffles}"

# Update ui based on selected fitter
def fitter_change(fitter):
    res = [gr.update(visible=False) for _ in config.DISTS]
    idx = config.DISTS.index(fitter)
    res[idx] = gr.update(visible=True)
    return res

# max and min on sample number
def sample_num_change(num):
    config.total_sample = num

def sample_percentage_change(num):
    if num > 100:
        num = 100
    if num < 1:
        num = 1
    config.sample_percent = num