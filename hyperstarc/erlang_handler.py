import logging

from gradio import State
from .config import Parameters

from . import config

logger = logging.getLogger(__name__)
# event handler for erlang fit method
def er_fit_md_change(fit_method: str, params:Parameters) -> Parameters:
    ermd = config.ERMD(fit_method)
    if ermd == config.ERMD.MOM:
        params.erlang_method = config.ERMD.MOM
    elif ermd == config.ERMD.MLE:
        params.erlang_method = config.ERMD.MLE
    return params



# event handler for erlang rounding method
def er_round_change(rounding: str, params: Parameters) -> Parameters:
    round = config.ROUNDING(rounding)
    if round == config.ROUNDING.ceil:
        params.erlang_rounding = config.ROUNDING.ceil
    elif round == config.ROUNDING.floor:
        params.erlang_rounding = config.ROUNDING.floor
    elif round == config.ROUNDING.round:
        params.erlang_rounding = config.ROUNDING.round
    return params


# event handler for erlang max phase
def er_max_phase_change(phase: int, params: Parameters) -> Parameters:
    max_phase = phase
    if max_phase < 1:
        max_phase = 1
    params.erlang_max_phase = max_phase
    return params