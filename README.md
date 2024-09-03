# IceRidges Simulation

This simulation is based on the work by [Ilija Samardzija](https://github.com/ilijasam/IceRidges). Some background information about ridges and probabilistic modelling can be found in the [documentation](manual.pdf).

## Get the code
This code is organized in a git repository. If you have worked with git before, you can skip the following paragraph, it explains briefly what git is and how to use it.

### What is git?
Git is a tool that helps you keep track of changes you make to your files, especially when working on projects like writing code or creating documents. Think of it as a supercharged "undo" button that not only lets you go back to previous versions of your work but also helps you see what changes were made and who made them. It's especially useful when working with others because it allows everyone to work on the same project simultaneously without overwriting each other's work. You can think of Git as a digital filing cabinet that keeps everything organized and makes collaboration smooth and efficient. For more information, you can visit the official Git website. [official website](https://git-scm.com/).

### How to get git
To get the code, you need to have git installed on your computer. If you don't have it yet, you can [download git](https://git-scm.com/downloads) from the official website and install it on your computer. 

### How to use git
#### Cloning the repository
Cloning a repository means, that an instance of the code is downloaded to your computer. This way, you can work on the code locally and get the latest updates from the repository in an easy way.
We will use the terminal (on Windows, 'git bash' is a good option) for all git commands. In the following, only the expression 'terminal' is used, even though on windows no application called 'terminal' exists. Don't be affraid of the terminal, it's not as scary as it looks. All needed commands can be directly copied from here. Just one hint: don't use `ctrl` + `c` to copy in the terminal, becuase it will stop the current command. Use `crtl + shift + c` instead.

To clone the repository, open the terminal or command prompt and navigate to the folder where you want to store the code. In this example, we will store the code in `Documents` in a folder called `IceRidges`. To create this folder, type the following command and press enter:

```bash
cd Documents # navigate to the Documents folder
mkdir IceRidges # create a new folder called IceRidges
cd IceRidges # navigate to the IceRidges folder
```

---
**NOTE**

If your standard directory for documents is not `Documents` (e.g. because your computer is in a different language), you have to replace `Documents` with the name of your standard directory for documents.

---

Now, you find a new folder `IceRidges` in your `Documents` folder. You can clone the repository by typing the following command and pressing enter:

```bash
git clone https://github.com/Pingulina/IceRidges_student
```

This will download the code to your computer and initialize the git structure. You can now navigate to the `IceRidges_student` folder and start working with the code.

```bash	
cd IceRidges_student # navigate to the IceRidges_student folder
```

Now, you will find a folder called `IceRidges_student` in your `IceRidges` folder. This folder contains the code of the simulation. To run the code, you have to set up the environment and download the data as described [below](README.md#setting-up-the-environment).

#### Updating your code with git
To keep your code up to date, you have to pull the latest changes from the repository. Navigate to the `IceRidges_student` folder and update by the following command:

```bash
cd ./Documents/IceRidges/IceRidges_student # navigate to the IceRidges_student folder
git pull # pull the latest changes from the repository (like updating the code)
```


## Setting up the environment
### What is a Python environment?
A Python environment is like a special workspace on your computer where you can run Python programs. Think of it as a clean room where you can install all the tools and libraries you need for a specific project without affecting other projects or the rest of your computer. This way, you can have different projects with different requirements running smoothly side by side. For example, one project might need an older version of a tool, while another needs a newer version. By using separate environments, you can keep everything organized and avoid conflicts. Setting up a Python environment ensures that you have all the necessary components to run your code correctly.
Python environments are either setup using `pip` or `conda`. `pip` is the standard package manager for Python, while `conda` is a package manager that is especially useful for scientific computing and data science. In this project, we will use `conda` to set up the Python environment. The advantage of `conda` is that it can be controlled via a graphical user interface, which makes it easier to use for beginners. This graphical user interface is called Anaconda Navigator, the installation is described in the following section.

### Set up the Python environment
To set up the Python environment, the function `initialize_python.py` can be used. It will guide you through all necessary steps.
It requires a `conda` environment, then all needed packages are installed via `conda` automatically. It is recommended to use Anaconda to set up the Python environment. The simulation was set up by using `Python3.11.8`. \

To set up the `conda` environment, it is recommended to use [Anaconda](https://www.anaconda.com/download). Download and install [Anaconda](https://www.anaconda.com/download). 

Open the Anaconda Navigator and create a new environment. The environment can be named as you like. For example, you can name it `IceRidges`. The Python version should be `3.11` or newer. After creating the environment, open the terminal. On Windows, it is recommended to use the Powershell Prompt provided by Anaconda. You can find it on the starting page of the Anaconda Navigator. Then activate the environment by typing 
```bash
conda activate IceRidges
``` 
If you named your environment differently, replace `IceRidges` with the actual name of your environment. Navigate to the folder where the code is stored and run the `initialize_python.py` script by typing 
```bash
cd # with this, you navigate to your home directory
cd Documents/IceRidges/IceRidges_student # navigate to the folder where the code is stored
cd initialization_preparation # navigate to the initialization_preparation folder, we need to run a script from here
python initialize_python.py` # run the script
```
The script will guide you through the installation process. At some points, you have to confirm the installation by typing `y` and pressing `enter`.


Alternatively, you can set up your envinronment manually via conda or pip. Then you have to install all necessary packages manually. A list of all packages can be found in `initialize_python.py`. In general, this is not recommended, unless you are very familiar with python, the installation of packages and if you have to use pip for some reason.



## Data
The data used is available on [Woods Hole Oceanographic Institution](https://www2.whoi.edu/site/beaufortgyre/data/mooring-data/) (Accessed on March 07, 2024). Please download the .dat files for all time slots you want to simulate. 
Store the data in the `Data_Beaufort_Gyre_Exploration` folder with subfolders for every mooring season. The folder structure should look like this:

```bash
Data_Beaufort_Gyre_Exploration
│   2015-2016
│   │   uls15a_draft.dat
│   │   uls15b_draft.dat
│   │   ...
│   2016-2017
│   │   uls16a_draft.dat
│   │   uls16b_draft.dat
│   │   ...
|   ...
```
Make sure the folder name is equivalent with the actual season(s). Some of the mooring data are sampled over multiple years, so the folder name should reflect this (e.g. for the mooring data from 2018-2021, the folder name is `2018-2021`).

---
**NOTE:**
If you want to use your own data files, please make sure that they are in `.dat` format with columns `date` (int), `time` (int) and `draft` (float or double). Otherwise, you could use `.csv` files, but have to change the separation character in `data2json.py`.

---


## Starting the GUI
Please refer to the [GUI Manual](GUI_dash_plotly/README.md) for instructions on how to use the GUI.
