import importlib.util
import os

import numpy as np

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


def build_FDTD(lumerical_name: str, crystal_constant, fiber_mode, injection_angle=0):
    ## Constants
    wavelength_start = 1.5  # [um]
    wavelength_stop = 1.6  # [um]
    block_length = 210  # [um]
    block_width = 210  # [um]
    simulation_height = 20  # [um]
    modes = 100
    min_mesh_step = 0.05
    wg_mesh_step = 0.005


    WG = {
        "length": block_length,
        "width": block_width,
        "height": 0.22,  # [um]
        "matname": "Si3N4 (Silicon Nitride) - Luke"
    }

    BOX = {
        "length": block_length,
        "width": block_width,
        "height": 3,  # [um]
        "matname": "SiO2 (Glass) - Palik"
    }

    SUB = {
        "length": block_length,
        "width": block_width,
        "height": 5,  # [um]
        "matname": "Si (Silicon) - Palik"
    }

    FIBER = {
        "z span": 100,  # [um]
        'CORE': {
            "radius": 25,  # [um]
            "matname": "SiO2 (Glass) - Palik"
        },
        'CLADDING': {
            "radius": 125/2,  # [um]
            "index": 1.4271426  # NA = 0.22, n_core = 1.444
        }
    }

    FDTD = {
        "simulation time": 2000e-15,  # in seconds
        "dimension": "2D",
        "x": 0,
        "x span": 0.8 * block_length * 1e-6,
        "y min": 2e-6,
        "y max": 35e-6,
        "z": 0,
        "mesh accuracy": 2,
        "min mesh step": min_mesh_step * 1e-6
    }

    PORT1 = {
        "injection axis": "y",
        "direction": "backward",
        "theta": injection_angle,
        "x": 0,
        "x span": 80*1e-6,
        "y": 20*1e-6,
        "z": 0,
        "z span": 80*1e-6
    }

    #########################################
    # SiO2, Si3N4, Air stack
    #########################################
    fdtd = lumapi.FDTD()

    # Si
    fdtd.addrect()
    fdtd.set('name', 'SUB')
    coordinates = {
        "x": 0,
        "x span": SUB["length"] * 1e-6,
        "y min": 0,
        "y max": SUB["height"] * 1e-6,  # Height now represents the y span
        "z": 0,  # Z-coordinate starts at 0
        "z span": SUB["width"] * 1e-6  # Width now represents the z span
    }
    fdtd.set(coordinates)
    fdtd.select('SUB')
    fdtd.set('material', SUB["matname"])
    # Default settings
    fdtd.set('color opacity', 0.5)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 3)

    # SiO2
    fdtd.addrect()
    fdtd.set('name', 'BOX')
    coordinates = {
        "x": 0,
        "x span": BOX["length"] * 1e-6,
        "y min": SUB["height"] * 1e-6,  # Start from Si height
        "y max": SUB["height"] * 1e-6 + BOX["height"] * 1e-6,  # Height of SiO2
        "z": 0,
        "z span": BOX["width"] * 1e-6  # Width of SiO2
    }
    fdtd.set(coordinates)
    fdtd.select('BOX')
    fdtd.set('material', BOX["matname"])
    # Default settings
    fdtd.set('color opacity', 0.5)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 3)

    # Si3N4
    fdtd.addrect()
    fdtd.set('name', 'WG')
    coordinates = {
        "x": 0,
        "x span": WG["length"] * 1e-6,
        "y min": (SUB["height"] + BOX["height"]) * 1e-6,  # Start from SiO2 height
        "y max": (WG["height"] + SUB["height"] + BOX["height"]) * 1e-6,  # Height of Si3N4
        "z": 0,
        "z span": WG["width"] * 1e-6  # Width of Si3N4
    }
    fdtd.set(coordinates)
    fdtd.select('WG')
    fdtd.set('material', WG["matname"])
    # Default settings
    fdtd.set('color opacity', 0.5)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 3)

    #########################################
    # Add fiber
    #########################################
    # Add fiber core
    fdtd.addcircle()
    fdtd.set('name', 'CORE')
    coordinates = {
        "x": 0,
        "y": 0,
        "z": 0,
        "z span": FIBER["z span"] * 1e-6,
        "radius": FIBER["CORE"]["radius"] * 1e-6,
        "first axis": "x",
        "rotation 1": 90,
        "second axis": "z",
        "rotation 2": injection_angle
    }
    fdtd.set(coordinates)
    fdtd.select('CORE')
    fdtd.set('material', FIBER["CORE"]["matname"])
    fdtd.set('color opacity', 0.3)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 4)
    fdtd.addtogroup('FIBER')

    # Add fiber cladding
    fdtd.addcircle()
    fdtd.set('name', 'CLADDING')
    coordinates = {
        "x": 0,
        "y": 0,
        "z": 0,
        "z span": FIBER["z span"] * 1e-6,
        "radius": FIBER["CLADDING"]["radius"] * 1e-6,
        "first axis": "x",
        "rotation 1": 90,
        "second axis": "z",
        "rotation 2": injection_angle
    }
    fdtd.set(coordinates)
    fdtd.select('CLADDING')
    fdtd.set('index', FIBER["CLADDING"]["index"])
    fdtd.set('color opacity', 0.3)
    fdtd.set('override mesh order from material database', 1)
    fdtd.set('mesh order', 5)
    fdtd.addtogroup('FIBER')


    #########################################
    # Add solver
    #########################################

    # and solver
    fdtd.addfdtd()
    for key, value in FDTD.items():
        fdtd.setnamed("FDTD", key, value)
    # add BCs

    #########################################
    # Add Ports
    #########################################

    # Add port 1
    fdtd.addport()
    fdtd.set("name", "input port")
    for key, value in PORT1.items():
        fdtd.set(key, value)

    #########################################
    # Add mesh constraint
    #########################################

    #########################################
    # Add monitors
    #########################################


    #########################################
    # Save
    #########################################
    fdtd.save(lumerical_name)

    return fdtd