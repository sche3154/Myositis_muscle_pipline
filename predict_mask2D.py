import torch
import numpy as np
import random
import argparse

from utils.data_io import *
from utils.processing import *
from utils.tms_net2D import *
from utils.net_operations import *

torch.manual_seed(1)
np.random.seed(1)
random.seed(1)
torch.cuda.manual_seed_all(1)
torch.cuda.manual_seed(1)
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = True

device = torch.device('cuda:{}'.format(0))
kernel_size = (128,128,128)
stride_size = (64,64,64)

if __name__ == '__main__':
    torch.cuda.empty_cache()

    parser = argparse.ArgumentParser(description='Arguments for predicting thigh mask')
    parser.add_argument('-i', type= str, required= True, help='The input file path')
    parser.add_argument('-o', type= str, required= True, help='The output file path')
    # parser.add_argument('-batch_size', type = int, default= 10, help='The default batch size')
    parser.add_argument('-confidence_thres', type = float, default= 0.5, help='The default confidence threshold for generating final mask')
    args = parser.parse_args()

    net = init_net(TmsNet2D(), gpu_ids=[0])
    load_networks(net, load_path='/home/sheng/RA/Myositis_muscle_pipline/40_net_tms.pth')

    sigmoid = nn.Sigmoid()

    thigh_data, affine = load_data(args.i, needs_affine=True)
    print('Input shape: {}'.format(thigh_data.shape))
    # for each slice, pathcing

    mask = np.zeros(thigh_data.shape)
    for z in range(thigh_data.shape[2]):
        cur_slice_data = thigh_data[:,:,z]
        slice_patches_data = slice_matrix(cur_slice_data, kernel_size, stride_size, three_dim =False)

        # print(len(slice_patches_data))

        outputs = []
        for i in range(len(slice_patches_data)):
            cur_patch = slice_patches_data[i]
            # cur_patch = (slice_patches_data[i] - np.mean(slice_patches_data))/(np.std(slice_patches_data)+1e-6)
            cur_patch = torch.tensor(cur_patch).to(device).unsqueeze(0).unsqueeze(0)\
                .type(dtype= torch.cuda.FloatTensor)
            # print(cur_patch.shape)
            output = net(cur_patch)
            output = sigmoid(output)
            # print(output.shape)
            output = output.squeeze(0).squeeze(0)
            output = output.detach().cpu().numpy()
            outputs.append(output)

        # print(len(outputs))

        recon_slice = concat_2Dmatrices(outputs, cur_slice_data.shape, kernel_size, stride_size)
        recon_slice[recon_slice>args.confidence_thres] = 1.
        recon_slice[recon_slice<=args.confidence_thres] = 0.
        mask[:,:,z] = recon_slice

    save_data(mask, affine, args.o)
