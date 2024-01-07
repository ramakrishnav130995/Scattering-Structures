from gdshelpers.layout import GridLayout
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.text import Text
import numpy as np

from ..devices.devices import InputOutputDevices

kwargs = {
    "wg_width": 2,
    "wg_length": 3
}
io_devices = InputOutputDevices(wg_width=2, wg_length = 3e3)

n_repeat = 4
n_hor = 16
vert_space = 5000  # [um]
hor_space = 125  # [um]

# write positional arrays
x_pos = np.arange(0, n_hor*hor_space, n_hor)

layout = GridLayout(title=None, frame_layer=0, text_layer=2, region_layer_type=None, vertical_spacing=vert_space,
                    text_size=500, horizontal_spacing=1, horizontal_alignment=127)

# ---------------
# write first row of calibration devices
# ---------------

for x in x_pos:
    cell = InputOutputDevices.calibration_with_gratings(origin=(x,0))
    layout.add_to_row(cell)
    test = 1

# write and save chip
layout_cell, mapping = layout.generate_layout()
layout_cell.save("test_chip")