import subprocess
from utils.data_io import *

def crop_middle(roi_fln):
    try:      
        roi_img = nib.load(roi_fln + '.nii.gz')
    except FileNotFoundError:
        print('INFO: Cannot find the .nii.gz file, loading .nii instead')
        roi_img = nib.load(roi_fln + '.nii')

    roi_dat = roi_img.get_fdata()
    roi_aff = roi_img.affine
    roi_hdr = roi_img.header

    projection_z = np.mean(roi_dat,axis=2)
    projection_z = np.rot90(projection_z)

    projection_zx = np.mean(projection_z, axis=0)
    left_max = np.argmax(projection_zx[0:int(np.shape(projection_zx)[0]/2)])
    right_max = np.argmax(projection_zx[int(np.shape(projection_zx)[0]/2):int(np.shape(projection_zx)[0])]) + int(np.shape(projection_zx)[0]/2)
    middle_point = np.argmin(projection_zx[left_max:right_max])
    middle_point += left_max

    
    print('########           Cropping ' + roi_fln + ' left         ########')
    crop_command = ["fslroi", roi_fln, roi_fln + "_left.nii.gz", str(middle_point), str(roi_dat.shape[0]-middle_point), '0', str(roi_dat.shape[1]), '0', str(roi_dat.shape[2])]
    print(crop_command)
    subprocess.call(crop_command)
    print('########          Cropping ' + roi_fln + ' right         ########')
    crop_command = ["fslroi", roi_fln, roi_fln + "_right.nii.gz", '0', str(middle_point), '0', str(roi_dat.shape[1]), '0', str(roi_dat.shape[2])]
    subprocess.call(crop_command)
    print(crop_command)
    return 1


data_path = os.path.join('/home/sheng/RA/data/pilot_data', '_--_SNAC_Thigh_20240313115104_2')
crop_middle(data_path)