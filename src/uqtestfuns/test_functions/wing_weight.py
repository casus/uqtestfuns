"""
Module with an implementation of Wing Weight test function.

The Wing Weight test function[1] is a 10-dimensional scalar-valued function
that models a light aircraft wing.

References
----------

[1] A. I. J. Forrester, A. Sóbester, and A. J. Keane, Engineering Design
    via Surrogate Modelling: A Practical Guide, 1st ed. Wiley, 2008.
    doi: 10.1002/9780470770801.
"""
import numpy as np

from ..core import UQTestFun
from ..core import MultivariateInput
from .utils import deg2rad


__all__ = ["WingWeight"]

# Define the default input of the Wing Weight test function
DEFAULT_INPUT_DICTS = [
    {
        "name": "Sw",
        "distribution": "uniform",
        "parameters": [150, 200],
        "description": "wing area [ft^2]"
    },
    {
        "name": "Wfw",
        "distribution": "uniform",
        "parameters": [220, 300],
        "description": "weight of fuel in the wing [lb]"
    },
    {
        "name": "A",
        "distribution": "uniform",
        "parameters": [6, 10],
        "description": "aspect ratio [-]"
    },
    {
        "name": "Lambda",
        "distribution": "uniform",
        "parameters": [-10, 10],
        "description": "quarter-chord sweep [degrees]"
    },
    {
        "name": "q",
        "distribution": "uniform",
        "parameters": [16, 45],
        "description": "dynamic pressure at cruise [lb/ft^2]"
    },
    {
        "name": "lambda",
        "distribution": "uniform",
        "parameters": [0.5, 1.0],
        "description": "taper ratio [-]"
    },
    {
        "name": "tc",
        "distribution": "uniform",
        "parameters": [0.08, 0.18],
        "description": "aerofoil thickness to chord ratio [-]"
    },
    {
        "name": "Nz",
        "distribution": "uniform",
        "parameters": [2.5, 6.0],
        "description": "ultimate load factor [-]"
    },
    {
        "name": "Wdg",
        "distribution": "uniform",
        "parameters": [1700, 2500],
        "description": "flight design gross weight [lb]"
    },
    {
        "name": "Wp",
        "distribution": "uniform",
        "parameters": [0.025, 0.08],
        "description": "paint weight [lb/ft^2]"
    }
]

DEFAULT_INPUT = MultivariateInput(DEFAULT_INPUT_DICTS)


class WingWeight(UQTestFun):
    """Implementation of the Wing Weight test function.

    Parameters
    ----------
    input : MultivariateInput
        MultivariateInput instance that specifies 10-dimensional probabilistic
        input model for the Wing Weight function.

    Attributes
    ----------
    input : MultivariateInput
        Probabilistic input of the test function.
    spatial_dimension : int
        Number of input variables of the test function.
    """

    def __init__(self, input: MultivariateInput = DEFAULT_INPUT):
        if not isinstance(input, MultivariateInput):
            raise TypeError("Input must be MultivariateInput type!")
        if input.spatial_dimension != DEFAULT_INPUT.spatial_dimension:
            raise ValueError("Input dimensionality is inconsistent! "
                             f"Expected {DEFAULT_INPUT.spatial_dimension}, "
                             f"but got {input.spatial_dimension}.")

        self._spatial_dimension = DEFAULT_INPUT.spatial_dimension
        self.input = DEFAULT_INPUT

    def evaluate(self, xx: np.ndarray) -> np.ndarray:
        """Evaluate the Wing Weight function on a set of input values.

        Parameters
        ----------
        xx : np.ndarray
            10-Dimensional input values given by N-by-10 arrays where
            N is the number of input values.
        """
        if xx.shape[1] != self.spatial_dimension:
            raise ValueError(
                f"Wrong dimensionality of the input array!"
                f"Expected {self.spatial_dimension}, got {xx.shape[1]}."
            )

        term_1 = 0.036 * xx[:, 0]**0.758 * xx[:, 1]**0.0035
        term_2 = (xx[:, 2] / np.cos(deg2rad(xx[:, 3]))**2)**0.6
        term_3 = xx[:, 4]**0.006
        term_4 = xx[:, 5]**0.04
        term_5 = (100 * xx[:, 6] / np.cos(np.pi / 180.0 * xx[:, 3]))**(-0.3)
        term_6 = (xx[:, 7] * xx[:, 8])**0.49
        term_7 = xx[:, 0] * xx[:, 9]

        yy = term_1 * term_2 * term_3 * term_4 * term_5 * term_6 + term_7

        return yy
