import subprocess
import argparse
from utils.data_io import *

def split_middle(file_path):     
    ### Load the data ###
    roi_data, affine = load_data(file_path, needs_affine=True)
    name = file_path.split('.')[0]

    ### Find the middle point ###
    projection_z = np.mean(roi_data,axis=2)
    projection_z = np.rot90(projection_z)

    projection_zx = np.mean(projection_z, axis=0)
    left_max = np.argmax(projection_zx[0:int(np.shape(projection_zx)[0]/2)])
    right_max = np.argmax(projection_zx[int(np.shape(projection_zx)[0]/2):int(np.shape(projection_zx)[0])]) + int(np.shape(projection_zx)[0]/2)
    middle_point = np.argmin(projection_zx[left_max:right_max])
    middle_point += left_max

    ### Split the left and right based on the middle point
    print('########           Cropping ' + name + ' left         ########')
    crop_command = ["fslroi", file_path, name + "_left.nii.gz", str(middle_point), str(roi_data.shape[0]-middle_point), '0', str(roi_data.shape[1]), '0', str(roi_data.shape[2])]
    print(crop_command)
    subprocess.call(crop_command)
    print('########          Cropping ' + file_path + ' right         ########')
    crop_command = ["fslroi", file_path, name + "_right.nii.gz", '0', str(middle_point), '0', str(roi_data.shape[1]), '0', str(roi_data.shape[2])]
    subprocess.call(crop_command)
    print(crop_command)
    return 1

parser = argparse.ArgumentParser(description='Arguments for splitting left and right legs')
parser.add_argument('-f', type= str, required= True, help='The input file path')
args = parser.parse_args()

split_middle(args.f)