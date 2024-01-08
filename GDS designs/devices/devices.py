import os

# Set the GEOS_LIBRARY_PATH environment variable
os.environ['GEOS_LIBRARY_PATH'] = '/opt/homebrew/Cellar/geos/3.12.1/lib/libgeos.dylib'  # Adjust the path accordingly

from gdshelpers.layout import GridLayout
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.text import Text
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.port import Port
import numpy as np

class InputOutputDevices:
    def __innit__(self, **kwargs):
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
