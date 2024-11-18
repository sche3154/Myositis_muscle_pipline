import torch
import numpy as np
import random
import time
import os 
import argparse

from utils.data_io import *
from utils.processing import *
from utils.unet3D import *
from utils.net_operations import *

torch.manual_seed(1)
np.random.seed(1)
random.seed(1)
torch.cuda.manual_seed_all(1)
torch.cuda.manual_seed(1)
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = True

if __name__ == '__main__':
    torch.cuda.empty_cache()

    parser = argparse.ArgumentParser(description='Arguments for predicting thigh mask')
    parser.add_argument('-i', type= str, required= True, help='The input file path')
    parser.add_argument('-o', type= str, required= True, help='The output file path')
    args = parser.parse_args()

    thigh_data, affine = load_data(args.i, needs_affine=True)
    thigh_data_patches, thigh_coords, bb = preprocessing(thigh_data)

    net =  init_net(U3DNet(1,1), gpu_ids=[0])
    load_net(net, '/home/sheng/RA/Myositis_muscle_pipline/503_net_tms.pth')
    net.eval()

    for i, data in enumerate(dataset):

        start_time = time.time()

        if i >= opt.num_test:  # only apply our model to opt.num_test images.
            break

        if opt.input_patch_size > 0: # now can handle patches
            pred_list = []
            patch_nums = len(data[next(iter(data))].squeeze(0))
            # print(patch_nums)
            outputs = []

            for j in range(0, patch_nums, opt.input_patch_size):
                data_patched = {}
                for key, value in data.items():
                    value = value.squeeze(0)
                    data_patched[key] = value[j:min(j+opt.input_patch_size, patch_nums),...]
                    # print(data_patched[key].shape)
                model.set_input(data_patched)
                output = model.test()  # run inference
                outputs.append(output)

            dataset.dataset.postprocessing(outputs, counter= i+1)

        else:
            pass


    print('End inference')