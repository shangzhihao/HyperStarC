import logging

import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from . import config
from .fitters import ErlangFitter, ExponentialFitter, Fitter
from .plot_handler import gen_hist

logger = logging.getLogger(__name__)


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
    if fig is None:
        return None
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

