"""
Test module for instances of UQMetaTestFun (meta).
"""
import numpy as np
import pytest

from scipy.special import comb

from uqtestfuns import UQMetaTestFun, UQTestFun, UQMetaFunSpec, UnivDist
from uqtestfuns.meta.metaspec import UQTestFunSpec
from uqtestfuns.meta.basis_functions import BASIS_BY_ID
from conftest import create_random_marginals, assert_call


def _create_args_effects_dict(spatial_dimension):
    """Create a dictionary of effects-length specification.

    Notes
    -----
    - The length of each effect created with this function is the total
      number of possible terms.
    """
    effects_dict = dict()

    for i in range(1, spatial_dimension + 1):
        max_num = int(comb(spatial_dimension, i))
        effects_dict[i] = np.random.randint(1, max_num + 1)

    return effects_dict


def _create_reference_evaluate(xx: np.ndarray, parameters: UQTestFunSpec):
    """Evaluate a test function realization with alternative way."""
    basis_funs = parameters.basis_functions
    selected_basis = parameters.selected_basis
    effects_tuples = parameters.effects_tuples
    effects_coeffs = parameters.effects_coeffs

    yy = np.zeros(xx.shape[0])

    for key in effects_tuples:
        for idx, effects_indices in enumerate(effects_tuples[key]):
            zz = np.ones(xx.shape[0])
            for effect_idx in effects_indices:
                zz[:] *= basis_funs[selected_basis[effect_idx]](
                    xx[:, effect_idx]
                )
            yy[:] += effects_coeffs[key][idx] * zz

    return yy


@pytest.fixture(params=[1, 2, 3, 4, 5, 10])
def uqmetafunspec(request):
    """Create an instance of UQMetaFunSpec."""

    spatial_dimension = request.param

    basis_functions = {0: lambda x: x, 1: lambda x: x**2}

    effects_dict = _create_args_effects_dict(spatial_dimension)

    inputs = create_random_marginals(spatial_dimension)

    coeffs_generator = np.random.rand

    my_args = {
        "spatial_dimension": spatial_dimension,
        "basis_functions": basis_functions,
        "effects_dict": effects_dict,
        "inputs": inputs,
        "coeffs_generator": coeffs_generator,
    }

    my_metafun_spec = UQMetaFunSpec(
        spatial_dimension,
        basis_functions,
        effects_dict,
        inputs,
        coeffs_generator,
    )

    return my_metafun_spec, my_args


def test_create_instance(uqmetafunspec):
    """Test for creating an instance with custom UQMetaFunSpec"""
    # Create an instance of meta specification
    my_metafun_spec, my_args = uqmetafunspec

    # Create an instance of UQMetaTestFun
    my_metafun = UQMetaTestFun(my_metafun_spec)

    # Assertions
    assert (
        my_metafun.metafun_spec.spatial_dimension
        == my_args["spatial_dimension"]
    )
    assert (
        my_metafun.metafun_spec.basis_functions == my_args["basis_functions"]
    )
    assert my_metafun.metafun_spec.input_marginals == my_args["inputs"]
    assert (
        my_metafun.metafun_spec.coeffs_generator == my_args["coeffs_generator"]
    )
    for key in my_metafun.metafun_spec.effects:
        assert (
            my_metafun.metafun_spec.effects[key]
            == my_args["effects_dict"][key]
        )


@pytest.mark.parametrize("spatial_dimension", [1, 2, 3, 4, 5, 10])
@pytest.mark.parametrize("input_id", [None, 0, 1, 2, 3, 4, 5, 6, 7])
def test_create_instance_default(spatial_dimension, input_id):
    """Test for creating a default instance."""

    # Create an instance from default
    my_metafun = UQMetaTestFun.from_default(spatial_dimension, input_id)

    if spatial_dimension == 1:
        effects_keys_ref = [1]
    elif spatial_dimension in [2, 3, 4]:
        effects_keys_ref = [1, 2]
    else:
        effects_keys_ref = [1, 2, 3]

    # Assertions
    assert isinstance(my_metafun.metafun_spec, UQMetaFunSpec)
    assert my_metafun.metafun_spec.spatial_dimension == spatial_dimension
    assert effects_keys_ref == list(my_metafun.metafun_spec.effects)
    assert_call(my_metafun.metafun_spec.coeffs_generator, 10)


def test_create_instance_default_ranges():
    """Test for creating a default instance with ranges as the dimension."""

    # Create an instance from default
    my_metafun = UQMetaTestFun.from_default(np.arange(1, 11))

    # Assertions
    assert 1 <= my_metafun.metafun_spec.spatial_dimension < 11

    spatial_dimension = my_metafun.metafun_spec.spatial_dimension
    print(spatial_dimension)
    if spatial_dimension == 1:
        effects_keys_ref = [1]
    elif spatial_dimension in [2, 3, 4]:
        effects_keys_ref = [1, 2]
    else:
        effects_keys_ref = [1, 2, 3]
    assert list(my_metafun.metafun_spec.effects) == effects_keys_ref


def test_create_instance_default_zero_dimension():
    """Test for creating a zero-dimension instance (raise an exception)."""

    # Create an instance from default
    with pytest.raises(ValueError):
        UQMetaTestFun.from_default(0)


@pytest.mark.parametrize("spatial_dimension", [1, 2, 5, 10, 100])
def test_get_sample(spatial_dimension):
    """Test for getting a sample of UQTestFuns from the meta."""

    # Create an instance from default
    my_metafun = UQMetaTestFun.from_default(spatial_dimension)

    # Get sample 0
    my_testfun = my_metafun.get_sample(0)
    # Assertion
    assert my_testfun is None

    # Get sample 1
    my_testfun = my_metafun.get_sample(1)
    # Assertion
    assert isinstance(my_testfun, UQTestFun)
    assert my_testfun.spatial_dimension == spatial_dimension
    assert my_testfun.prob_input.spatial_dimension == spatial_dimension
    assert isinstance(my_testfun.parameters, UQTestFunSpec)
    assert_call(my_testfun, my_testfun.prob_input.get_sample(100))

    # Get sample > 1
    sample_size = 100
    my_testfuns = my_metafun.get_sample(sample_size)
    assert isinstance(my_testfuns, list)
    assert len(my_testfuns) == sample_size
    for i in range(sample_size):
        assert isinstance(my_testfuns[i], UQTestFun)


@pytest.mark.parametrize("spatial_dimension", [1, 2, 3, 4, 5])
def test_evaluate_sample(spatial_dimension):
    """Test for evaluating a sample of test function from the meta."""

    basis_functions = BASIS_BY_ID

    effects_dict = _create_args_effects_dict(spatial_dimension)

    input_marginals = [
        UnivDist(distribution="uniform", parameters=[0, 1]),
    ]

    coeffs_generator = np.random.rand

    # Create an instance from default
    my_metafun_spec = UQMetaFunSpec(
        spatial_dimension,
        basis_functions,
        effects_dict,
        input_marginals,
        coeffs_generator,
    )
    my_metafun = UQMetaTestFun(my_metafun_spec)

    # Get sample 0
    my_testfun = my_metafun.get_sample()

    # Assertion
    assert isinstance(my_testfun, UQTestFun)

    sample_size = 1000
    xx = my_testfun.prob_input.get_sample(sample_size)
    yy = my_testfun(xx)

    yy_ref = _create_reference_evaluate(xx, my_testfun.parameters)

    # Assertion
    assert np.allclose(yy, yy_ref)
