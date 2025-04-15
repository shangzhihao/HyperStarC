import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from src.fitters import ErlangFitter, ExponentialFitter, Fitter

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
    ax.set_ylabel("histogram", color='red')
    # ax.legend(f"{num_sample} samples")
    plt.tight_layout()
    return fig

def replot_click()->Figure|None:
    if config.samples is None:
        return None
    return gen_hist(config.samples)


def fit_click()->Figure|None:
    if config.samples is None:
        logging.log(logging.ERROR, "No samples loaded")
        return None
    fitter = make_fitter()
    if fitter is None:
        logging.log(logging.ERROR, "No fitter selected")
        return None
    dist = fitter.fit(config.samples)
    fig = gen_hist(config.samples)
    smp_min = np.min(config.samples)
    smp_max = np.max(config.samples)
    x = np.linspace(smp_min, smp_max, 100)
    y = [dist.pdf(i) for i in x]
    ax2 = fig.axes[0].twinx()
    ax2.plot(x, y, color='blue')
    ax2.set_ylabel("pdf", color='blue')
    plt.tight_layout()
    return fig

# Update ui based on selected fitter
def fitter_change(fitter: str):
    res = [gr.update(visible=False) for _ in config.FITTER_NAMES]
    if fitter not in config.FITTER_NAMES:
        return res
    idx = config.FITTER_NAMES.index(fitter)
    res[idx] = gr.update(visible=True)
    config.selected_fitter = config.FITTERS(fitter)
    return res

# max and min on sample number
def sample_num_change(num: int):
    config.total_sample = num

def sample_percentage_change(num: int):
    if num > 100:
        num = 100
    if num < 1:
        num = 1
    config.sample_percent = num

def make_fitter()->Fitter|None:
    if config.selected_fitter == config.FITTERS.Exponential:
        return ExponentialFitter()
    if config.selected_fitter == config.FITTERS.Erlang:
        return ErlangFitter(method=config.erlang_method, rounding=config.eralng_rounding, max_phase=config.erlang_max_phase)
    return None
