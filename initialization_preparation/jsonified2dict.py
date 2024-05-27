# function to store a dictionary in a json file, converting the numpy arrays to lists
import json
import numpy as np



def handle_dict(d):
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
        if v['type'] == 'dict':
            out[k] = handle_dict(v)
        elif v['type'] == np.ndarray.__name__: # 'numpy.ndarray'
            out[k] = np.array(v['data'])
        elif  v['type'] == 'list of numpy.ndarray':
            out[k] = [np.array(i) for i in v['data']]
        elif v['type'] in [np.int_.__name__, np.intc.__name__, np.intp.__name__, np.int8.__name__, np.int16.__name__, np.int32.__name__, np.int64.__name__, np.uint8.__name__, np.uint16.__name__, np.uint32.__name__, np.uint64.__name__]:
            out[k] = int(v['data'])
        elif v['type'] in [np.float_.__name__, np.float16.__name__, np.float32.__name__, np.float64.__name__]:
            out[k] = float(v['data'])
        elif v['type'] in [bool.__name__, np.bool_.__name__]:
            out[k] = bool(v['data'])
        elif v['type'] in [f"list of {bool.__name__}", f"list of {np.bool_.__name__}"]:
            out[k] = [bool(i) for i in v['data']]
        else:
            out[k] = v['data']
    return out

def jsonified2dict(dict_data:dict):
    """Converting numpy stuff back to numpy
    :param dict_data: dictionary to store in the json file
    :type dict_data: dict
    :type file_path: str
    """
    dict_withNp = handle_dict(dict_data)

    return dict_withNp