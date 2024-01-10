import numpy as np
import os
import h5py as h5


# define hdf5 reader function
def read_hdf5(direct, file, readon=True):
    filepath = os.path.join(direct, file)
    base = os.path.basename(file)
    file_name = os.path.splitext(base)[0]
    file_name_print = file_name
    file_name = {}

    if os.path.isfile(filepath) is True:
        with h5.File(filepath, "r") as hdf:
            folders = list(hdf.keys())  ## get parent folder name in hdf5 file
            for folder in folders:
                sub_folders = list(hdf.get(folder).keys())
                # print(*sub_folders, sep= "\n")
                for subfolder in sub_folders:
                    file_name[subfolder] = np.array(hdf.get(folder).get(subfolder))
    else:
        print("file or folder does not exist in path:", filepath)
    if readon is True:
        print("Folder name:", file_name_print)
        print("group names -", type(file_name), ":")
        print(*file_name.keys(), sep="\n")

    return file_name
