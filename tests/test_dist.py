import numpy as np
import pytest
from src.dist import Exponential, Erlang, HyperErlang, HyperErlangBranch, MAP
from scipy.stats import erlang

def test_exponential():
    lam = 2.0
    dist = Exponential(rate=lam)
    assert dist.pdf(0.0) == pytest.approx(lam)
    assert dist.cdf(0.0) == 0.0
    assert dist.get_mean() == pytest.approx(1 / lam)
    assert dist.get_var() == pytest.approx(1 / lam**2)

def test_erlang():
    rate = 3.0
    phase = 2
    dist = Erlang(rate=rate, phase=phase)
    x = 5.0
    y = dist.pdf(x)
    # a: shape, loc: shift, scale: 1/rate
    y_exp = erlang.pdf(x=x, a=phase, loc=0, scale=1/rate)
    y = dist.cdf(x)
    y_exp = erlang.cdf(x=x, a=phase, loc=0, scale=1/rate)
    assert y == pytest.approx(y_exp)
    
    assert dist.get_mean() == pytest.approx(phase / rate)
    assert dist.get_var() == pytest.approx(phase / rate**2)

def test_hyper_erlang():
    e1 = Erlang(rate=1.0, phase=1)
    e2 = Erlang(rate=2.0, phase=2)
    b1 = HyperErlangBranch(e1, prob=0.4)
    b2 = HyperErlangBranch(e2, prob=0.6)
    dist = HyperErlang([b1, b2])
    assert dist.pdf(0.0) == pytest.approx(b1.erlang.pdf(0.0) * 0.4 + b2.erlang.pdf(0.0) * 0.6)
    assert dist.cdf(0.0) == pytest.approx(0.0)

def test_map():
    D0 = np.array([[-5.0, 2.0],
                   [1.0, -3.0]])
    D1 = np.array([[3.0, 0.0],
                   [0.0, 2.0]])
    dist = MAP(d0=D0, d1=D1)
    assert dist.pdf(0.0) >= 0
    assert 0.0 <= dist.cdf(0.1) <= 1.0
    assert dist.get_mean() > 0
    assert dist.get_var() > 0
    assert isinstance(dist.get_trans_matrix(), tuple)
    assert dist.get_limit_prob().shape == (2, 2)

