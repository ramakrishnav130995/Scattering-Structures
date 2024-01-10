import os
from gdshelpers.layout import GridLayout
import numpy as np
from math import pi
from GDS_designs.devices import InputOutputDevices

# waveguide params
wg_length = 700
wg_width = 1.3
# get devices class
io_devices = InputOutputDevices(wg_length=wg_length, bend_radius=70, wg_width=wg_width)

# grid params
n_repeat = 4
n_hor = 10
vert_space = 500  # [um]
hor_space = 100  # [um]
# get layout
layout = GridLayout(title="LM_01_Characterization_Chip", frame_layer=0, text_layer=2, text_size=80, horizontal_spacing=hor_space)


# ---------------
# write first three rows of calibration devices with straight waveguides
# ---------------
coupler_params = {
    'full_opening_angle': np.deg2rad(90),
    'grating_period': 0.88,
    'grating_ff': 0.6,
    'n_gratings': 20,
    'taper_length': 12.00,
    'width': 2.0
}

for i in range(3):
    layout.begin_new_row("neg deffr. angle\n"
                         "nop-apodized gratings\n"
                         "p = 0.88um\n"
                         "ff sweep\n")

    periods = np.linspace(0.82, 0.92, n_hor)

    for p in periods:
        coupler_params["grating_period"] = p
        cell = io_devices.calibration_without_offset(origin=(0, 0), cell_name=str(i)+str(p), coupler_params=coupler_params)
        layout.add_to_row(cell)

    # Add column labels
    layout.add_column_label_row(('Period %0.2f um' % p for p in periods), row_label='')

# ---------------
# write last three rows of calibration devices with negative input angle
# ---------------
neg_angle_params = {
    'full_opening_angle': np.deg2rad(90),
    'grating_period': 0.89,
    'grating_ff': 0.6,
    'n_gratings': 10,
    'ap_max_ff': 0.95,
    'n_ap_gratings': 40,
    'taper_length': 12.00,
    'width': 2.0
}

for i in range(3):
    layout.begin_new_row("-9 deffr. angle\n"
                         "apodized gratings\n"
                         "p = 0.89um\n"
                         "ff = 0.6\n"
                         "ap_max_ff = 0.95\n")

    for j in range(4):
        cell = io_devices.calibration(origin=(0, 0), cell_name=str(i)+"test" + str(j), coupler_params=neg_angle_params)
        layout.add_to_row(cell)


# write and save chip
layout_cell, mapping = layout.generate_layout()
layout_cell.save("LM_01_setup_test_chip.gds")
