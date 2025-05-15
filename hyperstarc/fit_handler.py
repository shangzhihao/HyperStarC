import logging

import gradio as gr
import numpy as np
from matplotlib.figure import Figure

from . import config
from .config import Parameters
from .fitters import ErlangFitter, ExponentialFitter, Fitter, HyperErlangFitter
from .plot_handler import gen_hist, gen_sa_cdf

logger = logging.getLogger(__name__)


# event handler for fit button
def fit_click(params: Parameters)->tuple[Figure, Figure]:
    no_figs = (config.no_fig, config.no_fig)
    if params.samples_all is None:
        logger.error("No samples loaded")
        return no_figs
    fitter = make_fitter(params)
    if fitter is None:
        logger.error("No fitter selected")
        gr.Warning("No fitter selected")
        return no_figs
    dist = fitter.fit(params.samples_all)
    pdf_fig = gen_hist(params.samples_plot, params)
    cdf_fig = gen_sa_cdf(params.samples_plot, params)
    if params.samples_plot is not None:
        smp_min = np.min(params.samples_plot)
        smp_max = np.max(params.samples_plot)
    else:
        smp_min = np.min(params.samples_all)
        smp_max = np.max(params.samples_all)
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
def fitter_change(fitter: str, params: Parameters)->list:
    res = [gr.update(visible=False) for _ in config.FITTER_NAMES]
    if fitter not in config.FITTER_NAMES:
        res.append(params)
        return res
    idx = config.FITTER_NAMES.index(fitter)
    res[idx] = gr.update(visible=True)
    params.fitter_selected = config.FITTERS(fitter)
    res.append(params)
    return res



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
    if params.fitter_selected == config.FITTERS.HyperErlang:
        return HyperErlangFitter(
            peaks=params.herlang_peaks,
            method=params.herlang_method,
            rounding=params.herlang_rounding,
            max_phase=params.herlang_max_phase,)
    return None

