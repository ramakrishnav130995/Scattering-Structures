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
    # 2D y-normal monitor
    y_normal_configuration = {
        "monitor type": 6,  # 2D y normal
        "y": 0.0,
        "z min": 0.0,
        "x span": block_length * 1e-6,
        "z max": simulation_height * 1e-6,
    }
    fdtd.addpower()
    fdtd.set("name", "2D Y-normal")
    # set geometry
    for key, value in y_normal_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("Monitors")

    # 2D x-normal monitor
    y_normal_configuration = {
        "monitor type": 5,  # 2D x normal
        "x": 0.0,
        "z min": 0.0,
        "y span": block_width * 1e-6,
        "z max": simulation_height * 1e-6,
    }
    fdtd.addpower()
    fdtd.set("name", "2D X-normal")
    # set geometry
    for key, value in y_normal_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("Monitors")

    # slab-edge monitor(s)
    # four individual monitors have to be added.
    slab_edge_configuration = {
        "monitor type": 6,  # 2D y normal
        "y": -0.5 * block_width * 1e-6,
        "x": 0,
        "x span": block_length * 1e-6,
        "z min": (SUB["height"] + BOX["height"]) * 1e-6,
        "z max": (SUB["height"] + BOX["height"] + WG["height"]) * 1e-6,
    }
    fdtd.addpower()
    fdtd.set("name", "1")
    # set geometry
    for key, value in slab_edge_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("WG edge monitor(s)")
    #########################
    slab_edge_configuration = {
        "monitor type": 6,  # 2D y normal
        "y": +0.5 * block_width * 1e-6,
        "x": 0,
        "x span": block_length * 1e-6,
        "z min": (SUB["height"] + BOX["height"]) * 1e-6,
        "z max": (SUB["height"] + BOX["height"] + WG["height"]) * 1e-6,
    }
    fdtd.addpower()
    fdtd.set("name", "2")
    # set geometry
    for key, value in slab_edge_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("WG edge monitor(s)")
    #########################
    slab_edge_configuration = {
        "monitor type": 5,  # 2D y normal
        "x": -0.5 * block_length * 1e-6,
        "y": 0,
        "y span": block_width * 1e-6,
        "z min": (SUB["height"] + BOX["height"]) * 1e-6,
        "z max": (SUB["height"] + BOX["height"] + WG["height"]) * 1e-6,
    }
    fdtd.addpower()
    fdtd.set("name", "3")
    # set geometry
    for key, value in slab_edge_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("WG edge monitor(s)")
    #########################
    slab_edge_configuration = {
        "monitor type": 5,  # 2D y normal
        "x": +0.5 * block_length * 1e-6,
        "y": 0,
        "y span": block_width * 1e-6,
        "z min": (SUB["height"] + BOX["height"]) * 1e-6,
        "z max": (SUB["height"] + BOX["height"] + WG["height"]) * 1e-6,
    }
    fdtd.addpower()
    fdtd.set("name", "4")
    # set geometry
    for key, value in slab_edge_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("WG edge monitor(s)")
    fdtd.select("WG edge monitor(s)")
    fdtd.addtogroup("Monitors")

    # substrate monitor
    substrate_configuration = {
        "monitor type": 3,  # 2D z normal
        "x": 0.0,
        "y": 0.0,
        "x span": block_length * 1e-6,
        "y span": block_width * 1e-6,
        "z": 0.0,
    }
    fdtd.addpower()
    fdtd.set("name", "2D z-normal SUB monitor")
    # set geometry
    for key, value in substrate_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("Monitors")

    # air monitor
    air_configuration = {
        "monitor type": 3,  # 2D z normal
        "x": 0.0,
        "y": 0.0,
        "x span": block_length * 1e-6,
        "y span": block_width * 1e-6,
        "z": simulation_height * 1e-6,
    }
    fdtd.addpower()
    fdtd.set("name", "2D z-normal Air monitor")
    # set geometry
    for key, value in air_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("Monitors")

    # movie monitor
    movie_configuration = {
        "monitor type": 1,  # 2D x normal
        "x": 0,
        "y": 0,
        "y span": block_width * 1e-6,
        "z": 0,
        "z span": simulation_height * 1e-6,
        "horizonal resolution": 100,
        "vertical resolution": 100, # TODO with mesh size
    }
    fdtd.addmovie()
    fdtd.set("name", "2D x-normal movie monitor")
    # set geometry
    for key, value in movie_configuration.items():
        fdtd.set(key, value)
    fdtd.addtogroup("Monitors")

    # movie monitor 2D z normal in WG
    movie_configuration = {
        "monitor type": 3,  # 2D z normal
        "x": 0,
        "y": 0,
        "x span": block_length * 1e-6,
        "y span": block_width * 1e-6,
        "z": 0,
        "horizonal resolution": 100,
        "vertical resolution": 100, # TODO with mesh size
    }
    fdtd.addmovie()
    fdtd.set("name", "2D z-normal WG movie monitor")
    fdtd.addtogroup("Monitors")

    #########################################
    # Save
    #########################################
    fdtd.save(name=lumerical_name + ".fsp")
