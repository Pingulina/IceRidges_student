# this file is used to initialize the python environment
# this includes installing all the necessary packages

import os
import subprocess

def initialize_python():
    """
    Initialize the python environment and install the necessary packages
    :return: None
    """
    # ask the user, if the anaconda environment is already initiated
    # if yes, ask for the name of the environment
    # if no, ask for the name of the environment and create it
    print("""Welcome to the python environment initialization. 
        I will guide you through the setup process for the conda environment and the necessary packages.""")

    package_list = ['numpy', 'matplotlib', 'conda-forge::pynput', 'json', 'datetime', 'sys']

    while True:
        env_exist = input("Do you have an anaconda environment initiated? - Y, N:")
        if env_exist == 'Y' or env_exist == 'y':
            print("Please enter the name of the existing environment")
            env_name = input("Environment name: ")
            print("Activating the environment")
            try:
                os.system(f"conda activate {env_name}")
            except:
                print("Environment not found. Try again.")
            else:
                print("Environment activated")
                break
        elif env_exist == 'N' or env_exist == 'n':
            print("Please enter the name of the environment you want to create")
            env_name = input("Environment name: ")
            print("Creating the environment")
            try:
                os.system(f"conda create --name {env_name} python=3.11")
            except:
                print("Environment already exists. Try again.")
                continue
            else:
                print(f"Environment {env_name} created")
                print("Activating the environment")
                os.system(f"conda activate {env_name}")
                print("Environment activated")
                break
        else:
            print("Invalid input. Use Y/y or N/n. Try again.")
            continue

    # install the necessary packages
    print("""Installing the necessary packages. 
        \nThis may take a while. Please accept the installation of the packages by typing 'y' and pressing enter. 
        Otherwise, the installation of the current package will be aborted and the next package will be handled.""")

    for package in package_list:
        print(f"Installing {package}")
        os.system(f"conda install -n {env_name} {package}")

    # check if the installation was successful
    print("Checking the installation")
    number_packages = len(package_list)
    number_success = 0
    for package in package_list:
        try:
            subprocess.check_output(f"conda list -n {env_name} {package}", shell=True)
        except subprocess.CalledProcessError:
            print(f"Installation of {package} failed. Try again.")
        else:
            print(f"{package} installed successfully")
            number_success += 1

    print(f"Environment initialization completed, installed {number_success} out of {number_packages} packages successfully.")