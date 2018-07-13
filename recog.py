# coding=gbk
import cv2
import tensorflow as tf
from mtcnn.mtcnn import MTCNN
from skimage import transform as trans
import numpy as np
import pdb
import facenet
import sys

#��ƴ��ת�ɺ���
pinyin2hanzi = {'lingengxin':'�ָ���','zhoudongyu':'�ܶ���','liangjiahui':'���һ�','shenteng':'����','liyifeng':'���׷�','dengchao':'�˳�','shuqi':'���','huangbo':'�Ʋ�','zhangmanyu':'������','liushishi':'��ʫʫ','fanbingbing':'������','zhaoyouting':'����͢','zhourunfa':'����','louyixiao':'¦����','liangjiahui':'���һ�','liruotong':'����ͮ','liuhaoran':'���Ȼ','xienuo':'л��','hangeng':'����','liuyifei':'�����','zhenzidan':'���ӵ�','liudehua':'���»�','songqian':'����','guanzhilin':'��֮��','nini':'����','wangzuxian':'������','tongliya': '١���','dilireba': '�����Ȱ�',
'wangbaoqiang': '����ǿ',
'yangying' :'��ӱ',
'zhoujielun': '�ܽ���',
'tangyan' :'����',
'xuzheng': '���',
'lijiaxin': '�����',
'zhangbaizhi': '�Ű�֥',
'handongjun': '������',
'gulinuozha': '��������',
'chenhe': '�º�',
'chenqiaoen' :'���Ƕ�',
'gutianle': '������',
'yaochen': 'Ҧ��',
'guofucheng' :'������',
'zhangyixing': '������',
'yangzi': '����',
'zhouhuimin' :'�ܻ���',
'sunli' :'��ٳ',
'mayili': '������',
'fengshaofeng' :'���ܷ�',
'jingtian': '����',
'liujialing' :'������',
'chenkun': '����',
'jiangwen' :'����',
'pengyuyan' :'������',
'luhan' :'¹��',
'gaoyuanyuan' :'��ԲԲ',
'zhaoliying':'����ӱ',
'wulei':'����',
'zhangjiahui':'�żһ�'}

#��׼���������������꣬���㽫��������
POINTS_SRC = np.array([
             [30.2946, 51.6963],
             [65.5318, 51.5014],
             [48.0252, 71.7366],
             [33.5493, 92.3655],
             [62.7299, 92.2041] ], dtype=np.float32)

#�����������ı�׼��С
SHAPE = [112,96] 
IMG_SIZE = 160

#ʶ��ģ�͵�ַ
MODEL_DIR = '/root/sourlab/test/models/20180402-114759.pb'

class sourlab_face(object):
    #�������graph��txt���ļ���ַ
    #��ʼ���࣬������graph��txt
    _graph = tf.Graph()
    _sess = tf.Session(graph=_graph)
    movie_star = []
    feature_list = []
    _detector = MTCNN(min_face_size = 12)
    txt_file = '/root/sourlab/test/feature.txt'
    print('load detection module')
    with _graph.as_default():
        _recognition = facenet.load_model(MODEL_DIR)
        print('load recognition module')

    def __init__(self, min_face_size=12):
        pass

    def detect_and_warp(self, img_file):
    #���������ĸ���
        image = cv2.imread(img_file)
        if image is None:
            print('image load error')
            return None, None
            
        #�������
        result = sourlab_face._detector.detect_faces(image)
        num_face = len(result)
        points_dst = np.zeros((num_face,5,2))
        warped_face = np.zeros((num_face,SHAPE[0],SHAPE[1],3))
        
        #����⵽������������������λ��
        for i in range(num_face):
            keypoints = result[i]['keypoints']
            points_dst[i,0,:] = keypoints['left_eye']
            points_dst[i,1,:] = keypoints['right_eye']
            points_dst[i,2,:] = keypoints['nose']
            points_dst[i,3,:] = keypoints['mouth_left']
            points_dst[i,4,:] = keypoints['mouth_right']
            # get the transform matrix and warp the face
            tform = trans.SimilarityTransform()
            tform.estimate(points_dst[i,:,:], POINTS_SRC)
            M = tform.params[0:2,:]
            warped_face[i,:,:,:] = cv2.warpAffine(image,M,(SHAPE[1],SHAPE[0]), borderValue = 0.0)
        return num_face, warped_face


    def recognition(self, img_file):
        #ʶ��ǰ���ȼ��ͽ�������
        num_face, warped_face = self.detect_and_warp(img_file)
        
        #û���˻��߶���2��������������-1
        if num_face is None:
            print('detect no faces')
            return -1
        if num_face == 0:
            print('detect no face')
            return -1

        if num_face>=2:
            print('detect more than 2 faces in the picture')
            return 0
        try:
            face_checked =  cv2.resize(warped_face[0],(IMG_SIZE,IMG_SIZE), interpolation=cv2.INTER_CUBIC)
        except BaseException:
            pdb.set_trace()
        else:
            pass
        print('detect face')	
        
        #��ͼƬ����Ԥ����
        face_checked = facenet.prewhiten(face_checked)
        input_data = []
        input_data.append(face_checked.reshape(-1,IMG_SIZE ,IMG_SIZE ,3))
        #��ȡ��������512ά����
        return self.extract_feature(input_data)

    #����ʶ��ģ�ͣ��õ��û�ͼƬ��512ά��������
    def  extract_feature(self, input_data):
    #���س�ȡ����512ά������
        with sourlab_face._graph.as_default():
            image_placeholder = sourlab_face._graph.get_tensor_by_name("input:0")
            embedding = sourlab_face._graph.get_tensor_by_name('embeddings:0')
            phase_train_placeholder = sourlab_face._graph.get_tensor_by_name("phase_train:0")
            embedding_size = embedding.get_shape()[1]
            embed_array = np.zeros((1,embedding_size))
            with sourlab_face._sess.as_default():
                embed_array[0] = sourlab_face._sess.run(embedding, feed_dict={image_placeholder: input_data[0], phase_train_placeholder: False })
                return embed_array
                
    #��̬��������feature
    @staticmethod
    def load_feature():
        f = open(sourlab_face.txt_file, 'r')
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            line = line.split(' ')
            sourlab_face.movie_star.append(line[0])
            #tmp = []
            #print(len(line))
            for i in range(len(line) - 1):
                sourlab_face.feature_list.append(float(line[i + 1]))
                
    #���������ҵ����������λ��
    def find_nearest(self,feature):
    #�������ǵ����֣��÷֣���ͼƬ�ĵ�ַ
        sourlab_face.feature_list = np.array(sourlab_face.feature_list)
        dim = 512
        sourlab_face.feature_list = sourlab_face.feature_list.reshape(-1,dim)
        # feature_list = feature_list.reshape(feature_list.shape[0],feature_list.shape[2])
        dist = np.zeros(sourlab_face.feature_list.shape[0])
        for i in range(dist.shape[0]):
             dist[i] = np.sqrt(np.sum(np.square(np.subtract(sourlab_face.feature_list[i], feature))))
        
        idx = np.argsort(dist)[0]
        if dist[idx]<=0.5:
            score = 90+10*(0.5-dist[idx])
        if 0.5<dist[idx]<=0.9:
            score = 50+(0.9-dist[idx])*100
        if dist[idx]>0.9:
            score = 20+(np.max(dist)-dist[idx])*(30/(np.max(dist)-0.9))
        img_path = sourlab_face.movie_star[np.argsort(dist)[0]]
        return pinyin2hanzi[img_path.split('/')[-2]],score,img_path
        


if __name__ == '__main__':
    img_name1 , img_name2 = sys.argv[1], sys.argv[2]
    recog1 =  sourlab_face(12)
    sourlab_face.load_feature()
    feature1 = recog1.recognition(img_name1)
    a,b,c = recog1.find_nearest(feature1)
    pdb.set_trace()
