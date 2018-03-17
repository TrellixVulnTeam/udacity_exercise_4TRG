#coding=utf8
"""
Created on 2017.6.19 12:15
Author: Victoria
Email: wyvictoria1@gmail.com
Generating SVHN dataset for Goodfellow 2014. The shape of image should be 3*64*64.
"""
import os
import pickle
import random
import h5py
import cv2
import numpy as np
import torch
import torch.utils.data as data
random.seed(20)

def draw_box(img, box):
    """
    Draw box in image.
    Input:
        img: np.array
        box:(left, top, width, height), int
    Return:    
    """
    cv2.rectangle(img, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), (255, 0, 0), 2)
    cv2.imshow('hh', img)
    cv2.waitKey()

def random_crop(img):
    """
    Crop 54*54 from the resized img at random location.
    Input:
        img: np.array
    Return:
        random_croped_img: np.array
    """
    left = random.randint(0, 10)
    top = random.randint(0, 10)
    
    return img[top:(top+54), left:(left+54)]    
        
def resize(img, size):
    """
    Resized the croped img into 64*64.
    Input:
        img: np.array, croped img
    Return:
        resized_img: np.array, 64*64    
    """
    return cv2.resize(img, (size, size))
    
def crop(img, box):
    """
    Crop regoin of box in image.
    Input:
        img: np.array
        box: (left, top, width, height), int
    Return:
        croped_img: np.array    
    """
    croped_img = img[box[1]:(box[1]+box[3]), box[0]:(box[0]+box[2])]
    return croped_img

def expand_box(box, img_width, img_height):
    """
    Expand merged box in image by 30% in both x and y direction.
    Input:
        box: list, (left, top, width, height), int
        img_width:　int, checking whether scaled right/bottom resonable 
        img_height: int, 
    Return:
        expanded_box: list, int    
    """    
    left, top, width, height = box
    expanded_left = max(left - 0.15*width, 0)
    expanded_top = max(top-0.15*height, 0)
    expanded_right = min(expanded_left+width+0.15*width, img_width)
    expanded_bottom = min(expanded_top+height+0.15*height, img_height)
    return int(expanded_left), int(expanded_top), int((expanded_right-expanded_left)), int(expanded_bottom-expanded_top)
        
def merge_boxes_per_img(boxes_per_img):
    """
    Merge digit boxes in one image into a large box.
    Input:
        boxes_per_img: list, (left, top, width, height), float
    Return:
        merged_left: float, left of merged box
        merged_top:
        merged_width:
        merged_height:
    """
    best_left, best_top, best_width, best_height = boxes_per_img[0]
    best_right = best_left + best_width
    best_bottom = best_top + best_height
    for box in boxes_per_img:
        left, top, width, height = box
        right = left + width
        bottom = top + height
        if left < best_left:
            best_left = left
        if top < best_top:
            best_top = top
        if right > best_right:
            best_right = right
        if bottom > best_bottom:
            best_bottom = bottom
    return best_left, best_top, (best_right-best_left), (best_bottom-best_top)                
        
    
def generate_dataset(train="train", data_aug=False, rand_num=5):
    """
    Read digitStruct.mat　file and generate (img, label) dataset.
    Input:
        train: str, {"train", "extra", "test"}
        data_aug: bool, true: data augmention operation, resize expanded croped image into 64*64 and then random cropping imgs; false: resize expanded cropped image into 54*54 directly
        rand_num: int, random cropping times
    Return:
        imgs: list of np.array
        labels: list of label tensor likes [length, digit1, digit2, digit3, digit4, digit5]    
    """
    print ("loading data...")
    imgs = []
    boxes = []
    labels = []
    if os.path.exists("./loaded_data/{}.pkl".format(train)):
        with open("./loaded_data/{}.pkl".format(train), "rb") as f:
            imgs,labels = pickle.load(f)
    else:
        path = "../dataset/SVHN/{}/digitStruct.mat".format(train)
        data = h5py.File(path)
        name = data["digitStruct/name"] #shape: (-1, 1)
        box = data["digitStruct/bbox"] #shape:(-1, 1) 
        for i in range(name.shape[0]):

            #print "i: ", i
            #if i > 200:
                #break
            #image name
            #if i == 29929:
           # 	continue
            name_element = name[i][0]
            
            name_obj = data[name_element]
            img_name = "".join([chr(j) for j in name_obj[:]])
            img = cv2.imread("../dataset/SVHN/{}/{}".format(train, img_name))
               
            #box and label
            box_element = box[i][0]
            box_obj = data[box_element] #HDF5 group
            if box_obj["label"].shape[0] == 1:
                digit = int(box_obj["label"][0][0])
                if digit == 10: #SVHN: digit 0's label is 10, most cases of label=10 are wrong, skipping
                    continue
                label = [1, digit, 10, 10, 10, 10]#10 represents digit doesn' exist
                left = int(box_obj["left"][0][0])
                top = int(box_obj["top"][0][0])
                width = int(box_obj["width"][0][0])
                height = int(box_obj["height"][0][0])
            else:
                digits = []
                boxes_per_img = []
                for j in range(box_obj["label"].shape[0]):
                    label_element = box_obj["label"][j][0]
                    left_element = box_obj["left"][j][0]
                    top_element = box_obj["top"][j][0]
                    width_element = box_obj["width"][j][0]
                    height_element = box_obj["height"][j][0]                    
                    label_obj = data[label_element]
                    left_obj = data[left_element]
                    top_obj = data[top_element]
                    width_obj = data[width_element]
                    height_obj = data[height_element]
                    #print "label: ", type(label_obj)   #h5py._hl.dataset.Dataset
                    #print "height: ", type(height_obj) #h5py._hl.dataset.Dataset
                    svhn_label = int(label_obj[0][0].item())
                    if svhn_label == 10:
                        svhn_label = 0
                    if i==433:
                        print (svhn_label)
                    digits.append(svhn_label)
                    boxes_per_img.append([int(left_obj[0][0]), int(top_obj[0][0]), int(width_obj[0][0]), int(height_obj[0][0])])
                left, top, width, height = merge_boxes_per_img(boxes_per_img)
                #If digits num in image is larger than 5, should be clipped 
                if len(digits)<=5:
                    label = [len(digits)] + digits + [10] * (5-len(digits))
                else:
                    label = [5] + digits[0:5]    
                    print ("more than 5 digits in image {}".format(img_name))

            merged_box = [left, top, width, height]
            img_height, img_width = img.shape[0], img.shape[1]
            expanded_box = expand_box(merged_box, img_width, img_height)
            croped_img = crop(img, expanded_box)
            if data_aug:
                resized_img = resize(croped_img, 64) #64*64
                for k in range(rand_num): 
                    aug_img = random_crop(resized_img)   #54*54      
                    imgs.append(torch.from_numpy(resize(aug_img, 64).transpose(2, 0, 1)))                 
                    labels.append(torch.from_numpy(np.array(label)))
            else:
            	imgs.append(torch.from_numpy(resize(croped_img, 64).transpose(2, 0, 1)))
            	labels.append(torch.from_numpy(np.array(label)))         
        with open("./loaded_data/{}.pkl".format(train), "wb") as f:
            pickle.dump([imgs, labels], f)
    print ("len of img:", len(imgs))
    
    return imgs, labels      

class SVHNDataset(data.Dataset):
    def __init__(self, images, labels):
        self.images = images
        self.labels = labels
    def __len__(self):
        return len(self.images)
    def __getitem__(self, index):
        return self.images[index], self.labels[index]    

    
if __name__=="__main__":
    generate_dataset(train="train", data_aug=True, rand_num=5)  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
