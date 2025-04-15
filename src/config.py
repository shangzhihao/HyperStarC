import enum
from tkinter import ROUND
from numpy.typing import NDArray
from typing import Literal






# samples
samples: NDArray|None = None
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
hist_bins = 100

# erlang parameters
class ERMD(enum.Enum):
    MLE = "mle"
    MOM = "mom"
class ROUNDING(enum.Enum):
    CEIL = "ceil"
    FLOOR = "floor"
    ROUND = "round"

erlang_max_phase = 1000
erlang_method: ERMD = ERMD.MOM
eralng_rounding: ROUNDING = ROUNDING.ROUND
erlang_floor = True