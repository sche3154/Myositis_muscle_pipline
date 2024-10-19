from utils.data_io import *
import subprocess
import argparse

def crop_roi(file_path, bottom, top):
    roi_data, affine = load_data(file_path, needs_affine=True)
    name = file_path.split('.')[0]

    print('#### cropping %s from bottom %s to top %s'%(name, bottom, top))
    crop_command = ["fslroi", file_path, name + "_roi.nii.gz", '1', str(roi_data.shape[0]), '1', str(roi_data.shape[1]), str(bottom), str(top-bottom)]
    print(crop_command)
    subprocess.call(crop_command)

data_path = os.path.join('/home/sheng/RA/data/pilot_data', '_--_SNAC_Thigh_20240313115104_2_left')

parser = argparse.ArgumentParser(description='Arguments for croping roi')
parser.add_argument('-f', type= str, required= True, help='The input file path')
parser.add_argument('-b', '--bottom', type= int, default=0, help='z-axis slice to start')
parser.add_argument('-t', '--top', type= int, default=200, help='z-axis slice to end')
args = parser.parse_args()

crop_roi(args.f, args.bottom, args.top)