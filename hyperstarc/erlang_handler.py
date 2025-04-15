import logging


from . import config

logger = logging.getLogger(__name__)
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