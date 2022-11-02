"""
Test module for UnivariateInput instances with a truncated normal distribution.
"""
import pytest
import numpy as np

from scipy.stats import norm

from uqtestfuns.core.prob_input.univariate_input import UnivariateInput
from conftest import create_random_alphanumeric


DISTRIBUTION_NAME = "truncnormal"


def _calc_mean(parameters: np.ndarray) -> float:
    """Compute the analytical mean of a given truncated normal distribution."""
    mu, sigma, lb, ub = parameters[:]

    alpha = (lb - mu) / sigma
    beta = (ub - mu) / sigma
    phi_alpha = norm.pdf(alpha)
    phi_beta = norm.pdf(beta)
    z = norm.cdf(beta) - norm.cdf(alpha)

    mean = mu - (phi_beta - phi_alpha) / z * sigma

    return mean


def _calc_std(parameters: np.ndarray) -> float:
    """Compute the analytical standard deviation of a given trunc. normal."""
    mu, sigma, lb, ub = parameters[:]

    alpha = (lb - mu) / sigma
    beta = (ub - mu) / sigma
    phi_alpha = norm.pdf(alpha)
    phi_beta = norm.pdf(beta)
    z = norm.cdf(beta) - norm.cdf(alpha)

    term_1 = 1
    term_2 = (beta * phi_beta - alpha * phi_alpha) / z
    term_3 = ((phi_beta - phi_alpha) / z) ** 2
    var = sigma**2 * (term_1 - term_2 - term_3)

    return np.sqrt(var)


def test_wrong_number_of_parameters():
    """Test the failure when specifying invalid number of parameters."""
    name = create_random_alphanumeric(5)
    distribution = DISTRIBUTION_NAME
    # A truncated normal distribution expects 4 parameters not 6!
    parameters = np.sort(np.random.rand(6))

    with pytest.raises(ValueError):
        UnivariateInput(
            name=name, distribution=distribution, parameters=parameters
        )


def test_failed_parameter_verification():
    """Test the failure when specifying the wrong parameter values"""
    name = create_random_alphanumeric(10)
    distribution = DISTRIBUTION_NAME

    # The 2nd parameter of the Beta distribution must be strictly positive!
    parameters = [7.71, -10, 1, 2]

    with pytest.raises(ValueError):
        UnivariateInput(
            name=name, distribution=distribution, parameters=parameters
        )

    # The mean must be inside the bounds!
    parameters = [5, 2, 1, 3]

    with pytest.raises(ValueError):
        UnivariateInput(
            name=name, distribution=distribution, parameters=parameters
        )

    # The mean must be inside the bounds!
    parameters = [0, 2, 1, 3]

    with pytest.raises(ValueError):
        UnivariateInput(
            name=name, distribution=distribution, parameters=parameters
        )

    # The lower bound must be smaller than upper bound!
    parameters = [3.5, 2, 4, 3]

    with pytest.raises(ValueError):
        UnivariateInput(
            name=name, distribution=distribution, parameters=parameters
        )


def test_estimate_mean():
    """Test the mean estimation of a truncated normal distribution."""

    # Create an instance of a truncated normal UnivariateInput
    name = create_random_alphanumeric(10)
    distribution = DISTRIBUTION_NAME
    # mu must be inside the bounds
    parameters = np.sort(1 + 2 * np.random.rand(3))
    parameters[[0, 1]] = parameters[[1, 0]]
    # Insert sigma as the second parameter
    parameters = np.insert(parameters, 1, np.random.rand(1))

    my_univariate_input = UnivariateInput(name, distribution, parameters)

    sample_size = 100000
    xx = my_univariate_input.get_sample(sample_size)

    # Estimated result
    mean = np.mean(xx)

    # Analytical result
    mean_ref = _calc_mean(parameters)

    # Assertion
    assert np.isclose(mean, mean_ref, rtol=1e-03, atol=1e-04)


def test_estimate_std():
    """Test the standard deviation estimation of a trunc. normal dist."""

    # Create an instance of a truncated normal UnivariateInput
    name = create_random_alphanumeric(10)
    distribution = DISTRIBUTION_NAME
    # mu must be inside the bounds
    parameters = np.sort(1 + 2 * np.random.rand(3))
    parameters[[0, 1]] = parameters[[1, 0]]
    # Insert sigma as the second parameter
    parameters = np.insert(parameters, 1, np.random.rand(1))

    my_univariate_input = UnivariateInput(name, distribution, parameters)

    sample_size = 1000000
    xx = my_univariate_input.get_sample(sample_size)

    # Estimated result
    std = np.std(xx)

    # Analytical result
    std_ref = _calc_std(parameters)

    # Assertion
    assert np.isclose(std, std_ref, rtol=1e-03, atol=1e-04)