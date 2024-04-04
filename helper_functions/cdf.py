import numpy as np
# equivalent to matlab cdf function
def cdf(x, mu):
    """Compute the cumulative distribution function
    :param x: values at which to evaluate
    :param mu: mean value of the distribtion
    :return: cdf
    """
    z = x / mu # elementwise division of x by mu
    p = - (np.exp(-z) - 1)

    return p