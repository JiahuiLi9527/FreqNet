import torch
import torch.nn.functional as F
import numpy as np
import os, argparse
from lib.HFEA import HFEANetModel
import imageio
import torch.nn as nn
from utils.dataloader import test_dataset
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--testsize', type=int, default=352, help='testing size')
parser.add_argument('--pth_path', type=str, default='/DATA/home/zyw/LJH/PVT_HFEA/checkpoints/11_6_MEGANet-Res2Net/MEGANet-199.pth')

for _data_name in ['CVC-300', 'CVC-ClinicDB', 'Kvasir', 'CVC-ColonDB', 'ETIS-LaribPolypDB']:
    data_path = '/DATA/home/zyw/LJH/PraNet/PraNet-master/data/TestDataset/{}'.format(_data_name)
    save_path = '/DATA/home/zyw/LJH/FreqNet/results/test/{}/'.format(_data_name)
    opt = parser.parse_args()
    model = HFEANetModel()
    model.load_state_dict(torch.load(opt.pth_path))
    model.cuda()
    model.eval()

    os.makedirs(save_path, exist_ok=True)
    image_root = '{}/images/'.format(data_path)
    gt_root = '{}/masks/'.format(data_path)
    test_loader = test_dataset(image_root, gt_root, opt.testsize)

    for i in range(test_loader.size):
        image, gt, name = test_loader.load_data()
        gt = np.asarray(gt, np.float32)
        gt /= (gt.max() + 1e-8)
        image = image.cuda()

        predicts= model(image)
        res = predicts[0]
        res = F.upsample(res, size=gt.shape, mode='bilinear', align_corners=False)
        res = res.data.cpu().numpy().squeeze()
        res = (res - res.min()) / (res.max() - res.min() + 1e-8)
        imageio.imwrite(save_path+name, ((res>.5)*255).astype(np.uint8))
