import torch
import numpy as np
import random
import time
import os 
import argparse

from collections import OrderedDict
from utils.data_io import *
from utils.processing import *
from utils.tms_net import *

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
    parser.add_argument('-input_patch_num', tpye = int, default= 10, help='The default input patch nums')
    args = parser.parse_args()

    thigh_data, affine = load_data(args.i, needs_affine=True)
    thigh_data_patches, thigh_coords, bb = preprocessing(thigh_data)
    print(thigh_data_patches.shape)

    net = init_net(TmsNet(), gpu_ids=[0])
    load_networks(net, load_path='/home/sheng/RA/Myositis_muscle_pipline/503_net_tms.pth')

    pred_list = []
    patch_nums = thigh_data_patches.shape[0]
    print(patch_nums)
    outputs = []

    for j in range(0, patch_nums, args.input_patch_num):
        data_patched = {}
                for key, value in data.items():
                    value = value.squeeze(0)
                    data_patched[key] = value[j:min(j+opt.input_patch_size, patch_nums),...]
                    # print(data_patched[key].shape)
                model.set_input(data_patched)
                output = model.test()  # run inference
                outputs.append(output)

    #         dataset.dataset.postprocessing(outputs, counter= i+1)


    print('End inference')