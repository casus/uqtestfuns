"""
Test module for instances of the available UQ test functions.

Notes
-----
- All UQ test functions are instantiated as UQTestFun.
- The tests in this module only deal with the behavior of the UQTestFun
  instances associated with the UQ test functions not about the correctness
  of the computation results.
"""
import numpy as np
import pytest

from uqtestfuns import create_from_default
from conftest import assert_call

from uqtestfuns.test_functions.default import AVAILABLE_FUNCTIONS

AVAILABLE_FUNCTION_KEYS = list(AVAILABLE_FUNCTIONS.keys())


@pytest.fixture(params=AVAILABLE_FUNCTION_KEYS)
def default_testfun(request):
    """Fixture for the tests, an instance from the available test functions."""
    testfun = create_from_default(request.param)
    testfun_mod = AVAILABLE_FUNCTIONS[request.param]

    return testfun, testfun_mod


def test_create_instance(default_testfun):
    """Test the creation of the default instance of available test functions."""

    testfun, testfun_mod = default_testfun

    # Assertions
    assert testfun.spatial_dimension == \
           testfun_mod.DEFAULT_INPUT.spatial_dimension
    assert testfun.input == testfun_mod.DEFAULT_INPUT


def test_call_instance(default_testfun):
    """Test calling an instance of the test function."""

    testfun, _ = default_testfun

    xx = np.random.rand(10, testfun.spatial_dimension)

    # Assertions
    assert_call(testfun, xx)
    assert_call(testfun.evaluate, xx)


def test_transform_input(default_testfun):
    """Test transforming a set of input values in the default uniform domain."""

    testfun, _ = default_testfun

    # Transformation from the default uniform domain to the input domain
    np.random.seed(315)
    xx_1 = -1 + 2 * np.random.rand(100, testfun.spatial_dimension)
    xx_1 = testfun.transform_inputs(xx_1)

    # Directly sample from the input property
    np.random.seed(315)
    xx_2 = testfun.input.get_sample(100)

    # Assertion: two sampled values are equal
    assert np.allclose(xx_1, xx_2)


def test_transform_input_non_default(default_testfun):
    """Test transforming an input from non-default domain."""

    testfun, _ = default_testfun

    # Transformation from non-default uniform domain to the input domain
    np.random.seed(315)
    xx_1 = np.random.rand(100, testfun.spatial_dimension)
    xx_1 = testfun.transform_inputs(xx_1, min_value=0.0, max_value=1.0)

    # Directly sample from the input property
    np.random.seed(315)
    xx_2 = testfun.input.get_sample(100)

    # Assertion: two sampled values are equal
    assert np.allclose(xx_1, xx_2)


def test_wrong_input_dim(default_testfun):
    """Test if an exception is raised when input is of wrong dimension."""

    testfun, _ = default_testfun

    # Compute variance via Monte Carlo
    xx = np.random.rand(10, testfun.spatial_dimension*2)

    with pytest.raises(ValueError):
        testfun(xx)
