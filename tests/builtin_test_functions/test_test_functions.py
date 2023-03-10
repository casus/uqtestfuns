"""
Test module for instances of the available UQ test functions.

Notes
-----
- All UQ test functions are derived from UQTestFunABC abstract base class.
- The tests in this module only deal with the general behaviors of the concrete
  implementations not about the correctness of computation of a particular
  implementation.
"""
import numpy as np
import pytest
import copy

from conftest import assert_call
from uqtestfuns.utils import get_available_classes

from uqtestfuns import test_functions

AVAILABLE_FUNCTION_CLASSES = get_available_classes(test_functions)


@pytest.fixture(params=AVAILABLE_FUNCTION_CLASSES)
def builtin_testfun(request):
    _, testfun = request.param

    return testfun


def test_create_instance(builtin_testfun):
    """Test the creation of the default instance of avail. test functions."""
    testfun = builtin_testfun

    # Assertion
    assert_call(testfun)


def test_create_instance_with_custom_name(builtin_testfun):
    """Test the creation of an instance and passing the name argument."""
    testfun_class = builtin_testfun

    # Get the default name of the test function
    name = testfun_class.__name__

    # Create a default instance
    my_fun = testfun_class()

    # Assertion
    assert my_fun.name == name

    # Use custom name to create a test function
    my_fun = testfun_class(name=name)
    assert my_fun.name == name


def test_create_instance_with_prob_input(builtin_testfun):
    """Test the creation of a default instance and passing prob. input.

    Notes
    -----
    - If non-default probabilistic input is to be specified, first create
      an instance without probabilistic input then assign the input after
      construction.
    """
    testfun_class = builtin_testfun

    # Create an instance
    my_fun = testfun_class()

    # Copy the underlying probabilistic input
    my_prob_input = copy.copy(my_fun.prob_input)

    # Create an instance without probabilistic input
    if testfun_class.AVAILABLE_INPUTS is not None:
        my_fun_2 = testfun_class(prob_input_selection=None)
        assert my_fun_2.prob_input is None
        assert my_fun_2.spatial_dimension == (
            testfun_class.DEFAULT_SPATIAL_DIMENSION
        )

        # Assign the probabilistic input
        my_fun_2.prob_input = my_prob_input
        assert my_fun_2.prob_input is my_prob_input

        # Nonsensical probabilistic input model
        with pytest.raises(TypeError):
            my_fun_2.prob_input = 10


def test_create_instance_with_parameters(builtin_testfun):
    """Test the creation of the default instance and passing parameters.

    Notes
    -----
    - If non-default parameters are to be specified, first create
      an instance without parameters then assign the parameters after
      construction.
    """

    testfun_class = builtin_testfun

    my_fun = testfun_class()
    parameters = my_fun.parameters

    if testfun_class.AVAILABLE_PARAMETERS is not None:
        my_fun_2 = testfun_class(parameters_selection=None)
        assert my_fun_2.parameters is None
        my_fun_2.parameters = parameters
        assert my_fun_2.parameters is parameters
    else:
        assert my_fun.parameters is None


def test_available_inputs(builtin_testfun):
    """Test creating test functions with different built-in input specs."""

    testfun_class = builtin_testfun

    available_inputs = testfun_class.AVAILABLE_INPUTS

    for available_input in available_inputs:
        assert_call(testfun_class, prob_input_selection=available_input)


def test_available_parameters(builtin_testfun):
    """Test creating test functions with different built-in parameters."""

    testfun_class = builtin_testfun

    available_parameters = testfun_class.AVAILABLE_PARAMETERS

    if available_parameters is not None:
        for available_parameter in available_parameters:
            assert_call(
                testfun_class, parameters_selection=available_parameter
            )


def test_call_instance(builtin_testfun):
    """Test calling an instance of the test function on input values."""

    testfun = builtin_testfun

    # Create an instance
    my_fun = testfun()

    xx = my_fun.prob_input.get_sample(10)

    # Assertions
    assert_call(my_fun, xx)


def test_transform_input(builtin_testfun):
    """Test transforming a set of input values in the default unif. domain."""

    testfun = builtin_testfun

    # Create an instance
    my_fun = testfun()

    sample_size = 100

    # Transformation from the default uniform domain to the input domain
    np.random.seed(315)
    # NOTE: Direct sample from the input property is done by column to column,
    # for reproducibility using the same RNG seed the reference input must be
    # filled in column by column as well with the. The call to NumPy random
    # number generators below yields the same effect.
    xx_1 = -1 + 2 * np.random.rand(my_fun.spatial_dimension, sample_size).T
    xx_1 = my_fun.transform_sample(xx_1)

    # Directly sample from the input property
    np.random.seed(315)
    xx_2 = my_fun.prob_input.get_sample(sample_size)

    # Assertion: two sampled values are equal
    assert np.allclose(xx_1, xx_2)


def test_transform_input_non_default(builtin_testfun):
    """Test transforming an input from non-default domain."""

    testfun = builtin_testfun

    # Create an instance
    my_fun = testfun()

    sample_size = 100

    # Transformation from non-default uniform domain to the input domain
    np.random.seed(315)
    # NOTE: Direct sample from the input property is done by column to column,
    # for reproducibility using the same RNG seed the reference input must be
    # filled in column by column as well with the. The call to NumPy random
    # number generators below yields the same effect.
    xx_1 = np.random.rand(my_fun.spatial_dimension, sample_size).T
    xx_1 = my_fun.transform_sample(xx_1, min_value=0.0, max_value=1.0)

    # Directly sample from the input property
    np.random.seed(315)
    xx_2 = my_fun.prob_input.get_sample(sample_size)

    # Assertion: two sampled values are equal
    assert np.allclose(xx_1, xx_2)


def test_evaluate_wrong_input_dim(builtin_testfun):
    """Test if an exception is raised when input is of wrong dimension."""

    testfun = builtin_testfun()

    xx = np.random.rand(10, testfun.spatial_dimension * 2)

    with pytest.raises(ValueError):
        testfun(xx)


def test_evaluate_wrong_input_domain(builtin_testfun):
    """Test if an exception is raised when sampled input is in wrong domain."""

    testfun = builtin_testfun()

    # Create a sample in [-2, 2]
    xx = -2 + 4 * np.random.rand(1000, testfun.spatial_dimension)

    with pytest.raises(ValueError):
        # By default, the transformation domain is from [-1, 1]
        testfun.transform_sample(xx)

    # Create sampled input values from the default and perturb them
    xx = np.empty((100, testfun.spatial_dimension))
    for i, marginal in enumerate(testfun.prob_input.marginals):
        lb = marginal.lower + 1000
        ub = marginal.upper - 1000
        xx[:, i] = lb + (ub - lb) * np.random.rand(100)

    with pytest.raises(ValueError):
        # Evaluation will check if the sampled input are within the domain
        testfun(xx)


def test_evaluate_invalid_spatial_dim(builtin_testfun):
    """Test if an exception is raised if invalid spatial dimension is given."""

    if builtin_testfun.DEFAULT_SPATIAL_DIMENSION is None:
        with pytest.raises(TypeError):
            builtin_testfun(spatial_dimension="10")


def test_evaluate_invalid_input_selection(builtin_testfun):
    """Test if an exception is raised if invalid input selection is given."""
    with pytest.raises(ValueError):
        builtin_testfun(prob_input_selection=100)
