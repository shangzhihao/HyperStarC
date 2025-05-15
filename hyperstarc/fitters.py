from abc import ABC, abstractmethod

import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import KMeans

from .config import ERMD, ROUNDING
from .dist import AbcPhDist, Erlang, Exponential, HyperErlang, HyperErlangBranch
from . import config


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

    # fit an exponential distribution
    def _fit(self, samples: NDArray) -> AbcPhDist:
        rate = float(np.mean(samples))
        return Exponential(1 / rate)


class ErlangFitter(Fitter):
    def __init__(
        self,
        method: ERMD = ERMD.MLE,
        rounding: ROUNDING = ROUNDING.round,
        max_phase=config.default_param.erlang_max_phase,
    ) -> None:
        super().__init__()
        self.method = method
        self.rounding = rounding
        self.max_phase = max_phase

    def _fit(self, samples: NDArray) -> AbcPhDist:
        if self.method == ERMD.MLE:
            return self._mle_fit(samples)
        elif self.method == ERMD.MOM:
            return self._mom_fit(samples)
        else:
            raise ValueError("fitter must be 'mle' or 'mom'")

    # fit an erlang distribution by moments method
    def _mom_fit(self, samples: NDArray) -> AbcPhDist:
        sample_mean = np.mean(samples)
        if self.rounding == ROUNDING.ceil:
            phase = np.ceil(self._mom_calc_phase(samples))
        elif self.rounding == ROUNDING.floor:
            phase = np.floor(self._mom_calc_phase(samples))
        else:
            phase = np.round(self._mom_calc_phase(samples))
        rate = float(phase / sample_mean)
        return Erlang(rate, int(phase))

    # fit an erlang distribution by maximum likelihood estimation
    def _mle_fit(self, samples: NDArray) -> AbcPhDist:
        sample_mean = np.mean(samples)
        if self.rounding == ROUNDING.ceil:
            phase = np.ceil(self._mle_calc_phase(samples))
        elif self.rounding == ROUNDING.floor:
            phase = np.floor(self._mle_calc_phase(samples))
        else:
            phase = np.round(self._mle_calc_phase(samples))
        rate = float(phase / sample_mean)
        return Erlang(rate, int(phase))

    # calculate phase by moments method
    def _mom_calc_phase(self, samples: NDArray) -> float:
        sample_mean = np.mean(samples)
        sample_var = np.var(samples)
        if sample_var == 0:
            sample_var = np.finfo(float).eps
        phase = (sample_mean**2) / sample_var
        if phase > self.max_phase:
            phase = self.max_phase
        return float(phase)

    # calculate phase by moments method
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
    def __init__(
        self,
        peaks: int = config.default_param.herlang_peaks,
        method: ERMD = ERMD.MLE,
        rounding: ROUNDING = ROUNDING.round,
        max_phase=config.default_param.herlang_max_phase,
    ) -> None:
        super().__init__()
        self.peaks = peaks
        self.method = method
        self.rounding = rounding
        self.max_phase = max_phase
        self.erlang_fitter = ErlangFitter(
            method=self.method,
            rounding=self.rounding,
            max_phase=self.max_phase,)

    def _fit(self, samples: NDArray) -> AbcPhDist:
        n_clusters = self.peaks
        sam_2d = samples.reshape(-1, 1)
        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(sam_2d)
        erlang_branches = []
        for i in range(n_clusters):
            cluster_i = sam_2d[kmeans.labels_ == i]
            cluster_i = cluster_i.reshape(-1)
            erlang_dist = self.erlang_fitter.fit(cluster_i)
            prob = cluster_i.size / samples.size
            branch = HyperErlangBranch(erlang_dist, prob=prob)
            erlang_branches.append(branch)
        return HyperErlang(erlang_branches)

class MAPFitter(Fitter):
    def __init__(self) -> None:
        super().__init__()

    def _fit(self, samples: NDArray) -> AbcPhDist:
        pass
