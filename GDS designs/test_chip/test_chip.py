import os

# Set the GEOS_LIBRARY_PATH environment variable
os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/Cellar/geos/3.12.1/lib/'  # Adjust the path accordingly



from gdshelpers.layout import GridLayout
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.text import Text
import numpy as np


class InputOutputDevices:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def calibration_with_gratings(self, origin):
        wg_width = self.kwargs["wg_width"]
        wg_length = self.kwargs["wg_length"]
        # -----------------------------
        # Input Grating Coupler
        # -----------------------------
        coupler_in = GratingCoupler.make_traditional_coupler_from_database(
            origin, wg_width, 'sn330', 1550)
        # -----------------------------
        # Straight Waveguide
        # -----------------------------
        wg = Waveguide.make_at_port(coupler_in.port)
        wg.add_straight_segment(length=wg_length)
        # -----------------------------
        # Output Grating Coupler
        # -----------------------------
        coupler_out = GratingCoupler.make_traditional_coupler_from_database(
            wg.current_port, 1, 'sn330', 1550)

        cell = Cell("CALIBRATION DEVICE")
        cell.add_to_layer(1, coupler_in, wg, coupler_out)
        return cell

    # def slab_with_scattering_structures:
        # TODO
        # return None

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

# Start a new row
layout.begin_new_row()

for x in x_pos:
    cell = io_devices.calibration_with_gratings(origin=(x, 0))
    layout.add_to_row(cell)
    test = 1

# write and save chip
layout_cell, mapping = layout.generate_layout()
layout_cell.save("test_chip")