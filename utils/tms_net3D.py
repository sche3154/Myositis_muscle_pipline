import torch
import torch.nn.functional as F
import torch.nn as nn
from utils.net_operations import *

class Conv3D(torch.nn.Module):

    def __init__(self, in_channels, out_channels, kernel_size = 3, stride=1, padding=0, dilation=1, groups=1, bias=True, batch_norm=True, activation=torch.nn.LeakyReLU(0.2, inplace=True)):
        super(Conv3D, self).__init__()
        self.batch_norm = batch_norm
        self.activation = activation
        self.conv3d = torch.nn.Conv3d(in_channels, out_channels, kernel_size, stride, padding, dilation, groups, bias)
        self.batch_norm3d = torch.nn.BatchNorm3d(out_channels)

    def forward(self, input):
        x = self.conv3d(input)

        if self.batch_norm:
            x = self.batch_norm3d(x)

        if self.activation is not None:
            x = self.activation(x)

        return x
    
class DeConv3D(torch.nn.Module):
    def __init__(self, scale_factor, in_channels, out_channels, kernel_size = 3
            , stride = 2, padding=1, output_padding = 1, dilation=1
            , groups=1, bias=True, batch_norm=True, activation=torch.nn.LeakyReLU(0.2, inplace=True)):
        super(DeConv3D, self).__init__()

        self.conv3d = nn.Sequential(
                        nn.ConvTranspose3d(in_channels, out_channels, kernel_size, stride= stride
                            , padding= padding, output_padding = output_padding, dilation =dilation),  
                        nn.BatchNorm3d(out_channels),
                        activation)

    def forward(self, input):
        x = self.conv3d(input)
        return x

class U3DNet(nn.Module):
    def __init__(self, in_channels=8, out_channels=6, batch_norm=True, cnum=32):
        super(U3DNet, self).__init__()
        print("UNet3D is created")
        self.in_channels = in_channels
        self.out_channels = out_channels
        activation = nn.ReLU(inplace=True)
        # activation = nn.LeakyReLU(0.2, inplace=True)

        # Down sampling In_dim
        self.enc1_1 = Conv3D(in_channels, cnum, 3, 1, padding= 1, batch_norm=batch_norm, activation=activation)
        self.enc1_2 = Conv3D(cnum, cnum, 3, 2, padding= 1, batch_norm=batch_norm, activation=activation)
        # In_dim/2
        self.enc2_1 = Conv3D(cnum, 2 * cnum, 3, 1, padding= 1, batch_norm=batch_norm, activation=activation)
        self.enc2_2 = Conv3D(2 * cnum, 2 * cnum, 3, 2, padding=1, batch_norm=batch_norm, activation=activation)
        # In_dim/4
        self.enc3_1 = Conv3D(2 * cnum, 4 * cnum, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)
        self.enc3_2 = Conv3D(4 * cnum, 4 * cnum, 3, 2, padding=1, batch_norm=batch_norm, activation=activation)
        # In_dim/8
        self.enc4_1 = Conv3D(4 * cnum, 8 * cnum, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)
        self.enc4_2 = Conv3D(8 * cnum, 8 * cnum, 3, 2, padding=1, batch_norm=batch_norm, activation=activation)
    
        # Bridge In_dim/16
        self.bridge = Conv3D(8 * cnum, 16 * cnum, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)

        # Up sampling In_dim/16
        self.dec1_1 = DeConv3D(2, 16 * cnum, 8 * cnum, 3, 2, padding=1, output_padding = 1, batch_norm=batch_norm, activation=activation)
        self.dec1_2 = Conv3D(16 * cnum, 8 * cnum, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)
        # Up Sampling In_dim/8
        self.dec2_1 = DeConv3D(2, 8 * cnum, 4 * cnum, 3, 2, padding=1, output_padding = 1, batch_norm=batch_norm, activation=activation)
        self.dec2_2 = Conv3D(8 * cnum, 4 * cnum, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)
        # Up Sampling In_dim/4
        self.dec3_1 = DeConv3D(2, 4 * cnum, 2 * cnum, 3, 2, padding=1, output_padding = 1, batch_norm=batch_norm, activation=activation)
        self.dec3_2 = Conv3D(4 * cnum, 2 * cnum, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)
        # Up Sampling In_dim/2
        self.dec4_1 = DeConv3D(2, 2 * cnum, cnum, 3, 2, padding=1, output_padding = 1, batch_norm=batch_norm, activation=activation)
        self.dec4_2 = Conv3D(2 * cnum, cnum, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)

        # Output In_dim
        self.out = nn.Sequential(Conv3D(cnum, out_channels, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)
                                 ,Conv3D(out_channels, out_channels, 1, 1, padding=0, batch_norm=batch_norm, activation=None))
        
        # self.out = Conv3D(cnum, out_channels, 3, 1, padding=1, batch_norm=batch_norm, activation=activation)
                                 
    def forward(self, x, encoder_only=False):
        feat = []

        # x: b c w h d
        # Down sampling
        down_1 = self.enc1_1(x)
        pool_1 = self.enc1_2(down_1)

        down_2 = self.enc2_1(pool_1)
        pool_2 = self.enc2_2(down_2)
            
        down_3 = self.enc3_1(pool_2)
        pool_3 = self.enc3_2(down_3)
            
        down_4 = self.enc4_1(pool_3)
        pool_4 = self.enc4_2(down_4)
            
        # print('pool shape', pool_1.shape, pool_2.shape, pool_3.shape, pool_4.shape)

        if encoder_only:
            return feat

        # Bridge
        bridge = self.bridge(pool_4)

        # Up sampling
        trans_1 = self.dec1_1(bridge)
        concat_1 = torch.cat([trans_1, down_4], dim=1)
        up_1 = self.dec1_2(concat_1)

        trans_2 = self.dec2_1(up_1)
        concat_2 = torch.cat([trans_2, down_3], dim=1)
        up_2 = self.dec2_2(concat_2)

        trans_3 = self.dec3_1(up_2)
        concat_3 = torch.cat([trans_3, down_2], dim=1)
        up_3 = self.dec3_2(concat_3)

        trans_4 = self.dec4_1(up_3)
        concat_4 = torch.cat([trans_4, down_1], dim=1)
        up_4 = self.dec4_2(concat_4)
 
        out = self.out(up_4)

        return out
    
class TmsNet3D(nn.Module):

    def __init__(self):
        super(TmsNet3D, self).__init__()
        self.net = U3DNet(1, 1)

    def forward(self, x):
        
        out = self.net(x)

        return out