import numpy as np

def quantil_quantil_plotData(values1, values2):
    """returns the values needed to plot the q-q plot
    param values1: np.array, the values of the first distribution
    param values2: np.array, the values of the second distribution
    return x: np.array, the values for the x-axis
    return y: np.array, the values for the y-axis
    """
    # # sort the values of the distributions
    # values1_sorted = np.sort(values1)
    # values2_sorted = np.sort(values2)
    # return values1_sorted, values2_sorted

    # minmal length of the data
    n = min(len(values1), len(values2))
    # percentage steps for percentiles
    pvec = 100 * (np.arange(1, n+1, 1) - 0.5) / n
    # get the x-values (either sort or (if there are more x values than y values) get the percentiles)
    if len(values1) == n:
        xx = np.sort(values1)
    else:
        xx = np.percentile(values1, pvec)
    # get the y-values (either sort or (if there are more y values than x values) get the percentiles)
    if len(values2) == n:
        yy = np.sort(values2)
    else:
        yy = np.percentile(values2, pvec)

    return xx, yy

def exceedence_probability(data):
    """simple computation of the exceedence probability
    param data: np.array, the data to compute the exceedence probability
    return sorted_x: np.array, the sorted data
    return exceedence_probability: np.array, the exceedence probability of the data
    """
    sorted_x = np.sort(data)
    exceedence_probability = np.linspace(len(data), 1, len(data)) / len(data)
    return sorted_x, exceedence_probability