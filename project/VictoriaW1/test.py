"""
Created on 2017.7.3 8:21
Author: Victoria
Email: wyvictoria1@gmail.com
"""
import numpy as np

from load_data import generate_dataset, SVHNDataset
from net import MultiDigitsNet
from loss import loss
from accuracy import accu

import torch
from torch.autograd import Variable

def test(batch_size, cuda, path):
    """
    Test performance of testing dataset on trainined model.
    Input:
        batch_size: int
            testing batch size.
        cuda: bool
            running on GPU or CPU.
        path: str
            path to trained model.    
    Return:
    """
    print ("testing...")
    print ("cuda: ", cuda)
    test_data = generate_dataset(train="test")
    print ("len of image: ", len(test_data[0]))
    test_dataset = SVHNDataset(test_data[0], test_data[1]) 
    kwargs = {'num_workers': 1, 'pin_memory': True}  if cuda else {}
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size, **kwargs)      
    model = MultiDigitsNet()
    if cuda:
        model.cuda()
    model.eval()
    model.load_state_dict(torch.load(path))
    batch_losses = []
    batch_accuracy = []
    for batch_idx, (data, target) in enumerate(test_loader):
        if cuda:
            data, target = data.cuda(), target.cuda()
        data, target = Variable(data), Variable(target)    
        data = data.float()
        output = model(data)
        losses = loss(output, target, cuda)
        batch_losses.append(losses.data[0])
        accuracy = accu(output, target, cuda)
        batch_accuracy.append(accuracy.data[0])
        if batch_idx % 100 == 0:
            print ("[{} / {}]: testing loss: {}, testing accuracy: {}".format(batch_idx*batch_size, len(test_dataset), losses.data[0], accuracy.data[0]) )
    test_loss = np.mean(np.array(batch_losses))
    test_accuracy = np.mean(np.array(batch_accuracy))    
    print ("testing loss: {}, testing accuracy: {}".format(test_loss, test_accuracy))
