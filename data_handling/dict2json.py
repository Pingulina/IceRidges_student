# function to store a dictionary in a json file, converting the numpy arrays to lists
import json
import numpy as np



def dict2jsonable(d):
    """Recursively convert numpy arrays and numpy data types in a dictionary to lists and native python data types.
    :param d: dictionary to convert
    :type d: dict
    :return: dictionary with numpy arrays and numpy data types converted
    :rtype: dict
    """
    out = {}
    for k, v in d.items():
        # if out[k] doesn't exist, create it
        if k not in out:
            out[k] = {}
        if isinstance(v, dict):
            out[k] = dict2jsonable(v)
        elif isinstance(v, np.ndarray):
            out[k]['data'] = v.tolist()
            out[k]['type'] = type(v).__name__ # get the type of the variable as string # 'numpy.ndarray'
        elif  isinstance(v, list) and set(map(type, v)) == {np.ndarray}:
            out[k]['data'] = [i.tolist() for i in v]
            out[k]['type'] = 'list of numpy.ndarray' # type(v).__name__ # get the type of the variable as string # 'list of numpy.ndarray'
        elif isinstance(v, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
            out[k]['data'] = int(v)
            out[k]['type'] = type(v).__name__ # get the type of the variable as string #'numpy.int'
        elif isinstance(v, (np.float_, np.float16, np.float32, np.float64)):
            out[k]['data'] = float(v)
            out[k]['type'] = type(v).__name__ # get the type of the variable as string # 'numpy.float'
        else:
            out[k]['data'] = v
            out[k]['type'] = type(v).__name__ # get the type of the variable as string
    return out

def dict2json(dict_data:dict, file_path:str):
    """Store a dictionary in a json file, converting the numpy arrays to lists
    :param dict_data: dictionary to store in the json file
    :type dict_data: dict
    :param file_path: path to the json file
    :type file_path: str
    """
    dict_withoutNpArray = dict2jsonable(dict_data)
    with open(file_path, 'w') as file:
        json.dump(dict_withoutNpArray, file)
    return None