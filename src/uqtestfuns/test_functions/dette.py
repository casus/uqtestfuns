"""
Module with an implementation of the functions from Dette and Pepelyshev (2010)

The paper by Dette and Pepelyshev [1] contains several analytical test
functions used to compare different experimental designs for metamodeling
applications.

References
----------

1. H. Dette and A. Pepelyshev, “Generalized Latin Hypercube Design for Computer
   Experiments,” Technometrics, vol. 52, no. 4, pp. 421–429, 2010.
   DOI: 10.1198/TECH.2010.09157.
"""

import numpy as np

from uqtestfuns.core.custom_typing import ProbInputSpecs
from uqtestfuns.core.uqtestfun_abc import UQTestFunFixDimABC

__all__ = ["DetteExp"]


def evaluate_exp(xx: np.ndarray) -> np.ndarray:
    """Evaluate the exponential function from Dette and Pepelyshev (2010).

    Parameters
    ----------
    xx : np.ndarray
        M-Dimensional input values given by an N-by-3 array where
        N is the number of input values.

    Returns
    -------
    np.ndarray
        The output of the test function evaluated on the input values.
        The output is a 1-dimensional array of length N.
    """
    yy = np.sum(np.exp(-2 / xx ** ([1.75, 1.5, 1.25])), axis=1)

    return 100 * yy


class DetteExp(UQTestFunFixDimABC):
    """A concrete implementation of the exponential function."""

    _tags = ["metamodeling"]
    _description = "Exponential function from Dette and Pepelyshev (2010)"
    _available_inputs: ProbInputSpecs = {
        "Dette2010": {
            "function_id": "DetteExp",
            "description": (
                "Input specification for the exponential test function "
                "from Dette and Pepelyshev et al. (2010)"
            ),
            "marginals": [
                {
                    "name": f"x_{i + 1}",
                    "distribution": "uniform",
                    "parameters": [0, 1],
                    "description": None,
                }
                for i in range(3)
            ],
            "copulas": None,
        },
    }
    _available_parameters = None

    evaluate = staticmethod(evaluate_exp)  # type: ignore