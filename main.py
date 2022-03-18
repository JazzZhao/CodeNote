from tkinter.tix import MAIN
from unittest import main
import torch
from torch import nn
import torchvision
from torchvision import transforms
from torch.utils import data
from tqdm import tqdm
from IPython import display
import matplotlib.pyplot as plt
import utils

def nin_block(in_channels,out_channels,  kernel_size, strides, padding):
    return nn.Sequential(
    nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, stride=strides, padding=padding),
    nn.ReLU(),
    nn.Conv2d(out_channels, out_channels, kernel_size=1), nn.ReLU(),
    nn.Conv2d(out_channels, out_channels, kernel_size=1), nn.ReLU())    

def train_ch6(net , train_iter, test_iter, num_epochs, lr, device):
    def init_weight(m):
        if type(m) == nn.Linear or type(m) == nn.Conv2d:
            nn.init.xavier_uniform_(m.weight)
    net.apply(init_weight)
    net.to(device)
    print('training on', device)
    loss = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=lr)
    for epoch in tqdm(range(num_epochs)):
        net.train()
        metric = utils.Accumulator(2)
        for i, (X, y) in enumerate(train_iter):
            optimizer.zero_grad()
            X, y = X.to(device), y.to(device)
            l = loss(net(X), y)
            l.backward()
            optimizer.step()
        print(l)

def main():
    net = nn.Sequential(
        nin_block(1, 96, kernel_size=11, strides=4, padding=0),
        nn.MaxPool2d(3, stride=2),
        nin_block(96, 256, kernel_size=5, strides=1, padding=2),
        nn.MaxPool2d(3, stride=2),
        nin_block(256, 384, kernel_size=3, strides=1, padding=1),
        nn.MaxPool2d(3, stride=2),
        nn.Dropout(0.5),
        # 标签类别数是10
        nin_block(384, 10, kernel_size=3, strides=1, padding=1),
        nn.AdaptiveAvgPool2d((1, 1)),
        # 将四维的输出转成二维的输出，其形状为(批量大小,10)
        nn.Flatten())
    train_iter, test_iter = utils.load_data_fashion_mnist(64, resize=224)
    train_ch6(net, train_iter, test_iter, 10, 0.1, utils.try_gpu())

if __name__ == "__main__":
    main()
