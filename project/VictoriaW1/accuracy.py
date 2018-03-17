"""
Created on 2017.7.3 8:21
Author: Victoria
Email: wyvictoria1@gmail.com
"""

import torch

def accu(output, target, cuda):
    """
    Accuracy of output with respect to target.
    Input:
        output: list of Variables with shape (batch_size, 7/11)        
        target: Variable with shape (batch_size, 6)
        cuda: bool
    Return:    
    """
    batch_size = output[0].size(0)
    _, length_predict = torch.max(output[0], 1) #(batch_size, 1)
    length_correct = (length_predict == target[:, 0].contiguous().view(-1, 1).long()).float()
    _, digit1_predict = torch.max(output[1], 1)
    digit1_correct = (((digit1_predict == target[:, 1].contiguous().view(-1, 1).long()) + (1>length_predict)*2) > 0).float()
    digits_correct = digit1_correct #all digits should be predicted correctly
    for i in range(4):
        _, digit_predict = torch.max(output[i+2], 1)
        digit_correct = (((digit_predict == target[:, i+2].contiguous().view(-1, 1).long()) + ((i+2)>length_predict)*2) > 0).float()
        digits_correct = digits_correct * digit_correct
    correct = length_correct * digits_correct  #both length and digits shoule be predicted correctly   
    accuracy = torch.mean(correct)
    return accuracy        
            
        
