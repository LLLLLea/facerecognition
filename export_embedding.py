# coding=gbk
import tensorflow as tf
from recog import sourlab_face
import os
import pdb
import numpy as np

#path是明星照片的路径
path = "./star_images"

#遍历path下的所有路径，拿到每个明星照片的路径
image_path = []
for root,dirs,files in os.walk(path,topdown=False):
    for name in dirs:
        f_list = os.listdir(path+'/'+name)
        for i in f_list:
            image_path.append(path+'/'+name+'/'+i)

#申明一个sourlab_face类
recog = sourlab_face(12)

star_feature_dict = {}

#将feature写入到feature.txt中
txt_file = open('feature.txt','w')
for img_path in image_path: 
    feature = recog.recognition(img_path)

    if not isinstance(feature,int):
        star_feature_dict[img_path] = feature
        
#将512维的特征写入
feature_list = []
movie_star = []
for star in star_feature_dict:
    movie_star.append(star)
    txt_file.write(star)
    feature_list.append(star_feature_dict[star])

    for i in range(512):
        txt_file.write(" "+str(round(star_feature_dict[star][0][i],7)))

    txt_file.write("\n")
    





