# coding=gbk
import tensorflow as tf
from recog import sourlab_face
import os
import pdb
import numpy as np

#path��������Ƭ��·��
path = "./star_images"

#����path�µ�����·�����õ�ÿ��������Ƭ��·��
image_path = []
for root,dirs,files in os.walk(path,topdown=False):
    for name in dirs:
        f_list = os.listdir(path+'/'+name)
        for i in f_list:
            image_path.append(path+'/'+name+'/'+i)

#����һ��sourlab_face��
recog = sourlab_face(12)

star_feature_dict = {}

#��featureд�뵽feature.txt��
txt_file = open('feature.txt','w')
for img_path in image_path: 
    feature = recog.recognition(img_path)

    if not isinstance(feature,int):
        star_feature_dict[img_path] = feature
        
#��512ά������д��
feature_list = []
movie_star = []
for star in star_feature_dict:
    movie_star.append(star)
    txt_file.write(star)
    feature_list.append(star_feature_dict[star])

    for i in range(512):
        txt_file.write(" "+str(round(star_feature_dict[star][0][i],7)))

    txt_file.write("\n")
    





