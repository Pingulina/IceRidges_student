# load the data from the json file and return numpy arrays
import json
import os
import numpy as np

def json2numpy(file_path:str, loc_mooring:str):
    """Load the data from a json file and return numpy arrays
    :param file_path: path to the json file
    :type file_path: str
    :param loc_mooring: location of the mooring
    :type loc_mooring: str
    :return: numpy arrays
    :rtype: dict
    """
    try:
        data = json.load(open(file_path))
    except FileNotFoundError:
        sucess = False
        dateNum = None
        draft = None
        draft_mode = None
        return sucess, dateNum, draft, draft_mode
    data = data[loc_mooring] # get the data for the location
    dateNum = np.array(data['dateNum'])
    draft = np.array(data['draft'])
    if 'draft_mode' in data:
        draft_mode = np.array(data['draft_mode'])
    else:
        draft_mode = None
    sucess = True

    return sucess, dateNum, draft, draft_mode
