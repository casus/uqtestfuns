"""
Module with an implementation of the Sobol-G test function.

The Sobol-G function [1] is an M-dimensional scalar-valued function.
It has been used mainly to test integration algorithms
(e.g., quasi Monte-Carlo) such as in [1] and global sensitivity analysis
such as in [2], [3], and [4].

The parameters of the Sobol-G function (i.e., the weighting coefficients)
determine the importance of each input variable. There are several sets
of parameters used in the literature.

Notes
-----
- The parameters used in [3] and [4] correspond to
  the parameter choice 3 in [1].

References
----------
[1] I. M. Sobol’, “On quasi-Monte Carlo integrations,”
    Mathematics and Computers in Simulation, vol. 47, no. 2–5,
    pp. 103–112, 1998.
    DOI: 10.1016/S0378-4754(98)00096-2.
[2] S. Kucherenko, B. Feil, N. Shah, and W. Mauntz, “The identification of
    model effective dimensions using global sensitivity analysis,”
    Reliability Engineering & System Safety, vol. 96, no. 4, pp. 440–449, 2011.
    DOI: 10.1016/j.ress.2010.11.003.
[3] A. Marrel, B. Iooss, F. Van Dorpe, and E. Volkova, “An efficient
    methodology for modeling complex computer codes with Gaussian processes,”
    Computational Statistics & Data Analysis, vol. 52, no. 10,
    pp. 4731–4744, 2008.
    DOI: 10.1016/j.csda.2008.03.026.
[4] A. Marrel, B. Iooss, B. Laurent, and O. Roustant, “Calculations of Sobol
    indices for the Gaussian process metamodel,”
    Reliability Engineering & System Safety, vol. 94, no. 3,
    pp. 742–751, 2009.
    DOI: 10.1016/j.ress.2008.07.008.
[5] T. Crestaux, J.-M. Martinez, O. Le Maître, and O. Lafitte, “Polynomial
    chaos expansion for uncertainties quantification and sensitivity analysis,”
    presented at the Fifth International Conference on Sensitivity Analysis
    of Model Output, 2007.
    Accessed: Jan. 25, 2023
    URL: http://samo2007.chem.elte.hu/lectures/Crestaux.pdf
"""
import numpy as np

from typing import List, Optional

from ..core.prob_input.univariate_input import UnivariateInput
from ..core.uqtestfun_abc import UQTestFunABC
from .available import (
    create_prob_input_from_available,
    create_parameters_from_available,
)

__all__ = ["SobolG"]


def _create_sobol_input(spatial_dimension: int) -> List[UnivariateInput]:
    """Construct an input instance for a given dimension according to [1].

    Parameters
    ----------
    spatial_dimension : int
        The number of marginals to be created.

    Returns
    -------
    List[UnivariateInput]
        A list of M marginals as UnivariateInput instances to construct
        the MultivariateInput.
    """
    marginals = []
    for i in range(spatial_dimension):
        marginals.append(
            UnivariateInput(
                name=f"X{i + 1}",
                distribution="uniform",
                parameters=[0.0, 1.0],
                description="None",
            )
        )

    return marginals


AVAILABLE_INPUT_SPECS = {
    "sobol": {
        "name": "Sobol-G",
        "description": (
            "Probabilistic input model for the Sobol'-G function "
            "from Sobol' (1998)."
        ),
        "marginals": _create_sobol_input,
        "copulas": None,
    },
}

DEFAULT_INPUT_SELECTION = "sobol"


def _get_params_sobol_1(spatial_dimension: int) -> np.ndarray:
    """Construct a parameter array for Sobol-G according to choice 1 in [1].

    Notes
    -----
    - Using this choice of parameters, the supremum of the Sobol-G function
      grows exponentially as a function of dimension about 2^M [1].
    """
    yy = 0.01 * np.ones(spatial_dimension)

    return yy


def _get_params_sobol_2(spatial_dimension: int) -> np.ndarray:
    """Construct a parameter array for Sobol-G according to choice 2 in [1].

    Notes
    -----
    - Using this choice of parameters, the supremum of the Sobol-G function
      grows exponentially as a function of dimension about (1.5)^M [1];
      it's a bit slower than choice 1.
    """
    yy = np.ones(spatial_dimension)

    return yy


def _get_params_sobol_3(spatial_dimension: int) -> np.ndarray:
    """Construct a parameter array for Sobol-G according to choice 3 in [1].

    Notes
    -----
    - Using this choice of parameters, the supremum of the Sobol-G function
      grows linearly as a function of dimension, i.e., 1 + (M/2) [1].
    """
    yy = np.arange(1, spatial_dimension + 1)

    return yy


def _get_params_sobol_4(spatial_dimension: int) -> np.ndarray:
    """Construct a parameter array for Sobol-G according to choice 4 in [1].

    Notes
    -----
    - Using this choice of parameters, the supremum of the Sobol-G function
      is bounded at 1.0 [1].
    """
    yy = np.arange(1, spatial_dimension + 1) ** 2

    return yy


def _get_params_kucherenko_2a(spatial_dimension: int) -> np.ndarray:
    """Construct a param. array for Sobol-G according to problem 2A in [2]."""
    yy = np.zeros(spatial_dimension)
    if spatial_dimension >= 2:
        yy[2:] = 6.52

    return yy


def _get_params_kucherenko_3b(spatial_dimension: int) -> np.ndarray:
    """Construct a parameter array for Sobol-G according to problem 3B in [2].

    Notes
    -----
    - Using this choice of parameters, the supremum of the Sobol-G function
      grows exponentially as a function of dimension about (1.13)^M.
    """
    yy = 6.52 * np.ones(spatial_dimension)

    return yy


def _get_params_crestaux_2007(spatial_dimension: int) -> np.ndarray:
    """Construct a parameter array for Sobol-G according to [3]."""
    yy = (np.arange(1, spatial_dimension + 1) - 1) / 2.0

    return yy


AVAILABLE_PARAMETERS = {
    "sobol-1": _get_params_sobol_1,
    "sobol-2": _get_params_sobol_2,
    "sobol-3": _get_params_sobol_3,
    "sobol-4": _get_params_sobol_4,
    "kucherenko-2a": _get_params_kucherenko_2a,
    "kucherenko-3b": _get_params_kucherenko_3b,
    "crestaux-2007": _get_params_crestaux_2007,
}

DEFAULT_PARAMETERS_SELECTION = "crestaux-2007"

# The dimension is variable, it requires a default for fallback
DEFAULT_DIMENSION_SELECTION = 2


class SobolG(UQTestFunABC):
    """A concrete implementation of the M-dimensional Sobol'-G function."""

    tags = ["sensitivity-analysis"]

    available_inputs = tuple(AVAILABLE_INPUT_SPECS.keys())

    available_parameters = tuple(AVAILABLE_PARAMETERS.keys())

    default_dimension = None

    def __init__(
        self,
        spatial_dimension: int = DEFAULT_DIMENSION_SELECTION,
        *,
        prob_input_selection: Optional[str] = DEFAULT_INPUT_SELECTION,
        parameters_selection: Optional[str] = DEFAULT_PARAMETERS_SELECTION,
    ):
        # --- Arguments processing
        if not isinstance(spatial_dimension, int):
            raise TypeError(
                f"Spatial dimension is expected to be of 'int'. "
                f"Got {type(spatial_dimension):!r} instead."
            )
        # Sobol-G is an M-dimensional test function, either given / use default
        # Create the input according to spatial dimension
        prob_input = create_prob_input_from_available(
            prob_input_selection, AVAILABLE_INPUT_SPECS, spatial_dimension
        )
        # Create the parameters according to spatial dimension
        parameters = create_parameters_from_available(
            parameters_selection, AVAILABLE_PARAMETERS, spatial_dimension
        )

        super().__init__(
            prob_input=prob_input, parameters=parameters, name=SobolG.__name__
        )

    def evaluate(self, xx: np.ndarray):
        """Evaluate the Sobol-G function on a set of input values.

        Parameters
        ----------
        xx : np.ndarray
            M-Dimensional input values given by an N-by-M array where
            N is the number of input values.
        params: np.ndarray
            A set of parameters w/ the same length as the input dimension (M).

        Returns
        -------
        np.ndarray
            The output of the Sobol-G function evaluated on the input values.
            The output is a 1-dimensional array of length N.
        """
        params = self.parameters
        yy = np.sum(
            np.log(((np.abs(4 * xx - 2) + params) / (1 + params))), axis=1
        )

        return np.exp(yy)
