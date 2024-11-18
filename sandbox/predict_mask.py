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

device = torch.device('cuda:{}'.format(0))

if __name__ == '__main__':
    torch.cuda.empty_cache()

    parser = argparse.ArgumentParser(description='Arguments for predicting thigh mask')
    parser.add_argument('-i', type= str, required= True, help='The input file path')
    parser.add_argument('-o', type= str, required= True, help='The output file path')
    parser.add_argument('-intensity_thres', type = float, default= 5000, help='The default intensity threshold for coarse mask used in normaliztion')
    parser.add_argument('-input_patch_num', type = int, default= 20, help='The default input patch nums')
    parser.add_argument('-confidence_thres', type = float, default= 0.7, help='The default confidence threshold for generating final mask')
    args = parser.parse_args()

    thigh_data, affine = load_data(args.i, needs_affine=True)
    print('Input shape: {}'.format(thigh_data.shape))
    thigh_data_patches, thigh_coords, bb, bb_shape = preprocessing(thigh_data, args.intensity_thres)
    thigh_data_patches = torch.tensor(thigh_data_patches).to(device).type(dtype= torch.cuda.FloatTensor)
    thigh_data_patches = thigh_data_patches.unsqueeze(1)

    net = init_net(TmsNet(), gpu_ids=[0])
    load_networks(net, load_path='/home/sheng/RA/Myositis_muscle_pipline/503_net_tms.pth')

    pred_list = []
    patch_nums = thigh_data_patches.shape[0]
    print('NUmber of patches: {}'.format(patch_nums))
    outputs = []

    sigmoid = nn.Sigmoid()

    for j in range(0, patch_nums, args.input_patch_num):
        data_patched = thigh_data_patches[j:min(j+args.input_patch_num, patch_nums),...]
            # print(data_patched[key].shape)
        output = net(data_patched)
        output = sigmoid(output)
        output = output.squeeze(1)
        output = output.detach().cpu().numpy()
        outputs.append(output)

    outputs = np.concatenate(outputs, axis=0) 

    outputs = postprocessing(outputs, thigh_coords, bb, bb_shape, thigh_data.shape, args.confidence_thres)

    save_data(outputs, affine, args.o)

    print('End inference')