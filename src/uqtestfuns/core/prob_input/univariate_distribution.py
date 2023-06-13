"""
Module with an implementation of the ``UnivDist`` class.

The ``UnivDist`` class represents a univariate random variable.
Each random variable has a (parametric) probability distribution.
"""
from __future__ import annotations

import numpy as np

from numpy.random._generator import Generator
from numpy.typing import ArrayLike
from dataclasses import dataclass, field
from typing import Optional, Union

from .utils import (
    verify_distribution,
    get_distribution_bounds,
    verify_parameters,
    get_pdf_values,
    get_cdf_values,
    get_icdf_values,
)
from .input_spec import MarginalSpec
from ...global_settings import ARRAY_FLOAT

__all__ = ["UnivDist"]

# Ordered field names for printing purpose
FIELD_NAMES = ["name", "distribution", "parameters", "description"]


@dataclass(frozen=True)
class UnivDist:
    """A class for univariate random variables.

    Parameters
    ----------
    distribution : str
        The type of the probability distribution
    parameters : ArrayLike
        The parameters of the chosen probability distribution
    name : str, optional
        The name of the random variable
    description : str, optional
        The short text description of the random variable
    rng_seed : int, optional.
        The seed used to initialize the pseudo-random number generator.
        If not specified, the value is taken from the system entropy.

    Attributes
    ----------
    lower : float
        The lower bound of the distribution
    upper : float
        The upper bound of the distribution
    _rng : Generator
        The default pseudo-random number generator of NumPy.
        The generator is only created if or when needed (e.g., generating
        a random sample from the distribution).
    """

    distribution: str
    parameters: ArrayLike
    name: Optional[str] = None
    description: Optional[str] = None
    lower: float = field(init=False, repr=False)
    upper: float = field(init=False, repr=False)
    rng_seed: Optional[int] = field(default=None, repr=False)
    _rng: Optional[Generator] = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        # Because frozen=True, post init must access self via setattr
        # Make sure the distribution is lower-case
        object.__setattr__(self, "distribution", self.distribution.lower())

        # Convert parameters to a numpy array
        object.__setattr__(self, "parameters", np.array(self.parameters))

        # Verify the selected univariate distribution type
        verify_distribution(self.distribution)

        # Verify the value of the parameters
        verify_parameters(self.distribution, self.parameters)

        # Get and set the lower and upper bounds
        _lower, _upper = get_distribution_bounds(
            self.distribution, self.parameters
        )
        object.__setattr__(self, "lower", _lower)
        object.__setattr__(self, "upper", _upper)

    def transform_sample(
        self,
        xx: Union[float, np.ndarray],
        other: UnivDist,
    ) -> np.ndarray:
        """Transform a sample from a given distribution to another."""
        if not isinstance(other, UnivDist):
            raise TypeError("Other instance must be of UnivariateType!")

        xx_trans = self.cdf(xx)

        return get_icdf_values(
            xx_trans,
            other.distribution,
            other.parameters,
            other.lower,
            other.upper,
        )

    def get_sample(self, sample_size: int = 1) -> np.ndarray:
        """Get a random sample from the distribution."""
        if self._rng is None:  # pragma: no cover
            # Create a pseudo-random number generator (lazy evaluation)
            rng = np.random.default_rng(self.rng_seed)
            object.__setattr__(self, "_rng", rng)

        xx = self._rng.random(sample_size)  # type: ignore

        return get_icdf_values(
            xx, self.distribution, self.parameters, self.lower, self.upper
        )

    def pdf(self, xx: Union[float, np.ndarray]) -> ARRAY_FLOAT:
        """Compute the PDF of the distribution on a set of values."""
        # TODO: check if you put a scalar inside
        # Convert input to an np.array
        xx = np.asarray(xx)

        return get_pdf_values(
            xx, self.distribution, self.parameters, self.lower, self.upper
        )

    def cdf(self, xx: Union[float, np.ndarray]) -> ARRAY_FLOAT:
        """Compute the CDF of the distribution on a set of values.

        The function transforms the sample values in the domain
        of the distribution to the [0, 1] domain.
        """
        # TODO: check if you put a scalar inside
        # Convert input to an np.array
        xx = np.asarray(xx)

        return get_cdf_values(
            xx, self.distribution, self.parameters, self.lower, self.upper
        )

    def icdf(self, xx: Union[float, np.ndarray]) -> ARRAY_FLOAT:
        """Compute the inverse CDF of the distribution on a set of values.

        The function transforms values in the [0,1] domain to the domain
        of the distribution.
        """
        # TODO: verify that the input is in [0, 1]
        xx = np.asarray(xx)

        return get_icdf_values(
            xx, self.distribution, self.parameters, self.lower, self.upper
        )

    @classmethod
    def from_spec(
        cls, marginal_spec: MarginalSpec, rng_seed: Optional[int] = None
    ):
        """Create an instance of UnivDist from a marginal specification.

        Parameters
        ----------
        marginal_spec : MarginalSpec
            The specification for the univariate marginal.
        rng_seed : int, optional
            The seed used to initialize the pseudo-random number generator.
            If not specified, the value is taken from the system entropy.
        """
        return cls(
            distribution=marginal_spec.distribution,
            parameters=marginal_spec.parameters,
            name=marginal_spec.name,
            description=marginal_spec.description,
            rng_seed=rng_seed,
        )
