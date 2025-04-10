import math
from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np
from numpy.typing import NDArray
from scipy import linalg


class AbcPhDist(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._moments: dict[int, float] = {}

    def get_moment(self, k: int) -> float:
        if k in self._moments:
            return self._moments[k]
        else:
            res = self._calcMoment(k)
            self._moments[k] = res
            return res

    @property
    def mean(self):
        return self.get_moment(1)

    @property
    def var(self):
        return self.get_moment(2) - self.get_moment(1) ** 2

    @abstractmethod
    def _calcMoment(self, k: int) -> float:
        pass

    @abstractmethod
    def pdf(self, x: float) -> float:
        pass

    @abstractmethod
    def cdf(self, x: float) -> float:
        pass

    def llh(self, samples: NDArray) -> float:
        if not np.squeeze(samples).ndim == 1:
            raise ValueError("samples must be 1-dimentional")
        lh = map(self.pdf, samples)
        llh = map(math.log, lh)
        return math.prod(llh)


class Exponential(AbcPhDist):
    def __init__(self, rate: float) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        self.rate = rate
        super().__init__()

    def _calcMoment(self, k: int) -> float:
        if int(k) != k or k < 1:
            raise ValueError("k must be integer and greater than 0")

        return math.factorial(k) / self.rate**k

    # f(x) = \lambda e^{-\lambda x}
    def pdf(self, x: float) -> float:
        res = self.rate * math.exp(-self.rate * x)
        return res * (x >= 0)

    # F(x) = 1 - e^{-\lambda x}
    def cdf(self, x: float) -> float:
        res = 1 - math.exp(-self.rate * x)
        return res * (x >= 0)


# erlang distribution with phase parameter and rate parameter
# peak = (phase-1)*rate
# rate = mean/var
# phase = mean*rate
class Erlang(AbcPhDist):
    def __init__(self, rate: float, phase: int):
        if rate <= 0:
            raise ValueError("rate must be positive")
        if phase <= 0:
            raise ValueError("phase must be positive")
        if int(phase) != phase:
            raise ValueError("phase must be integer")
        self.rate = rate
        self.phase = phase
        super().__init__()

    # \frac{\Gamma(k + r)}{\Gamma(k)}
    # \cdot \frac{1}{\lambda^r}
    def _calcMoment(self, k: int) -> float:
        if int(k) != k or k < 1:
            raise ValueError("k must be integer and greater than 0")
        res: float = math.prod(range(self.phase, self.phase + k))
        res /= self.rate**k
        return res

    # f(x) = \frac{\lambda^k x^{k-1} e^{-\lambda x}}{(k-1)!}
    def pdf(self, x: float) -> float:
        x1 = self.rate**self.phase
        x2 = x ** (self.phase - 1)
        x3 = math.exp(-self.rate * x)
        return x1 * x2 * x3 / math.factorial(self.phase - 1)

    # F(x) = 1 - \sum_{n=0}^{k-1} \frac{(\lambda x)^n}{n!} e^{-\lambda x}
    def cdf(self, x: float) -> float:
        res = 0.0
        for i in range(self.phase):
            x1 = (self.rate * x) ** i
            x2 = math.exp(-self.rate * x)
            res += x1 * x2 / math.factorial(i)
        return 1 - res

    def get_trans_matrix(self) -> NDArray:
        res = np.zeros((self.phase, self.phase))
        for i in range(self.phase - 1):
            res[i, i] = -self.rate
            res[i, i + 1] = self.rate
        res[self.phase - 1, self.phase - 1] = -self.rate
        return res


class HyperErlangBranch:
    def __init__(self, dist: Erlang, prob: float):
        if prob <= 0 or prob >= 1:
            raise ValueError("probiblity of an Erlang branch must be in (0, 1)")
        self.erlang = dist
        self.prob = prob
        super().__init__()


# Hyper-Erlang distribution
# see https://en.wikipedia.org/wiki/Hyper-Erlang_distribution
class HyperErlang(AbcPhDist):
    def __init__(self, branches: list[HyperErlangBranch]):
        self.branches = branches
        self.phase = self.get_phase()
        super().__init__()

    def get_phase(self) -> int:
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
        if int(k) != k or k < 1:
            raise ValueError("k must be integer and greater than 0")

        trans = self.get_trans_matrix()
        dim = trans.shape[0]
        d0inv = np.linalg.inv(-trans)
        res = self.get_alpha()
        res = np.expand_dims(res, -1) * d0inv**k
        res = res @ np.ones((dim, 1))
        return res[0, 0] * math.factorial(k)

    # f(x) = \sum_{i=1}^N p_i \cdot
    # \frac{\lambda_i^{k_i} x^{k_i - 1} e^{-\lambda_i x}}
    # {(k_i - 1)!}
    def pdf(self, x: float) -> float:
        res = 0.0
        for branch in self.branches:
            res += branch.erlang.pdf(x) * branch.prob
        return res

    # F(x) = \sum_{i=1}^N p_i \cdot
    # \left(1 - \sum_{n=0}^{k_i - 1}
    # \frac{(\lambda_i x)^n}{n!}
    # e^{-\lambda_i x} \right)
    def cdf(self, x: float) -> float:
        res = 0.0
        for branch in self.branches:
            res += self.cdf_branch(branch, x)
        return 1 - res

    def cdf_branch(self, branch: HyperErlangBranch, x: float) -> float:
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
        # d0: transition matrix without an arrival
        # d1: transition matrix with an arrival
        if len(d0.shape) != 2:
            raise ValueError("d0 and d1 must be 2-D array")
        if d0.shape != d1.shape:
            raise ValueError("d0 and d1 must have the same shape")

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
        super().__init__()

    def _calcMoment(self, k: int) -> float:
        if int(k) != k or k < 1:
            raise ValueError("k must be integer and greater than 0")

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


if __name__ == "__main__":
    import pytest

    e1 = Erlang(rate=1.0, phase=1)
    e2 = Erlang(rate=2.0, phase=2)
    b1 = HyperErlangBranch(e1, prob=0.4)
    b2 = HyperErlangBranch(e2, prob=0.6)
    dist = HyperErlang([b1, b2])
    assert dist.pdf(0.0) == pytest.approx(
        b1.erlang.pdf(0.0) * 0.4 + b2.erlang.pdf(0.0) * 0.6
    )
    assert dist.cdf(0.0) == pytest.approx(0.0)
