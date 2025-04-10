from abc import ABC, abstractmethod
from typing import Literal
import numpy as np
from numpy.typing import NDArray

from .dist import AbcPhDist, Erlang, HyperErlang, MAP, Exponential


class Fitter(ABC):
    def __init__(self) -> None:
        super().__init__()

    def fit(self, samples: NDArray) -> AbcPhDist:
        if samples.ndim != 1:
            raise ValueError("samples must be 1-dimentional")
        return self._fit(samples)

    @abstractmethod
    def _fit(self, samples: NDArray) -> AbcPhDist:
        pass


class ExponentialFitter(Fitter):
    def __init__(self) -> None:
        super().__init__()

    def _fit(self, samples: NDArray) -> AbcPhDist:
        rate = float(np.mean(samples))
        return Exponential(rate)


class ErlangFitter(Fitter):
    def __init__(
        self,
        fitter: Literal["mle", "mom"] = "mle",
        mle_floor: bool = True,
        max_phase=1000,
    ) -> None:
        super().__init__()
        self.fitter = fitter
        self.mle_floor = mle_floor
        self.max_phase = max_phase

    def _fit(self, samples: NDArray) -> AbcPhDist:
        if self.fitter == "mle":
            if self.mle_floor:
                return self._mle_fit_floor(samples)
            else:
                return self._mle_fit_ceil(samples)
        elif self.fitter == "mom":
            if self.mle_floor:
                return self._mom_fit_floor(samples)
            else:
                return self._mom_fit_ceil(samples)
        else:
            raise ValueError("fitter must be 'mle' or 'mom'")

    def _mom_fit_floor(self, samples: NDArray) -> AbcPhDist:
        sample_mean = np.mean(samples)
        phase = np.floor(self._mom_calc_phase(samples))
        rate = float(phase / sample_mean)
        return Erlang(rate, phase)

    def _mom_fit_ceil(self, samples: NDArray) -> AbcPhDist:
        sample_mean = np.mean(samples)
        phase = np.ceil(self._mom_calc_phase(samples))

        rate = float(phase / sample_mean)
        return Erlang(rate, phase)

    def _mle_fit_floor(self, samples: NDArray) -> AbcPhDist:
        sample_mean = np.mean(samples)
        phase = np.floor(self._mle_calc_phase(samples))
        rate = float(phase / sample_mean)
        return Erlang(rate, phase)

    def _mle_fit_ceil(self, samples: NDArray) -> AbcPhDist:
        sample_mean = np.mean(samples)
        phase = np.ceil(self._mle_calc_phase(samples))

        rate = float(phase / sample_mean)
        return Erlang(rate, phase)

    def _mom_calc_phase(self, samples: NDArray) -> float:
        sample_mean = np.mean(samples)
        sample_var = np.var(samples)
        if sample_var == 0:
            sample_var = np.finfo(float).eps
        phase = (sample_mean**2) / sample_var
        if phase > self.max_phase:
            phase = self.max_phase
        return float(phase)

    # see https://en.wikipedia.org/wiki/Gamma_distribution#Maximum_likelihood_estimation
    def _mle_calc_phase(self, samples: NDArray) -> float:
        if samples.ndim != 1:
            raise ValueError("samples must be 1-dimentional")
        log_mean = np.log(np.mean(samples))
        mean_log = sum(map(np.log, samples)) / samples.size
        s = log_mean - mean_log
        res = (s - 3) ** 2 + 24 * s
        res = np.sqrt(res) + 3 - s
        res = res / (12 * s)
        if res > self.max_phase:
            res = self.max_phase
        return res


class HyperErlangFitter(Fitter):
    def __init__(self) -> None:
        super().__init__()

    def _fit(self, samples: NDArray) -> AbcPhDist:
        pass


class MAPFitter(Fitter):
    def __init__(self) -> None:
        super().__init__()

    def _fit(self, samples: NDArray) -> AbcPhDist:
        pass
