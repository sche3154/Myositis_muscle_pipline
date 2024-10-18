from utils.data_io import *
import subprocess

def snip(roi_fln, bottom, top):
    try:      
        roi_img = nib.load(roi_fln + '.nii.gz')
    except FileNotFoundError:
        print('INFO: Cannot find the .nii.gz file, loading .nii instead')
        roi_img = nib.load(roi_fln + '.nii')

    roi_dat = roi_img.get_fdata()
    roi_aff = roi_img.affine
    roi_hdr = roi_img.header

    crop_command = ["fslroi", roi_fln, roi_fln + "_snip.nii.gz", '1', str(roi_dat.shape[0]), '1', str(roi_dat.shape[1]), str(bottom), str(top-bottom)]
    subprocess.call(crop_command)

data_path = os.path.join('/home/sheng/RA/data/pilot_data', '_--_SNAC_Thigh_20240313115104_2_left')

snip(data_path, 0, 200)