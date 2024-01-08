import os
from gdshelpers.layout import GridLayout
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.text import Text
from gdshelpers.parts.port import Port
import numpy as np
from math import pi
from GDS_designs.devices import InputOutputDevices

# straight waveguide params
wg_length = 500

# grid params
n_repeat = 4
n_hor = 16
vert_space = 5000  # [um]
hor_space = 500  # [um]

coupler_params = {
    'width': 1.3,
    'full_opening_angle': np.deg2rad(40),
    'grating_period': 0.88,
    'grating_ff': 0.60,
    'n_gratings': 20,
    'taper_length': 16.
}
io_devices = InputOutputDevices(wg_length=wg_length)

# write positional arrays
x_pos = np.arange(0, n_hor * hor_space, n_hor)

layout = GridLayout(title=None, frame_layer=0, text_layer=2, region_layer_type=None, vertical_spacing=vert_space,
                    text_size=500, horizontal_spacing=hor_space, horizontal_alignment=127)

# ---------------
# write first row of calibration devices
# ---------------

# Start a new row
layout.begin_new_row()

for x in x_pos:
    cell = io_devices.calibration_with_gratings(origin=(0, 0), cell_name=str(x), coupler_params=coupler_params)
    layout.add_to_row(cell)

# write and save chip
layout_cell, mapping = layout.generate_layout()
layout_cell.save("test_chip")
