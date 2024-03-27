# function to find the intersections between two curves defined by x1, y1 and x2, y2
import scipy.interpolate
import scipy.optimize
import numpy as np

def find_intersections(x1, y1, x2, y2):
    """
    Find the intersections between two curves defined by x1, y1 and x2, y2
    :param x1: np.array, x values of the first curve
    :param y1: np.array, y values of the first curve
    :param x2: np.array, x values of the second curve
    :param y2: np.array, y values of the second curve
    :return: np.array, x values of the intersections
    """
    # find the intersections between the two curves
    f1 = scipy.interpolate.interp1d(x1, y1, kind='linear', fill_value='extrapolate')
    f2 = scipy.interpolate.interp1d(x2, y2, kind='linear', fill_value='extrapolate')
    x_intersections = scipy.optimize.fsolve(lambda x: f1(x) - f2(x), x1[np.where(np.diff(np.sign(y1 - y2)))[0]])
    y_intersections = f1(x_intersections)
    return x_intersections, y_intersections
