# example run of rayleigh_criterion.py (equivalent to S002_Rayleigh_critera_example.m):

import numpy as np
import matplotlib.pyplot as plt
import json
import os

import helper_functions.rayleigh_criterion as rc

position = 'a'
test_year = 2004
test_name = f"uls{str(test_year)[2:]}{position}_draft.json"
# load the data from folder mooring_data in Data. It is a json file
pathName = os.getcwd()
data = json.load(open(os.path.join(pathName, 'Data', 'mooring_data', f"{test_year}-{test_year+1}", test_name)))

x, h = rc.rayleigh_criterion(data['dateNum'], data['draft'], threshold_draft=2.5, min_draft=5.0)

# plot the data and the found independent points
rc_fig = plt.figure()
rc_ax = rc_fig.add_subplot(111)
rc_ax.plot(data['dateNum'], data['draft'], linewidth=0.5, color='#4575b4')
rc_ax.plot(x, h, 'o', markersize=5, markerfacecolor='none', markeredgecolor='#d73027')
rc_fig.show()

print('done!')