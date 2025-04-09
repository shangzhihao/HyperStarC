from abc import ABC, abstractmethod

from numpy.typing import NDArray

from .dist import AbcPhDist


class Fitter(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.fit_res = None
        self._llh = -1

    @abstractmethod
    def fit(self, samples: NDArray)->AbcPhDist:
        pass

#    def calc_llh(self)->float:
