import os
import sys

def import_module(module_name, module_dir_relative_to_cwd):
    # Get the current working directory
    cwd = os.getcwd()

    # Construct the path to your module directory
    module_dir = os.path.join(cwd, module_dir_relative_to_cwd)

    # Add the module directory to sys.path
    sys.path.insert(0, module_dir)

    # Dynamically import the module using the built-in __import__ function
    module = __import__(module_name)

    if module_name[0:9] == 'constants':
        return module.constants
    elif module_name == 'myColor':
        return module.myColor

    return module
