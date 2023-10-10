import sys, os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import savemat
from read_hdf5_reader import *  # Importing a custom module

from tabulate import tabulate  # Importing the 'tabulate' module

# Clear the console screen (works on Windows)
os.system("cls")

# Default path for current release
sys.path.append("C:\\Program Files\\Lumerical\\v231\\api\\python\\")
sys.path.append(os.path.dirname(__file__))  # Current directory

import lumapi  # Import the 'lumapi' module

## Define new project Details:

# Define materials
# SiO2 (Glass) - Palik
# etch
# Si (Silicon) - Palik
# Si3N4 (Silicon Nitride) - Luke
# PIXEL-TAO205
# PIXEL-SiO2

########### Design is in XY plane: x- length, y-height, and z-width ###########

wavelength = 0.925  # Wavelength in microns
modes = 6

WG_height = 0.300
BOX_height = 2.7

N = 50
N_uni = 10
Lambda = 0.845
ff_in = 0.94
ff_fin = 0.6

# Define TOX parameters
TOX = {
    "TOXlength": 80,
    "TOXheight": 2.6,
    "TOXwidth": 50,
    "TOXmatname": "etch",
}

# Define WG parameters
WG = {
    "WGlength": TOX["TOXlength"],
    "WGheight": WG_height,
    "WGwidth": 1.3,
    "WGmatname": "Si3N4 (Silicon Nitride) - Luke",
}

matname = "SiN"

# Define BOX parameters
BOX = {
    "BOXlength": TOX["TOXlength"],
    "BOXheight": BOX_height,
    "BOXwidth": 50,
    "BOXmatname": "SiO2 (Glass) - Palik",
}

# Define SUB parameters
SUB = {
    "sublength": TOX["TOXlength"],
    "subheight": 525,
    "subwidth": 50,
    "submatname": "Si (Silicon) - Palik",
}

# Define UGC parameters
UGC = {
    "etch_ht": WG["WGheight"],
    "etch_mat": TOX["TOXmatname"],
    "F_val": 0.75,
    "theta": 12,
    "inputwglength": 4,
    "outputwglength": 4,
    "gratinglength": 70,
}

if (
    UGC["inputwglength"] + UGC["outputwglength"] + UGC["gratinglength"]
    > TOX["TOXlength"]
):
    UGC["outputwglength"] = TOX["TOXlength"] - (
        UGC["inputwglength"] + UGC["gratinglength"]
    )

# Define parent directory
parent_dir = r"C:/Users/RamakrishnaVenkitakr/OneDrive - Pixel Photonics GmbH/Projects/2D_coupler_project/simulations/2D_coupler"
parent_dir = os.path.join(
    parent_dir, "Lumerical_Trials", "September_2023"
)

# Define new folder name
new_folder_name = (
    matname
    + "_"
    + str(int(wavelength * 1000))
    + "_twg_"
    + str(int(WG["WGheight"] * 1000))
)

# Create new directory structure if it doesn't exist
path = os.path.join(parent_dir, new_folder_name)
results_path = os.path.join(path, "results")

if os.path.isdir(path) is False:
    os.mkdir(path)
    os.mkdir(results_path)
    os.mkdir(os.path.join(results_path, "WG"))
    print("Directory '%s' created" % new_folder_name)
else:
    print("Directory ' %s' Already Exist")

lsfpath = r"C:\Users\RamakrishnaVenkitakr\OneDrive - Pixel Photonics GmbH\Projects\2D_coupler_project\grating_coupler_lsf"

savepath = path  ##Default save in the new directory

print("save path is " + savepath)

def waveguide_mode_analysis():
    # Create a MODE object
    mode1 = lumapi.MODE(hide=True)

    # Read and evaluate code from a file
    code = open(lsfpath + "/function_Waveguide_design.lsf").read()
    mode1.eval(code)

    # Perform WG analysis
    mode1.WG_analysis(TOX, WG, BOX, SUB, UGC, wavelength, modes, savepath)
    print("Waveguide simulation over\n")

def open_file(path, folder_name):
    simulationCMD = os.path.join(path, folder_name + ".fsp")
    engineCMD = '"C:\\Program files\\Lumerical\\v231\\bin\\fdtd-solutions.exe" -run '
    fullcmd = engineCMD + '"' + simulationCMD + '"'
    print('start "name" /B ' + fullcmd)
    lumapi.FDTD().system('start "name" /B ' + fullcmd)

def main():
    waveguide_mode_analysis()
    path = r""  # Add the actual path
    folder_name = ""  # Add the actual folder name
    open_file(path, folder_name)

if __name__ == "__main__":
    main()
