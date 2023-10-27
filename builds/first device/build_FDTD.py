from read_hdf5_reader import *  # Importing a custom module
from scattering_structure.scattering_structure import ScatteringStructure

import importlib.util
import os

# Add the DLL directory
os.add_dll_directory("C:\\Program Files\\Lumerical\\v232\\api\\python")

# Define the module name and file path
module_name = "lumapi"
# file_path = "C:\\Program Files\\Lumerical\\v232\\api\\python\\lumapi.py"
file_path = "C:\\Program Files\\Lumerical\\v232\\api\\python\\lumapi.py"


def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load the module
lumapi = load_module_from_file(module_name, file_path)


def build_FDTD(distribution_file: str, lumerical_name: str, injection_angle=0):
    ## Constants
    wavelength_start = 1.5
    wavelength_stop = 1.6
    block_length = 210
    block_width = 210
    simulation_height = 20
    modes = 100


    WG = {
        "length": block_length,
        "width": block_width,
        "height": 0.22,
        "matname": "Si3N4 (Silicon Nitride) - Luke"
    }

    BOX = {
        "length": block_length,
        "width": block_width,
        "height": 3,
        "matname": "SiO2 (Glass) - Palik"
    }

    SUB = {
        "length": block_length,
        "width": block_width,
        "height": 1,
        "matname": "Si (Silicon) - Palik"
    }

    RING = {
        "inner radius": 0.9384,
        "outer radius": 1.3432,
        "height": 0.070,
        "matname": "etch"
    }

    #########################################
    # SiO2, Si3N4, Air stack
    #########################################
    fdtd = lumapi.FDTD()
    # Si
    fdtd.addrect()
    fdtd.set('name', 'SUB')
    coordinates = {"x": 0,
                   "x span": SUB["length"] * 1e-6,
                   "y": 0,
                   "y span": SUB["width"] * 1e-6,
                   "z min": 0,
                   "z max": SUB["height"] * 1e-6}
    fdtd.set(coordinates)
    fdtd.select('SUB')
    fdtd.set('material', SUB["matname"])
    # default settings
    fdtd.set('color opacity', 0.5)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 3)
    # SiO2
    fdtd.addrect()
    fdtd.set('name', 'BOX')
    coordinates = {"x": 0,
                   "x span": BOX["length"] * 1e-6,
                   "y": 0,
                   "y span": BOX["width"] * 1e-6,
                   "z min": SUB["height"] * 1e-6,
                   "z max": (SUB["height"] + BOX["height"]) * 1e-6}
    fdtd.set(coordinates)
    fdtd.select('BOX')
    fdtd.set('material', BOX["matname"])
    # default settings
    fdtd.set('color opacity', 0.5)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 3)
    # Si3N4
    fdtd.addrect()
    fdtd.set('name', 'WG')
    coordinates = {"x": 0,
                   "x span": WG["length"] * 1e-6,
                   "y": 0,
                   "y span": WG["width"] * 1e-6,
                   "z min": (SUB["height"] + BOX["height"]) * 1e-6,
                   "z max": (SUB["height"] + BOX["height"] + WG["height"]) * 1e-6}
    fdtd.set(coordinates)
    fdtd.select('WG')
    fdtd.set('material', WG["matname"])
    # default settings
    fdtd.set('color opacity', 0.5)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 3)

    #########################################
    # Add rings
    #########################################
    # get the distribution
    load_pois = ScatteringStructure(geometry={'type': 'load_from_file'},
                                    arrangement={'type': 'load_from_file',
                                                 'filepath': distribution_file},
                                    scatterer_radius=1.343
                                    )
    i = 0
    for (x, y) in load_pois.get_reduced_points():
        name = str(i)
        fdtd.addring()
        fdtd.set('name', name)
        coordinates = {"x": x * 1e-6,
                       "y": y * 1e-6,
                       "z": 20 * 1e-6,
                       "z span": RING["height"] * 1e-6,
                       "inner radius": RING["inner radius"] * 1e-6,
                       "outer radius": RING["outer radius"] * 1e-6}
        fdtd.set(coordinates)
        fdtd.select(name)
        fdtd.set('material', RING["matname"])
        # fdtd.set('addtogroup', 'RINGS')
        # default settings
        fdtd.set('color opacity', 0.5)
        fdtd.set('override mesh order from material database', 1)
        fdtd.set('mesh order', 1)
        fdtd.addtogroup("RINGS")
        i += 1

        # save file as is
    fdtd.save("first_device.fsp")
    #########################################
    # Add solver
    #########################################
    configuration = {
        "FDTD": {
            "simulation time": 200e-15,  # in seconds
            "dimension": "3D",
            "x": 0,
            "y": 0.0,
            "z min": 0.0,
            "x span": block_length * 1e-6,
            "y span": block_width * 1e-6,
            "z max": simulation_height * 1e-6,
            "mesh accuracy": 1,
            "min mesh step": 0.025 * 1e-6
        }
    }

    # add solver
    fdtd.addfdtd()
    for key, value in configuration["FDTD"].items():
        fdtd.setnamed("FDTD", key, value)

    # add boundary conditions
    # is PMC by default

    #########################################
    # Add sources
    #########################################
    configuration = {
        "gaussian": {
            "name": "gaussian",
            "x": 0,
            "x span": block_length * 1e-6,
            "y": 0,
            "y span": block_width * 1e-6,
            "z": simulation_height * 1e-6,
            "waist radius w0": 50 * 1e-6,
            "direction": "Backward",
            "wavelength start": wavelength_start * 1e-6,
            "wavelength stop": wavelength_stop * 1e-6,
            "injection axis": "z",
            "theta": injection_angle
        }
    }

    # add gaussian source
    fdtd.addgaussian()
    for key, value in configuration["gaussian"].items():
        fdtd.setnamed("gaussian", key, value)

    #########################################
    # Add mesh constraint
    #########################################

    #########################################
    # Add monitors
    #########################################