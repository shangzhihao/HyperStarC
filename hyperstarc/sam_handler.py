# handlers for samples

import logging
from pathlib import Path

import gradio as gr
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from . import config
from .config import Parameters
from .plot_handler import gen_hist, gen_sa_cdf

logger = logging.getLogger(__name__)

# upload samples and draw histogram


# read samples from given file path
def _read_samples(filepath: str) -> NDArray | None:
    if not Path(filepath).is_file():
        logging.error("file not found")
        raise gr.Error("file not found", duration=config.msg_duration)
    try:
        samples = np.squeeze(np.loadtxt(filepath))
    except (IOError, OSError) as e:
        logging.error(f"Error loading file: {e}")
        raise gr.Error("cannot loading", duration=config.msg_duration)
    except ValueError as e:
        logging.error(f"Error in file format: {e}")
        gr.Warning("bad file format", duration=config.msg_duration)
        return None
    except Exception:
        raise gr.Error("errors in server", duration=config.msg_duration)
    if samples.ndim != 1:
        samples = samples[:, 0]
        logger.warning("samples is not 1-dimentional, the 1st column will be used")
        gr.Warning("the 1st column will be used", duration=config.msg_duration)
    return samples


def _select_sample(samples: NDArray | None, num: int) -> NDArray | None:
    if samples is None:
        return None
    res = np.squeeze(samples)
    num_sample = num
    num_sample = min(num_sample, res.size)
    np.random.shuffle(res)
    res = res[: int(num_sample)]
    return res


def upload_samples(
    filepath: str, params: Parameters
) -> tuple[Figure, Figure, Parameters]:
    samples = _read_samples(filepath)
    if samples is None:
        return config.no_fig, config.no_fig, params
    samples_plot = _select_sample(samples, params.samples_plot_num)
    if samples_plot is None:
        return config.no_fig, config.no_fig, params
    params.samples_all = samples
    params.samples_plot = samples_plot
    return gen_hist(samples, params), gen_sa_cdf(samples, params), params


# event handler for sample number
def sample_num_change(num: int, params: Parameters) -> Parameters:
    params.samples_plot_num = num
    params.samples_plot = _select_sample(params.samples_all, num)
    return params
