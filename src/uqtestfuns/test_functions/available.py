"""
Helpers module to construct probabilistic input and parameters.
"""
from typing import Callable, Optional, Any
from ..core import MultivariateInput


def create_prob_input_from_available(
    input_selection: str,
    available_input_specs: dict,
    spatial_dimension: Optional[int] = None,
) -> Optional[MultivariateInput]:
    """Construct a Multivariate input given available specifications.

    Parameters
    ----------
    input_selection : str
        Which available input specifications to construct.
    available_input_specs : dict
        Dictionary of available probabilistic input specifications.
    spatial_dimension : int, optional
        The requested number of spatial dimensions, when applicable.
        Some specifications are functions of spatial dimension.
    """
    if input_selection is None:
        return None

    if input_selection in available_input_specs:
        input_specs = available_input_specs[input_selection]
        if isinstance(input_specs["marginals"], Callable):
            marginals = input_specs["marginals"](spatial_dimension)
            prob_input = MultivariateInput(
                name=input_specs["name"],
                description=input_specs["description"],
                marginals=marginals,
                copulas=input_specs["copulas"],
            )
        else:
            prob_input = MultivariateInput(**input_specs)
    else:
        raise ValueError("Invalid selection!")

    return prob_input


def create_parameters_from_available(
    param_selection: str,
    available_parameters: dict,
    spatial_dimension: Optional[int] = None,
) -> Any:
    """Construct a set of parameters given available specifications.

    Parameters
    ----------
    param_selection : str
        Which parameter specification to construct.
    available_parameters : dict
        Dictionary of available parameters specifications.
    spatial_dimension : int, optional
        The requested number of spatial dimensions, when applicable.
        Some specifications are functions of spatial dimension.
    """

    if param_selection is None:
        return None

    if param_selection in available_parameters:
        parameters = available_parameters[param_selection]
        if isinstance(parameters, Callable):
            parameters = parameters(spatial_dimension)
    else:
        raise ValueError("Invalid parameters selection!")

    return parameters
