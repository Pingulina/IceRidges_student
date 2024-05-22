# the functions provided in this module are used to find independent points (e.g. keels) in a set of data points using the rayleigh criterion
import os
import sys
import numpy as np
import scipy.signal

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
# Get the current working directory
cwd = os.getcwd()
# Construct the path to the base directory
base_dir = os.path.join(cwd, '..')
# Add the base directory to sys.path
sys.path.insert(0, base_dir)
from import_module import import_module
constants = import_module('constants', 'helper_functions')

def rayleigh_criterion(data_x, data_h):
    """
    Find independent points (e.g. keels) in a set of data points using the rayleigh criterion
    :param data_x: list or numpy array, list of data 
    :param threshold: float, threshold for the rayleigh criterion
    :return: list, list of independent points
    """
    # if data_x and data_h are lists, convert them to numpy arrays
    if type(data_x) == list:
        data_x = np.array(data_x)
    if type(data_h) == list:
        data_h = np.array(data_h)

    # if they are still not numpy arrays, raise an error
    if type(data_x) != np.ndarray or type(data_h) != np.ndarray:
        raise ValueError("The input data is not a list or numpy array")

    peak_indices, _ = scipy.signal.find_peaks(data_h, height=constants.min_draft * (1+1e-5)) # +constants.machine_precision) # find the peaks in the data, that are larger than min_draft
    x_pot = np.array(data_x[peak_indices])
    h_pot = np.array(data_h[peak_indices])

    peak_indices, _ = scipy.signal.find_peaks(-data_h) # find the peaks in the negative data (to find the minima)
    x_min = np.array(data_x[peak_indices])
    h_min = np.array(data_h[peak_indices]) 
    # remove all values from x_min and h_min with a draft (h) smaller than the threshhold
    x_min = x_min[h_min >= constants.threshold_draft]
    h_min = h_min[h_min >= constants.threshold_draft]

    ## find the locations of the ridges in the data_x and data_h
    # make a binary signal for draft above the threshold
    xat = np.ones(len(data_x))
    xat[np.where(data_h < constants.threshold_draft)] = 0
    # find jumps in the binary signal (where the draft is above the threshold) and eliminate where there are no jumps
    corners = np.abs(np.diff(xat))
    corners_index = np.where(corners != 0)[0] # zero means, no jump, same side of the threshold for both values
    x_corners = data_x[corners_index] # the x value of the jump
    corners = corners[corners_index] # the value of the jump

    # emiminate all threshold crossings without a ridge
    peaks_zero_flag = np.zeros(len(x_pot), dtype=int)
    x_merged = np.concatenate((x_corners, x_pot))
    y_merged = np.concatenate((corners, peaks_zero_flag))

    sortIndex = np.argsort(x_merged)
    x_merged_sorted = x_merged[sortIndex]
    y_merged_sorted = y_merged[sortIndex]

    cor = np.diff(y_merged_sorted)
    cor_is_minus_one = np.where(cor == -1)[0]
    cor_is_one = np.where(cor == 1)[0]
    x_cor = np.concatenate((x_merged_sorted[cor_is_minus_one], x_merged_sorted[cor_is_one]))


    ###
    cuts = data_x[np.where(np.isin(data_x, x_cor))]
    trigger = 1
    iteration_index = 0
    while not trigger==0:
        print(f"------------------------------------ \nIteration: {iteration_index}")
        if not iteration_index == 0:
            x_min = x_min_temp
            h_min = h_min_temp
    
        # then remove all crossings from the list, where no ridge occurs
    
        for ps in range(len(h_pot)-1):
            if len(np.intersect1d(np.where(x_pot[ps] < x_cor), np.where(x_cor < x_pot[ps+1]))) == 0:
                # if in between two peaks there are no crossings, delete alll minimas except the smalles one (minima of minimas)
                x_del = np.intersect1d(np.where(x_pot[ps] < x_min), np.where(x_min < x_pot[ps+1]))
                xx = np.argmin(h_min[x_del]) # index of the smallest point between the two peaks
                # don't remove the smallest minima, remove it from x_del list
                x_del = np.delete(x_del, xx)

                # delete the entriex of x_min and h_min at the indices of x_del
                x_min = np.delete(x_min, x_del)
                h_min = np.delete(h_min, x_del)

            else:
                # if there is a crossing between two peaks, remove all the minimas
                x_del = np.intersect1d(np.where(x_pot[ps] < x_min), np.where(x_min < x_pot[ps+1]))
                x_min = np.delete(x_min, x_del)
                h_min = np.delete(h_min, x_del)

        # remove all minimas before the first and after the last peak
        h_min = np.delete(h_min, np.where(x_min < x_pot[0])) # h_min[np.where(x_min > x_pot[0])]
        x_min = np.delete(x_min, np.where(x_min < x_pot[0])) # x_min[np.where(x_min > x_pot[0])]
        h_min = np.delete(h_min, np.where(x_min > x_pot[-1])) # h_min[np.where(x_min < x_pot[-1])]
        x_min = np.delete(x_min, np.where(x_min > x_pot[-1])) # x_min[np.where(x_min < x_pot[-1])]

        # x_min and h_min are now the minimas between ridges where no crossing has occured, 
        # this are the places where potentialy two ridges can merge or be two separate ridges

        x_min_temp = x_min
        h_min_temp = h_min

        # double each entry of x_min and h_min
        x_min = np.repeat(x_min, 2)
        h_min = np.repeat(h_min, 2)

        x_start_stop = np.concatenate((x_min, x_cor))
        h_start_stop = np.concatenate((h_min, cuts))

        sortIndex = np.argsort(x_start_stop)
        x_start_stop = x_start_stop[sortIndex]
        h_start_stop = h_start_stop[sortIndex]

        # take every second element of x_start_stop in x_start and every second element of h_start_stop in h_start
        x_start = x_start_stop[::2]
        x_stop = x_start_stop[1::2]
        h_start = h_start_stop[::2]
        h_stop = h_start_stop[1::2]

        AA = np.isin(x_start, x_min_temp)
        alpha = AA * (np.max((h_pot, np.concatenate(([0], h_pot[:-1]))), axis=0) - constants.threshold_draft) # pairwise maximum of h_pot and h_pot shifted by one
        beta = AA * (alpha - (h_start - constants.threshold_draft))

        I1 = beta < 0.5 * alpha
        delta = AA * (2 * (alpha - beta) + constants.threshold_draft)
        I2 = AA * np.min((h_pot, np.concatenate(([0], h_pot[:-1]))), axis=0) < delta

        I3 = np.logical_or(I1, I2)

        x_start = x_start[np.where(I3 == 0)]
        h_start = h_start[np.where(I3 == 0)]
        x_stop = np.delete(x_stop, np.where(np.concatenate((I3[1:], [False]))))  
        h_stop = np.delete(h_stop, np.where(np.concatenate((I3[1:], [False]))))

        current = np.logical_and(I3, np.sign(h_pot - np.max((h_pot, np.concatenate(([0], h_pot[:-1]))), axis=0))) # combine I3 with all signs unequal to 0
        last = np.logical_xor(I3, current)

        not_curr_or_last = np.where(np.logical_and(current == 0, np.concatenate((last[1:], [0])) == 0))
        h_pot = h_pot[not_curr_or_last]
        x_pot = x_pot[not_curr_or_last]

        iteration_index += 1
        trigger = sum(I3)
        print(f"Deleted objects: {trigger}")

    return x_pot, h_pot



    

