# handlers for samples

from ast import Tuple
import logging
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from . import config
from .plot_handler import gen_hist, gen_sa_cdf

logger = logging.getLogger(__name__)

# upload samples and draw histogram
def upload_samples(filepath: str):
    samples = _read_samples(filepath)
    if samples is None:
        return None
    return gen_hist(samples), gen_sa_cdf(samples)


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
    selected_samples = _select_sample(samples)
    return selected_samples


def _select_sample(samples) -> NDArray:
    res = np.squeeze(samples)
    num_sample = config.total_sample
    num_sample = min(num_sample, res.size)

    res = res[: int(num_sample)]
    config.selected_samples = res
    return res


# event handler for sample number
def sample_num_change(num: int):
    config.total_sample = num
    _select_sample(config.samples)



