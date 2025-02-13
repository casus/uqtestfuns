---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

(getting-started:tutorial-built-in-functions)=
# Tutorial: Create Built-in Test Functions

UQTestFuns includes a wide range of test functions from the uncertainty
quantification community; these functions are referred to
as the _built-in test functions_.
This tutorial provides you with an overview of the package;
you'll learn about the built-in test functions, their common interfaces,
as well as their important properties and methods.

By the end of this tutorial, you'll be able to create any test function
available in UQTestFuns and access its basic but important functionalities.

UQTestFuns is designed to work with minimal dependency within the numerical
Python ecosystem.
At the very least, UQTestFuns requires NumPy and SciPy to work.
It might be a good idea to import NumPy alongside UQTestFuns:

```{code-cell} ipython3
import numpy as np
import uqtestfuns as uqtf
```

## Listing available test functions

To list all the test functions currently available:

```{code-cell} ipython3
:tags: ["output_scroll"]

uqtf.list_functions()
```

This function produces a list of test functions,
their respective constructor, input dimension, typical applications,
as well as a short description.

## A Callable instance

Take, for instance, the {ref}`borehole <test-functions:borehole>` function
{cite}`Harper1983`, an eight-dimensional test function typically used
in the context of metamodeling and sensitivity analysis.
To instantiate a borehole test function, call the constructor as follows:

```{code-cell} ipython3
my_testfun = uqtf.Borehole()
```

To verify whether the instance has been created,
print it to get some basic information on the terminal:

```{code-cell} ipython3
print(my_testfun)
```

```{margin}
Think of a `Callable` as a regular function;
it takes some inputs, evaluates them, and produces some outputs.
In otherwords, you _call_ it with arguments.
```

The resulting object is a `Callable`.
The instance can be evaluated with a set of input values.
For example, the eight-dimensional borehole function can be evaluated
at a single point (1-by-8 array):

```{code-cell} ipython3
xx = np.array([
  [
    1.04803586e-01, 2.54527756e+03, 9.44572869e+04, 9.94988176e+02,
    6.31793993e+01, 7.63308791e+02, 1.57530252e+03, 1.00591588e+04
  ]
])
my_testfun(xx)
```

```{note}
Calling the function on a set of input values automatically
verifies the correctness of the input (its dimensionality and bounds).
Moreover, the test function accepts a vectorized input
(that is, an $N$-by-$M$ array where $N$ and $M$ are the number of points
and dimensions, respectively)
```

## Probabilistic input

In general, the results of uncertainty quantification (UQ) analyses
depend on the specified probabilistic input.
When a test function appears in the literature,
a specification for the probabilistic input is usually provided.
In UQTestFuns, a probabilistic input model is an integral part
of each test function.

For instance, the borehole function has a probabilistic input model
that consists of eight independent random variables.
This input model is stored inside the `prob_input` property
of the test function instance.
Print it to the terminal to see the full specification:

```{code-cell} ipython3
print(my_testfun.prob_input)
```

```{note}
_Copulas_ models the statistical dependence structure
between the component (univariate) marginals.
If the marginals are independent, then the copulas value is `None`.
Currently, UQTestFuns does not support dependent probability inputs.
```

From the underlying probabilistic input model,
a set of input values can be randomly generated.
This is often useful for verification and validation purposes.
For instance, to generate $10'000$ sample points:

```{code-cell} ipython3
xx_sample = my_testfun.prob_input.get_sample(10000)
yy_sample = my_testfun(xx_sample)
```

The histogram of the output values can be created as follows:

```{code-cell} ipython3
:tags: [hide-input]

import matplotlib.pyplot as plt

plt.hist(yy_sample, bins="auto", color="#8da0cb")
plt.grid()
plt.xlabel("$\mathcal{M}(\mathbf{X})$")
plt.ylabel("Counts [-]")
plt.gcf().set_dpi(150);
```

```{note}
An `ProbInput` instance has a method called `reset_rng()`;
You can call this method to create a new underlying RNG
perhaps with a seed number.
In that case, the seed number is optional; if not specified,
the system entropy is used to initialized
the [NumPy default random generator](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng).

In UQTestFuns, each instance of probabilistic input model carries
its own pseudo-random number generator (RNG)
to avoid using the global NumPy random RNG.
See this [blog post](https://albertcthomas.github.io/good-practices-random-number-generators/)
regarding some good practices on using NumPy RNG.
```

## Transformation to the function domain

Some UQ methods often produce sample points in a hypercube domain
(for example, $[0, 1]^M$ or $[-1, 1]^M$ where $M$ is the number of input dimension)
at which the function should be evaluated.
This hypercube domain may differ from the test function's domain.
Before the test function can be evaluated,
those values must be first transformed to the function domain.

```{margin}
The transformation is done via an isoprobabilistic transformation.
```

UQTestFuns provides a convenient function to transform sample points
in one domain to the function domain.
For instance, suppose we have a sample of size $5$ in $[-1, 1]^8$
for the borehole function:

```{code-cell} ipython3
rng_1 = np.random.default_rng(42)
xx_sample_dom_1 = rng_1.uniform(low=-1, high=1, size=(5, 8))
xx_sample_dom_1
```

We can transform this set of values to the domain of the function
via the `transform_sample()` method:

```{code-cell} ipython3
xx_sample_trans_1 = my_testfun.transform_sample(xx_sample_dom_1)
xx_sample_trans_1
```

By default, the method assumes the uniform domain of the passed values
is in $[-1, 1]^M$.
It is possible to transform values defined in another uniform domain.
For example, the sample values in $[0, 1]^8$ (a unit hypercube):

```{code-cell} ipython3
rng_2 = np.random.default_rng(42)
xx_sample_dom_2 = rng_2.random((5, 8))
xx_sample_dom_2
```

can be transformed to the domain of the borehole function as follows:

```{code-cell} ipython3
xx_sample_trans_2 = my_testfun.transform_sample(
    xx_sample_dom_2, min_value=0.0, max_value=1.0
)
xx_sample_trans_2
```

Note that for a given sample, the bounds of the hypercube domain must be
the same in all dimensions.

The two transformed values above should be the same since
we use two instances of the default RNG with the same seed
to generate the random sample.

```{code-cell} ipython3
assert np.allclose(xx_sample_trans_1, xx_sample_trans_2)
assert np.allclose(my_testfun(xx_sample_trans_1), my_testfun(xx_sample_trans_2))
```

## Test functions with parameters

```{margin}
Parameters of a test function can be anything.
```

Some test functions are _parameterized_;
this means that to fully specify the function,
an additional set of values must be specified.
In principle, these parameter values can be anything:
numerical values, flags, selection using strings, etc.

For instance, consider the {ref}`Ishigami <test-functions:ishigami>` function
{cite}`Ishigami1991` defined as follows:

$$
\mathcal{M}(\boldsymbol{x}) = \sin{(x_1)} + a \sin^2{(x_2)} + b x_3^4 \sin{(x_1)}
$$

where $a$ and $b$ are the so-called parameters of the function.
Before the function can be evaluated,
these parameters must be assigned to some values.
The default Ishigami function in UQTestFuns has these values given
and stored in the `parameters` property:

```{code-cell} ipython3
my_testfun = uqtf.Ishigami()

print(my_testfun.parameters)
```

To assign different parameter values, override the property values
of the instance by specifying the name in brackets just like a dictionary:
For example:

```{code-cell} ipython3
my_testfun.parameters["a"] = 7.0
my_testfun.parameters["b"] = 0.35
```

Note that once set, the parameter values are kept constant
during the evaluation of the function on a set of input values

Different parameter values usually change the overall behavior of the function.
In the case of the Ishigami function,
different parameter values alter the total variance of the output
as illustrated in the figure below.

```{code-cell} ipython3
:tags: [remove-input]

xx_sample = my_testfun.prob_input.get_sample(10000)
my_testfun.parameters["a"] = 7.0
my_testfun.parameters["b"] = 0.05
yy_param_1 = my_testfun(xx_sample)
my_testfun.parameters["a"] = 7.0
my_testfun.parameters["b"] = 0.35
yy_param_2 = my_testfun(xx_sample)

plt.hist(yy_param_2, bins="auto", color="#fc8d62", label="parameter 2")
plt.hist(yy_param_1, bins="auto", color="#66c2a5", label="parameter 1")
plt.grid()
plt.xlabel("$\mathcal{M}(\mathbf{X})$")
plt.ylabel("Counts [-]")
plt.legend(fontsize=14)
plt.gcf().set_dpi(150);
```

## Test functions with variable dimension

```{margin}
input dimension must be a positive integer.
```

Some test functions support a _variable dimension_, meaning that an instance
of a test function can be constructed for any number (positive integer, please) 
of input dimension.

Consider, for instance, the {ref}`Sobol'-G <test-functions:sobol-g>` function
{cite}`Saltelli1995`,
a test function whose dimension can be varied
and a popular choice in the context of sensitivity analysis.
It is defined as follows:

$$
\mathcal{M}(\boldsymbol{x}) = \prod_{m = 1}^M \frac{\lvert 4 x_m - 2 \rvert + a_m}{1 + a_m}
$$
where $\boldsymbol{x} = \{ x_1, \ldots, x_M \}$ is the $M$-dimensional vector
of input variables,
and $\boldsymbol{a} = \{ a_1, \ldots, a_M \}$ are parameters of the function.

To create a six-dimensional Sobol'-G function,
use the parameter `input_dimension` to specify the desired dimensionality:

```{code-cell} ipython3
my_testfun = uqtf.SobolG(input_dimension=6)
```

Verify that the function is indeed a six-dimension one:

```{code-cell} ipython3
print(my_testfun)
```

and:

```{code-cell} ipython3
print(my_testfun.prob_input)
```

## References

```{bibliography}
:style: unsrtalpha
:filter: docname in docnames
```
