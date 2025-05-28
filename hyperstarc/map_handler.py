import logging

from . import config
from .config import Parameters

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


def map_peaks_change(peaks: int, params: Parameters) -> Parameters:
    params.map_peaks = peaks
    logger.debug(f"map_peaks: {params.map_peaks}")
    return params


def map_fit_md_change(fit_method: str, params: Parameters) -> Parameters:
    mapmd = config.ERMD(fit_method)
    params.map_method = mapmd
    logger.debug(f"map_method: {params.map_method}")
    return params


# event handler for hyper-erlang rounding method
def map_round_change(rounding: str, params: Parameters) -> Parameters:
    round = config.ROUNDING(rounding)
    params.map_rounding = round
    logger.debug(f"map_rounding: {params.map_rounding}")
    return params


def map_max_phase_change(phase: int, params: Parameters) -> Parameters:
    max_phase = phase
    if max_phase < 1:
        max_phase = 1
    params.map_max_phase = max_phase
    logger.debug(f"map_max_phase: {params.map_max_phase}")
    return params
