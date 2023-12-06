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


def build_FDTD(lumerical_name: str, injection_angle=0):
    ## Constants
    wavelength_start = 1.5  # [um]
    wavelength_stop = 1.6  # [um]
    block_length = 210  # [um]
    block_width = 210  # [um]
    wg_mesh_step = 0.005


    AIR = {
        "length": block_length,
        "width": block_width,
        "height": 5,  # [um]
        "matname": "etch"
    }

    WG = {
        "length": block_length,
        "width": block_width,
        "height": 0.33,  # [um]
        "matname": "Si3N4 (Silicon Nitride) - Luke"
    }

    BOX = {
        "length": block_length,
        "width": block_width,
        "height": 3.3,  # [um]
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
        "x span": 150e-6,
        "y min": 1e-6,
        "y max": 25e-6,
        "z": 0,
        "mesh accuracy": 2,
        "min mesh step": 25e-9
    }

    PORT1 = {
        "injection axis": "y",
        "direction": "backward",
        "theta": injection_angle,
        "x": 0,
        "x span": 60*1e-6,
        "y": 25*1e-6,
        "z": 0,
        "z span": 60*1e-6
    }

    MOVIE = {
        "name": "2D z normal",
        "monitor type": "2D z-normal",
        "x": 0,
        "x span": 100e-6,
        "y min": 0,
        "y max": 25e-6,
        "z": 0,
        "horizontal resolution": 2000,
        "vertical resolution": 500,
    }

    MONITOR_1 = {
        "name": "monitor_1",
        "monitor type": "Linear Y",
        "x": 35e-6,
        "y min": 8.3e-6,
        "y max": 8.63e-6,
        "z": 0
    }

    MONITOR_2 = {
        "name": "monitor_2",
        "monitor type": "Linear Y",
        "x": -35e-6,
        "y min": 8.3e-6,
        "y max": 8.63e-6,
        "z": 0
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

    # Air
    fdtd.addrect()
    fdtd.set('name', 'AIR')
    coordinates = {
        "x": 0,
        "x span": WG["length"] * 1e-6,
        "y min": (WG["height"] + SUB["height"] + BOX["height"]) * 1e-6,
        "y max": (WG["height"] + SUB["height"] + BOX["height"] + AIR["height"]) * 1e-6,
        "z": 0,
        "z span": WG["width"] * 1e-6  # Width of Si3N4
    }
    fdtd.set(coordinates)
    fdtd.select('AIR')
    fdtd.set('material', AIR["matname"])
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
    x_offset = np.sin(np.deg2rad(injection_angle)) * FDTD["y max"]
    coordinates = {
        "x": 0 + x_offset,
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
        "x": 0 + x_offset,
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
    # All PML

    # change wavelength in solver manually
    fdtd.setglobalsource("wavelength start", wavelength_start*1e-6)
    fdtd.setglobalsource("wavelength stop", wavelength_stop*1e-6)

    #########################################
    # Add Ports
    #########################################

    # Add port 1
    fdtd.addport()
    fdtd.set("name", "input_port")
    for key, value in PORT1.items():
        fdtd.set(key, value)

    # select first order TE mode
    # fdtd.select("FDTD::ports")
    # fdtd.set("source port", "input_port")
    #########################################
    # Add mesh constraint
    #########################################

    #########################################
    # Add monitors
    #########################################

    # Add movie monitor
    fdtd.addmovie()
    for key, value in MOVIE.items():
        fdtd.set(key, value)

    # Add monitor 1
    fdtd.addpower()
    for key, value in MONITOR_1.items():
        fdtd.set(key, value)

    # Add monitor 2
    fdtd.addpower()
    for key, value in MONITOR_2.items():
        fdtd.set(key, value)

    #########################################
    # Save
    #########################################
    fdtd.save(lumerical_name)

    return fdtd


def build_crystal(fdtd, **kwargs):
    dimension = kwargs["dimension"]
    crystal_constant = kwargs["crystal_constant"]
    scatterer_type = kwargs["scatterer"]
    scatterer_kwargs = kwargs["scatterer_kwargs"]

    # Define crystal structure
    def mirrored(maxval, inc=1):
        x = np.arange(inc, maxval, inc)
        return np.r_[-x[::-1], 0, x]

    arr = np.array(mirrored(maxval=dimension/2, inc=crystal_constant))
    point_tuples = np.array(np.meshgrid(arr, arr)).T.reshape(-1, 2)

    # Add scatterers in defined crystal order into given fdtd

    fdtd.select("WG")
    y_max = fdtd.get("y max")*1e6
    # delete old crystal
    fdtd.select("CRYSTAL")

    fdtd.delete()

    for point in point_tuples:
        # for now restrict to 2D
        if point[1] == 0:
            coordinates = {
                "x": point[0] * 1e-6,
                "z": point[1] * 1e-6,
                "y": (y_max - 0.5 * scatterer_kwargs["depth"]) * 1e-6,
                "z span": scatterer_kwargs["depth"] * 1e-6,
                "first axis": "x",
                "rotation 1": 90}
            if scatterer_type == "CIRCLE":
                fdtd.addcircle()
                fdtd.set("name", "circle")
                coordinates["radius"] = scatterer_kwargs["radius"]*1e-6
            elif scatterer_type == "RING":
                fdtd.addring()
                fdtd.set("name", "ring")
                coordinates["inner radius"] = scatterer_kwargs["inner_radius"]*1e-6
                coordinates["outer radius"] = scatterer_kwargs["outer_radius"]*1e-6
            else:
                raise ValueError("Invalid scatterer type")
            fdtd.set(coordinates)
            fdtd.set("material", scatterer_kwargs["matname"])
            fdtd.set("color opacity", 0.5)
            fdtd.set("override mesh order from material database", 1)
            fdtd.set("mesh order", 1)
            fdtd.addtogroup("CRYSTAL")
