import logging
from pathlib import Path

import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from src.fitters import ErlangFitter, ExponentialFitter, Fitter

from . import config

logger = logging.getLogger(__name__)


# upload samples and draw histogram
def upload_samples(filepath: str) -> Figure | None:
    samples = _read_samples(filepath)
    if samples is None:
        return None
    return gen_hist(samples)


# read samples from given file path and t
def _read_samples(filepath: str) -> NDArray | None:
    if not Path(filepath).is_file():
        logging.error("file not found")
        return None
    try:
        samples = np.squeeze(np.loadtxt(filepath))
    except (IOError, OSError) as e:
        logging.error(f"Error loading file: {e}")
        return None
    except ValueError as e:
        logging.error(f"Error in file format: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None
    if samples.ndim != 1:
        samples = samples[:, 0]
        logger.warning("samples is not 1-dimentional, 1st column will be used")
    config.samples = samples
    return samples


# generate a histogram of given samples
def gen_hist(data: NDArray) -> Figure:
    if not np.squeeze(data).ndim == 1:
        raise ValueError("samples must be 1-dimentional")
    data1d = np.squeeze(data)
    num_sample = config.sample_percent * data1d.size / 100
    num_sample = max(num_sample, config.total_sample)
    num_sample = min(num_sample, data1d.size)

    data1d = data1d[: int(num_sample)]
    fig, ax = plt.subplots()
    ax.hist(data1d, bins=config.hist_bins, color="red", alpha=0.6, density=True)
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


# event handler for fit button
def fit_click() -> Figure | None:
    if config.samples is None:
        logger.error("No samples loaded")
        return None
    fitter = make_fitter()
    if fitter is None:
        logger.error("No fitter selected")
        return None
    dist = fitter.fit(config.samples)
    fig = gen_hist(config.samples)
    smp_min = np.min(config.samples)
    smp_max = np.max(config.samples)
    x = np.linspace(smp_min, smp_max, 100)
    y = [dist.pdf(i) for i in x]
    ax2 = fig.axes[0].twinx()
    ax2.plot(x, y, color="blue")
    ax2.set_ylabel("pdf", color="blue")
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


# event handler for sample number
def sample_num_change(num: int):
    config.total_sample = num


# event handler for sample percentage
def sample_percentage_change(num: int):
    if num > 100:
        num = 100
        logger.warning("sample percentage must be less than 100")
    if num < 1:
        num = 1
        logger.warning("sample percentage must be greater than 100")
    config.sample_percent = num


# generate fitter object based on selected fitter
def make_fitter() -> Fitter | None:
    if config.selected_fitter == config.FITTERS.Exponential:
        return ExponentialFitter()
    if config.selected_fitter == config.FITTERS.Erlang:
        return ErlangFitter(
            method=config.erlang_method,
            rounding=config.eralng_rounding,
            max_phase=config.erlang_max_phase,
        )
    return None


# event handler for erlang fit method
def er_fit_md_cange(fit_method: str) -> None:
    ermd = config.ERMD(fit_method)
    if ermd == config.ERMD.MOM:
        config.erlang_method = config.ERMD.MOM
    elif ermd == config.ERMD.MLE:
        config.erlang_method = config.ERMD.MLE


# event handler for erlang rounding method
def er_round_change(rounding: str) -> None:
    round = config.ROUNDING(rounding)
    if round == config.ROUNDING.ceil:
        config.eralng_rounding = config.ROUNDING.ceil
    elif round == config.ROUNDING.floor:
        config.eralng_rounding = config.ROUNDING.floor
    elif round == config.ROUNDING.round:
        config.eralng_rounding = config.ROUNDING.round


# event handler for erlang max phase
def er_max_phase_change(phase: int) -> None:
    max_phase = phase
    if max_phase < 1:
        max_phase = 1
    config.erlang_max_phase = max_phase
