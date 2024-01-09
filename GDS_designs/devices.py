import os
from gdshelpers.geometry.chip import Cell
from gdshelpers.parts.text import Text
from gdshelpers.parts.waveguide import Waveguide
from gdshelpers.parts.coupler import GratingCoupler
from gdshelpers.parts.port import Port
import numpy as np
from math import pi

class InputOutputDevices:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def calibration(self, origin, cell_name, coupler_params):
        wg_length = self.kwargs["wg_length"]
        wg_width = self.kwargs["wg_width"]
        bend_radius = self.kwargs["bend_radius"]

        in_coupler = GratingCoupler.make_traditional_coupler(origin, angle=+np.pi/2, **coupler_params)
        wg1 = Waveguide.make_at_port(in_coupler.port)
        # taper further down to wg_width
        wg1.add_straight_segment(length=50, final_width=wg_width)
        wg1.add_bend(-pi, radius=bend_radius)
        wg1.add_straight_segment(length=wg_length)
        wg1.add_bend(pi, radius=bend_radius)
        # taper up again
        wg1.add_straight_segment(length=50, final_width=coupler_params["width"])
        out_coupler = GratingCoupler.make_traditional_coupler_at_port(wg1.current_port, **coupler_params)

        cell = Cell(cell_name)
        cell.add_to_layer(1, in_coupler, wg1, out_coupler)
        return cell

    def calibration_without_offset(self, origin, cell_name, coupler_params):
        wg_length = self.kwargs["wg_length"]
        wg_width = self.kwargs["wg_width"]
        bend_radius = self.kwargs["bend_radius"]

        in_coupler = GratingCoupler.make_traditional_coupler(origin, angle=+np.pi / 2, **coupler_params)
        wg1 = Waveguide.make_at_port(in_coupler.port)
        # taper further down to wg_width
        wg1.add_straight_segment(length=50, final_width=wg_width)
        wg1.add_bend(-pi, radius=bend_radius)
        wg1.add_straight_segment(length=wg_length)
        wg1.add_bend(-pi, radius=bend_radius)
        # taper up again
        wg1.add_straight_segment(length=50, final_width=coupler_params["width"])
        out_coupler = GratingCoupler.make_traditional_coupler_at_port(wg1.current_port, **coupler_params)

        cell = Cell(cell_name)
        cell.add_to_layer(1, in_coupler, wg1, out_coupler)
        return cell
    def calibration_with_gratings_straight(self, origin, cell_name, coupler_params):
        wg_length = self.kwargs["wg_length"]

        in_coupler = GratingCoupler.make_traditional_coupler(origin, **coupler_params)
        wg1 = Waveguide.make_at_port(in_coupler.port)
        wg1.add_straight_segment(length=wg_length)

        out_coupler = GratingCoupler.make_traditional_coupler_at_port(wg1.current_port, **coupler_params)

        cell = Cell(cell_name)
        cell.add_to_layer(1, in_coupler, wg1, out_coupler)
        return cell

    def calibration_with_gratings_s_bend(self, origin, cell_name, coupler_params):
        wg_length = self.kwargs["wg_length"]
        bend_radius = self.kwargs["bend_radius"]
        straight_length = (wg_length - 2*bend_radius)/2

        in_coupler = GratingCoupler.make_traditional_coupler(origin, **coupler_params)
        wg1 = Waveguide.make_at_port(in_coupler.port)
        wg1.add_straight_segment(length=straight_length)
        wg1.add_bend(-pi / 2, radius=bend_radius)
        wg1.add_bend(pi / 2, radius=bend_radius)
        wg1.add_straight_segment(length=straight_length)

        out_coupler = GratingCoupler.make_traditional_coupler_at_port(wg1.current_port, **coupler_params)

        cell = Cell(cell_name)
        cell.add_to_layer(1, in_coupler, wg1, out_coupler)
        return cell

    def calibration_with_straight_gratings_s_bend(self, origin, cell_name, coupler_params):
        wg_length = self.kwargs["wg_length"]
        wg_width = self.kwargs["wg_width"]
        bend_radius = self.kwargs["bend_radius"]
        straight_length = (wg_length - 2*bend_radius)/2

        in_coupler = GratingCoupler.make_traditional_coupler(origin, **coupler_params)
        wg1 = Waveguide.make_at_port(in_coupler.port)
        wg1.add_straight_segment(length=straight_length, final_width=wg_width)
        wg1.add_bend(-pi / 2, radius=bend_radius)
        wg1.add_bend(pi / 2, radius=bend_radius)
        wg1.add_straight_segment(length=straight_length, final_width=coupler_params["width"])

        out_coupler = GratingCoupler.make_traditional_coupler_at_port(wg1.current_port, **coupler_params)

        cell = Cell(cell_name)
        cell.add_to_layer(1, in_coupler, wg1, out_coupler)
        return cell
