import numpy as np
from .patch_operations import *

def instance_norm_2DSlices(image, mask=None):
        # (W,H,D)
        mask = mask if mask is not None else np.ones(image.shape)

        image[mask!=1] = 0

        for slice in range(mask.shape[2]):
            means = np.mean(image[...,slice])
            stds = np.std(image[...,slice])  

            image[...,slice] = (image[...,slice] - means)/stds  

        image[mask!=1] = 0
        return image

def find_bounding_box_3D(mask):
        x, y, z = mask.shape[0], mask.shape[1], mask.shape[2]
        for i in range(z):
            slice = mask[:,:,i]
            if np.sum(slice) > 0:
                save_z_from_I = i
                break

        for i in reversed(range(z)):
            slice = mask[:,:,i]
            if np.sum(slice) > 0:
                save_z_from_S = i
                break

        for i in range(y):
            slice = mask[:, i, :]
            if np.sum(slice) > 0:
                save_y_from_P = i
                break

        for i in reversed(range(y)):
            slice = mask[:, i, :]
            if np.sum(slice) > 0:
                save_y_from_A = i
                break

        for i in range(x):
            slice = mask[i,:,:]
            if np.sum(slice) > 0:
                save_x_from_L = i
                break

        for i in reversed(range(x)):
            slice = mask[i,:,:]
            if np.sum(slice) > 0:
                save_x_from_R = i
                break

        return save_x_from_L, save_x_from_R, save_y_from_P, save_y_from_A, save_z_from_I, save_z_from_S

def patch_generation(image, kernel_size, stride, three_dim):

        patches, coords = slice_matrix(image, kernel_size, stride, three_dim, save_coords = True)

        # print(len(patches))
        # Skip blank patches
  
        patches = np.stack(patches, axis = 0)
        coords = np.stack(coords, axis = 0)

        return patches, coords

def preprocessing(thigh_data):

    kernel_size = (128,128,16)
    stride_size = (64,64,12)

    thigh_data[thigh_data<=1000] = 0.
    coarse_mask = np.zeros(thigh_data.shape)
    coarse_mask[thigh_data>1000] = 1.

    thigh_data_norm = instance_norm_2DSlices(thigh_data, coarse_mask)

    x_1_t, x_2_t, y_1_t, y_2_t, z_1_t, z_2_t =  find_bounding_box_3D(coarse_mask)
    bb = [x_1_t, x_2_t, y_1_t, y_2_t, z_1_t, z_2_t]
    
    thigh_data_bounded = thigh_data_norm[bb[0]:bb[1], bb[2]:bb[3], bb[4]:bb[5]]
    coarse_mask_bounded = coarse_mask[bb[0]:bb[1], bb[2]:bb[3], bb[4]:bb[5]]
    
    bb_shape = thigh_data_bounded.shape
    coarse_mask = coarse_mask_bounded
    
    thigh_data_patches, thigh_coords = patch_generation(thigh_data_bounded
                                                        , kernel_size, stride_size, three_dim=True)

    return thigh_data_patches, thigh_coords, bb 