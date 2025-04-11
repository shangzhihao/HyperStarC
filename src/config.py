import enum
from numpy.typing import NDArray

samples: NDArray|None = None
class FITTERS(enum.Enum):
    Exponential = "Exponential"
    Erlang = "Erlang"
    HyperErlang = "HyperErlang"
    MAP = "MAP"
FITTER_NAMES = [dist.name for dist in FITTERS]
selected_fitter = FITTERS.Exponential
sample_percent = 100
total_sample = 1000
hist_bins = 100
