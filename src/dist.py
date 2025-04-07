from abc import ABC, abstractmethod
from typing import Tuple
from cmath import phase
from functools import reduce
import math
import numpy as np
from numpy.typing import NDArray
from scipy import linalg


class AbcPhDist(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._mean = self.get_moment(1)
        self._variance = self.get_moment(2) - self._mean**2
        self._moments = {}

    def get_mean(self) -> float:
        return self._mean

    def get_var(self) -> float:
        return self._variance

    def get_moment(self, k: int) -> float:
        if k in self._moments:
            return self._moments[k]
        else:
            res = self._calcMoment(k)
            self._moments[k] = res
            return res

    @abstractmethod
    def _calcMoment(self, k: int) -> float:
        pass

    @abstractmethod
    def pdf(self, x: float) -> float:
        pass

    @abstractmethod
    def cdf(self, x: float) -> float:
        pass


class Exponential(AbcPhDist):
    def __init__(self, rate: float) -> None:
        super().__init__()
        self.rate = rate

    def _calcMoment(self, k: int) -> float:
        assert k >= 0
        return math.factorial(k) / self.rate**k

    def pdf(self, x: float) -> float:
        assert x >= 0
        return self.rate * math.exp(-self.rate * x)

    def cdf(self, x: float) -> float:
        assert x >= 0
        return 1 - math.exp(-self.rate * x)


# erlang distribution with phase parameter and rate parameter
# peak = (phase-1)*rate
# rate = mean/var
# phase = mean*rate
class Erlang(AbcPhDist):
    def __init__(self, rate: float, phase: int):
        self.rate = rate
        self.phase = phase

    def _calcMoment(self, k: int) -> float:
        res = math.prod(range(self.phase, self.phase + k))
        res /= self.rate**self.phase
        return res

    def pdf(self, x: float) -> float:
        x1 = self.rate**self.phase
        x2 = x ** (self.phase - 1)
        x3 = math.exp(-self.rate * x)
        return x1 * x2 * x3 / math.factorial(self.phase - 1)

    def cdf(self, x: float) -> float:
        res = 0
        for i in range(self.phase):
            x1 = (self.rate * x) ** i
            x2 = math.exp(-self.rate * x)
            res += x1 * x2 / math.factorial(i)
        return 1 - res

    def get_trans_matrix(self) -> NDArray:
        res = np.zeros((self.phase, self.phase))
        for i in range(self.phase):
            res[i, i] = -self.rate
            res[i, i + 1] = self.rate
        return res


class HyperErlangBranch:
    def __init__(self, dist: Erlang, prob: float):
        self.erlang = dist
        self.prob = prob


# Hyper-Erlang distribution
# see https://en.wikipedia.org/wiki/Hyper-Erlang_distribution
class HyperErlang(AbcPhDist):
    def __init__(self, branches: list[HyperErlangBranch]):
        self.branches = branches
        self.phase = self._get_phase()

    def _get_phase(self) -> int:
        return sum(branch.erlang.phase for branch in self.branches)

    def get_alpha(self) -> NDArray:
        res = np.zeros(self.phase)
        pos = 0
        for branch in self.branches:
            res[pos] = branch.prob
            pos += branch.erlang.phase
        return res

    def get_trans_matrix(self) -> NDArray:
        res = np.zeros((self.phase, self.phase))
        pos = 0
        for branch in self.branches:
            k = branch.erlang.phase
            res[pos : pos + k, pos : pos + k] = branch.erlang.get_trans_matrix()
            pos += k
        return res

    def _calcMoment(self, k: int) -> float:
        trans = self.get_trans_matrix()
        dim = trans.shape[0]
        d0inv = np.linalg.inv(-trans)
        res = self.get_alpha()
        res *= d0inv**k
        res *= np.ones((dim, 1))
        res = math.factorial(k)
        return res

    def pdf(self, x: float) -> float:
        res = 0.0
        for branch in self.branches:
            res += branch.erlang.pdf(x) * branch.prob
        return res

    def cdf(self, x: float) -> float:
        res = 0.0
        for branch in self.branches:
            res += branch.erlang.cdf(x)
        return 1 - res

    def cdfBranch(self, branch: HyperErlangBranch, x: float) -> float:
        temp, res = 0.0, 0.0
        for i in range(branch.erlang.phase):
            temp = branch.erlang.rate * x
            temp = temp**i
            temp = temp * math.exp(-branch.erlang.rate * x)
            temp = temp / math.factorial(i)
            res = res + temp
        return res * branch.prob


class MAP(AbcPhDist):
    def __init__(self, d0: NDArray, d1: NDArray):
        assert len(d0.shape) == 2
        assert d0.shape == d1.shape
        self._d0 = d0
        self._d1 = d1
        self._dim = d0.shape[0]
        # for computing
        self._d0inv = np.linalg.inv(d0)
        # embedded process
        self._P = self._d0inv @ d1
        # steady probability of P
        # TODO : check if P is stable
        self._limit_prob = self._P**1000

    def _calcMoment(self, k: int) -> float:
        res = self._limit_prob @ (self._d0inv**k) @ np.ones((self._dim, 1))
        res = res * math.factorial(k)
        return res[0, 0]

    def get_trans_matrix(self) -> Tuple[NDArray, NDArray]:
        return (self._d0, self._d1)

    def get_limit_prob(self) -> NDArray:
        return self._limit_prob

    def pdf(self, x: float) -> float:
        res = -self._d0 @ np.ones((self._dim, 1))
        res = self._limit_prob @ (linalg.expm(self._d0 * x)) @ res
        return res[0, 0]

    def cdf(self, x: float) -> float:
        res = self._limit_prob @ (linalg.expm(self._d0 * x)) @ np.ones((self._dim, 1))
        res = 1 - res[0, 0]
        return res

    def acf(self, k: int) -> float:
        m_mean = (
            self._limit_prob
            @ self._d0inv
            @ (self._P**k)
            @ self._d0inv
            * np.ones((self._dim, 1))
        )
        cov = m_mean[0, 0] - self.get_mean() ** 2
        return cov / self.get_var()
