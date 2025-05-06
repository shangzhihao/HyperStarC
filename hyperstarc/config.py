import enum

from numpy.typing import NDArray
import matplotlib.pyplot as plt


from dataclasses import dataclass

msg_duration = 5

# plot
no_fig, ax = plt.subplots()
ax.text(
    0.5,
    0.5,
    "nothing to show",
    fontsize=20,
    ha="center",  # Horizontal alignment
    va="center",
)


# fitter
class FITTERS(enum.Enum):
    Exponential = "Exponential"
    Erlang = "Erlang"
    HyperErlang = "HyperErlang"
    MAP = "MAP"


FITTER_NAMES = [dist.name for dist in FITTERS]


# erlang parameters
class ERMD(enum.Enum):
    MLE = "MLE"
    MOM = "MOM"


ERMD_NAMES = [method.name for method in ERMD]


class ROUNDING(enum.Enum):
    round = "round"
    ceil = "ceil"
    floor = "floor"


RUNDING_NAMES = [rounding.name for rounding in ROUNDING]


@dataclass
class Parameters:
    samples_all: NDArray | None = None
    samples_plot: NDArray | None = None
    samples_plot_num: int = 1000

    draw_hist_bins: int = 200
    draw_max_bins: int = 1000
    draw_min_bins: int = 50
    draw_max_x: int = 0
    draw_min_x: int = 0

    erlang_max_phase: int = 1000
    erlang_method: ERMD = ERMD.MLE
    erlang_rounding: ROUNDING = ROUNDING.round

    fitter_selected: FITTERS = FITTERS.Exponential
