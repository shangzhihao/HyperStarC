import logging

from . import config
from .config import Parameters

logger = logging.getLogger(__name__)


# event handler for erlang fit method
def er_fit_md_change(fit_method: str, params: Parameters) -> Parameters:
    ermd = config.ERMD(fit_method)
    params.erlang_method = ermd
    return params


# event handler for erlang rounding method
def er_round_change(rounding: str, params: Parameters) -> Parameters:
    round = config.ROUNDING(rounding)
    params.erlang_rounding = round
    return params


# event handler for erlang max phase
def er_max_phase_change(phase: int, params: Parameters) -> Parameters:
    max_phase = phase
    if max_phase < 1:
        max_phase = 1
    params.erlang_max_phase = max_phase
    return params
