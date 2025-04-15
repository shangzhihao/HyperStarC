import enum

from numpy.typing import NDArray

# samples
samples: NDArray | None = None
sample_percent = 100
total_sample = 1000


# fitter
class FITTERS(enum.Enum):
    Exponential = "Exponential"
    Erlang = "Erlang"
    HyperErlang = "HyperErlang"
    MAP = "MAP"


FITTER_NAMES = [dist.name for dist in FITTERS]
selected_fitter = FITTERS.Exponential

# draw
hist_bins = 200


# erlang parameters
class ERMD(enum.Enum):
    MLE = "mle"
    MOM = "mom"


class ROUNDING(enum.Enum):
    round = "round"
    ceil = "ceil"
    floor = "floor"


RUNDING_NAMES = [rounding.name for rounding in ROUNDING]
ERMD_NAMES = [method.name for method in ERMD]

erlang_max_phase = 1000
erlang_method: ERMD = ERMD.MLE
eralng_rounding: ROUNDING = ROUNDING.round
