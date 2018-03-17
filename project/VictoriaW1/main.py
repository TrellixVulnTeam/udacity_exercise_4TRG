"""
Created on 2017.6.29 16:15
Author: Victoria
Email: wyvictoria1@gmail.com
"""
from train import train
from test import test
import argparse
import torch

parser = argparse.ArgumentParser()
parser.add_argument('--data_aug', type=int, default=0, help='data augmention or not(default: 0)')
parser.add_argument('--rand_num', type=int, default=5, help='random cropped image num(default: 5)')
parser.add_argument('--epochs', type=int, default=120, metavar='N', help='number of epochs to train (default: 10)')
parser.add_argument('--lr', type=float, default=0.0005, metavar='LR', help='learning rate (default: 0.001)')
parser.add_argument('--momentum', type=float, default=0.9, metavar='M', help='SGD momentum (default: 0.5)')
parser.add_argument('--batch_size', type=int, default=16, metavar='N', help='input batch size for training(default: 6)')
parser.add_argument('--log_interval', type=int, default=1, metavar='N', help='how many batches to wait before logging training status')
parser.add_argument('--seed', type=int, default=1, metavar='S', help='random seed (default: 1)')
parser.add_argument('--cuda', type=int, default=1, help='disable CUDA training')
args = parser.parse_args()
if args.data_aug:
    args.data_aug_bool = True
else:
    args.data_aug_bool = False    
if __name__=="__main__":
    train(data_aug=args.data_aug_bool, rand_num=args.rand_num, batch_size=args.batch_size, epochs=args.epochs, lr=args.lr, momentum=args.momentum, log_interval=args.log_interval, cuda=args.cuda,early_stopping=False, path="models/trained_model.model")
    test(args.batch_size, cuda=args.cuda, path="models/trained_model.model")
