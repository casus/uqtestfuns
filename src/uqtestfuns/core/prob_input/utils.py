"""
Utility module for probabilistic input modeling.
"""

from .univariate_distributions import uniform

SUPPORTED_MARGINALS = ["uniform"] #, "normal", "lognormal"]


def get_distribution_module(distribution: str):  # pragma: no cover
    """Get the relevant module corresponding to the distribution."""
    if distribution == "uniform":
        distribution_module = uniform

    return distribution_module

def verify_distribution(distribution: str):
    """Verify the type of distribution.

    Parameters
    ----------
    distribution : str
        Type of the distribution.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the type of distribution is not currently supported.
    """
    if distribution not in SUPPORTED_MARGINALS:
        raise ValueError(
            f"Univariate distribution '{distribution}' is not supported!"
        )


def get_distribution_bounds(distribution, parameters):
    """Get the bounds of the distribution given the parameters.

    While the support of many continuous density functions are unbounded,
    numerically they are always bounded. Below and above the bounds the density
    values are always zero.
    """
    distribution_module = get_distribution_module(distribution)
    lower = distribution_module.lower(parameters)
    upper = distribution_module.upper(parameters)

    return lower, upper


def verify_parameters(distribution, parameters):
    """Verify the parameter values of the distribution"""
    distribution_module = get_distribution_module(distribution)

    distribution_module.verify_parameters(parameters)


def get_pdf_values(xx, distribution, parameters):
    """Get the PDF values of the distribution on a set of sample points.

    Notes
    -----
    - PDF stands for "probability density function".
    """
    distribution_module = get_distribution_module(distribution)

    return distribution_module.pdf(xx, parameters)


def get_cdf_values(xx, distribution, parameters):
    """Get the CDF values of the distribution on a set of sample points.

    Notes
    -----
    - CDF stands for "cumulative distribution function".
    """
    distribution_module = get_distribution_module(distribution)

    return distribution_module.cdf(xx, parameters)


def get_icdf_values(xx, distribution, parameters):
    """Get the inverse CDF values of the distribution on a set of sample points.

    Notes
    -----
    - CDF stands for "cumulative distribution function".
    - ICDF stands for "inverse cumulative distribution function".
    """
    distribution_module = get_distribution_module(distribution)

    return distribution_module.icdf(xx, parameters)
