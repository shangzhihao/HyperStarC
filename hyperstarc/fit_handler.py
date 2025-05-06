import logging

import gradio as gr
from gradio import State
import numpy as np
from matplotlib.figure import Figure

from . import config
from .config import Parameters
from .fitters import ErlangFitter, ExponentialFitter, Fitter
from .plot_handler import gen_hist, gen_sa_cdf

logger = logging.getLogger(__name__)


# event handler for fit button
def fit_click(params: State)->tuple[Figure, Figure]:
    no_figs = (config.no_fig, config.no_fig)
    if params["sample.selected"] is None:
        logger.error("No samples loaded")
        return no_figs
    fitter = make_fitter(params)
    if fitter is None:
        logger.error("No fitter selected")
        gr.Warning("No fitter selected")
        return no_figs
    dist = fitter.fit(config.selected_samples)
    pdf_fig = gen_hist(config.selected_samples)
    cdf_fig = gen_sa_cdf(config.selected_samples)
    smp_min = np.min(config.selected_samples)
    smp_max = np.max(config.selected_samples)
    x = np.linspace(smp_min, smp_max, 100)
    if pdf_fig is not None:
        y = [dist.pdf(i) for i in x]
        ax2 = pdf_fig.axes[0].twinx()
        ax2.plot(x, y, color="blue")
        ax2.set_ylabel("pdf", color="blue")
        pdf_fig.tight_layout()
    if cdf_fig is not None:
        y = [dist.cdf(i) for i in x]
        ax2 = cdf_fig.axes[0].twinx()
        ax2.plot(x, y, color="blue")
        ax2.set_ylabel("cdf", color="blue")
        cdf_fig.tight_layout()
    return pdf_fig, cdf_fig


# Update ui based on selected fitter
def fitter_change(fitter: str, params: Parameters)->tuple[list, Parameters]:
    res = [gr.update(visible=False) for _ in config.FITTER_NAMES]
    if fitter not in config.FITTER_NAMES:
        return res, params
    idx = config.FITTER_NAMES.index(fitter)
    res[idx] = gr.update(visible=True)
    params.fitter_selected = config.FITTERS(fitter)
    return res, params



# generate fitter object based on selected fitter
def make_fitter(params: Parameters) -> Fitter | None:
    if params.fitter_selected == config.FITTERS.Exponential:
        return ExponentialFitter()
    if params.fitter_selected == config.FITTERS.Erlang:
        return ErlangFitter(
            method=params.erlang_method,
            rounding=params.erlang_rounding,
            max_phase=params.erlang_max_phase,
        )
    return None

