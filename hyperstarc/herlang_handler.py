import logging

from . import config
from .config import Parameters

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


def her_peaks_change(peaks: int, params: Parameters) -> Parameters:
    params.herlang_peaks = peaks
    logger.debug(f"herlang_peaks: {params.herlang_peaks}")
    return params


def her_fit_md_change(fit_method: str, params: Parameters) -> Parameters:
    hermd = config.ERMD(fit_method)
    params.herlang_method = hermd
    logger.debug(f"herlang_method: {params.herlang_method}")
    return params


# event handler for hyper-erlang rounding method
def her_round_change(rounding: str, params: Parameters) -> Parameters:
    round = config.ROUNDING(rounding)
    params.herlang_rounding = round
    logger.debug(f"herlang_rounding: {params.herlang_rounding}")
    return params


def her_max_phase_change(phase: int, params: Parameters) -> Parameters:
    max_phase = phase
    if max_phase < 1:
        max_phase = 1
    params.herlang_max_phase = max_phase
    logger.debug(f"herlang_max_phase: {params.herlang_max_phase}")
    return params
