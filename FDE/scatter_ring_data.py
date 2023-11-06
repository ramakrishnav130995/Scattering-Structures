import numpy as np
import h5py as h5
from read_hdf5_reader import *


def theta(lam: float, neff, m: int, width: float):
    """
    :param lam: wavelength
    :param neff: refr. index
    :param m: defraction order
    :param width: ring width = r2 -r1
    :return: scattering angle theta
    """
    arg = [m * lam / (2 * real * width) for (real, img) in neff]
    the = np.arcsin(arg)
    return np.degrees(the)


def data_prosessor_wavelength_sweep(**kwargs):
    path = kwargs['path']
    filename = kwargs['filename']
    # ----------------------------------------------
    # READ DATA
    # ----------------------------------------------
    mode_dict = read_hdf5(path, filename, False)
    neff = mode_dict['neff']
    wavelengths = np.squeeze(mode_dict['lams']) * 1e-6
    num_elements = len(mode_dict['lams'])

    # ----------------------------------------------
    # CONSTANTS
    # ----------------------------------------------
    inner_radius = kwargs['inner_radius']
    outer_radius = kwargs['outer_radius']
    width = outer_radius - inner_radius
    scattering_order = 1

    # -----------------------------------------------
    # DATA PROCESSING
    # -----------------------------------------------

    results = {'wavelengths': wavelengths,
               'num_elements': num_elements}

    # Disregard data with Im(n)<0
    neff_temp = []
    for i in range(num_elements):
        temp_array = [(real, img) for (real, img) in neff[i] if img >= -1e-8]
        neff_temp.append(temp_array)
    neff = neff_temp

    # Calculate mean and Std for each mode per sweep pint
    results['n_imag_mean'] = np.array([np.array([img for (real, img) in neff[i]]).mean() for i in range(num_elements)])
    results['n_imag_std'] = np.array([np.array([img for (real, img) in neff[i]]).std() for i in range(num_elements)])

    # get scattering angles
    thetas = []
    for i in range(num_elements):
        thetas.append(theta(lam=wavelengths[i], neff=neff[i], m=scattering_order, width=width))

    results['thetas'] = thetas

    return results


def data_prosessor_width_sweep(**kwargs):
    path = kwargs['path']
    filename = kwargs['filename']
    # ----------------------------------------------
    # READ DATA
    # ----------------------------------------------
    mode_dict = read_hdf5(path, filename, False)
    neff = mode_dict['neff']
    ring_widths = np.squeeze(mode_dict['ring_widths']) * 1e-6
    num_elements = len(mode_dict['ring_widths'])

    # ----------------------------------------------
    # CONSTANTS
    # ----------------------------------------------
    wavelength = kwargs['wavelength']
    scattering_order = 1

    # -----------------------------------------------
    # DATA PROCESSING
    # -----------------------------------------------

    results = {'ring_widths': ring_widths,
               'num_elements': num_elements}

    # Disregard data with Im(n)<0
    neff_temp = []
    for i in range(num_elements):
        temp_array = [(real, img) for (real, img) in neff[i] if img >= -1e-8]
        neff_temp.append(temp_array)
    neff = neff_temp

    # Calculate mean and Std for each mode per sweep pint
    results['n_imag_mean'] = np.array([np.array([img for (real, img) in neff[i]]).mean() for i in range(num_elements)])
    results['n_imag_std'] = np.array([np.array([img for (real, img) in neff[i]]).std() for i in range(num_elements)])

    # get scattering angles
    thetas = []
    for i in range(num_elements):
        thetas.append(theta(lam=wavelength, neff=neff[i], m=scattering_order, width=ring_widths[i]))

    results['thetas'] = thetas

    return results


def data_prosessor_radius_sweep(**kwargs):
    path = kwargs['path']
    filename = kwargs['filename']
    # ----------------------------------------------
    # READ DATA
    # ----------------------------------------------
    mode_dict = read_hdf5(path, filename, False)
    neff = mode_dict['neff']
    inner_radius = np.squeeze(mode_dict['inner_radius']) * 1e-6
    outer_radius = np.squeeze(mode_dict['outer_radius']) * 1e-6
    num_elements = len(mode_dict['inner_radius'])

    # ----------------------------------------------
    # CONSTANTS
    # ----------------------------------------------
    wavelength = kwargs['wavelength']
    scattering_order = 1

    # -----------------------------------------------
    # DATA PROCESSING
    # -----------------------------------------------

    results = {'inner_radius': inner_radius,
               'outer_radius': outer_radius,
               'num_elements': num_elements}

    # Disregard data with Im(n)<0
    neff_temp = []
    for i in range(num_elements):
        temp_array = [(real, img) for (real, img) in neff[i] if img >= -1e-8]
        neff_temp.append(temp_array)
    neff = neff_temp

    # Calculate mean and Std for each mode per sweep pint
    results['n_imag_mean'] = np.array([np.array([img for (real, img) in neff[i]]).mean() for i in range(num_elements)])
    results['n_imag_std'] = np.array([np.array([img for (real, img) in neff[i]]).std() for i in range(num_elements)])

    # get scattering angles
    thetas = []
    width = outer_radius[0] - inner_radius[0]  # width is fixed for this data
    for i in range(num_elements):
        thetas.append(theta(lam=wavelength, neff=neff[i], m=scattering_order, width=width))

    results['thetas'] = thetas

    return results
