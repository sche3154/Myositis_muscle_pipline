import os
import pickle
import nibabel as nib
from .mrtrix import *

def load_data(path, needs_affine = False):

    if not os.path.exists(path):
        raise ValueError(
            "Data could not be found \"{}\"".format(path)
        )
        exit(0)

    if path.endswith('.mif.gz') or path.endswith('.mif'):
        vol = load_mrtrix(path)
        data_copied = vol.data.copy()
        affine_copied = vol.transform.copy()
    elif path.endswith('.nii.gz') or path.endswith('.nii'):
        vol = nib.load(path)
        data_copied = vol.get_fdata().copy()
        affine_copied = vol.affine.copy()
    else:
        raise IOError('file extension not supported: ' + str(path))
        exit(0)

    # Return volume
    if needs_affine:
        return data_copied, affine_copied
    else:
        return data_copied
    

def save_data(img, affine, path):
    nifti = nib.Nifti1Image(img, affine=affine)
    nib.save(nifti, path)
    print('Save image to the path {:}'.format(path))


def save_pickle(file, path):

    with open(path, 'wb') as handle:
        pickle.dump(file, handle, protocol=pickle.HIGHEST_PROTOCOL)

def read_pickle(path):

    with open(path, 'rb') as handle:
        pickle_file = pickle.load(handle)

    return pickle_file