# coding=gbk
import cv2
import tensorflow as tf
from mtcnn.mtcnn import MTCNN
from skimage import transform as trans
import numpy as np
import pdb
import facenet
import sys

#将拼音转成汉字
pinyin2hanzi = {'lingengxin':'林更新','zhoudongyu':'周冬雨','liangjiahui':'梁家辉','shenteng':'沈腾','liyifeng':'李易峰','dengchao':'邓超','shuqi':'舒淇','huangbo':'黄渤','zhangmanyu':'张曼玉','liushishi':'刘诗诗','fanbingbing':'范冰冰','zhaoyouting':'赵又廷','zhourunfa':'周润发','louyixiao':'娄艺潇','liangjiahui':'梁家辉','liruotong':'李若彤','liuhaoran':'刘昊然','xienuo':'谢娜','hangeng':'韩庚','liuyifei':'刘亦菲','zhenzidan':'甄子丹','liudehua':'刘德华','songqian':'宋茜','guanzhilin':'关之琳','nini':'倪妮','wangzuxian':'王祖贤','tongliya': '佟丽娅','dilireba': '迪丽热巴',
'wangbaoqiang': '王宝强',
'yangying' :'杨颖',
'zhoujielun': '周杰伦',
'tangyan' :'唐嫣',
'xuzheng': '徐峥',
'lijiaxin': '李嘉欣',
'zhangbaizhi': '张柏芝',
'handongjun': '韩东君',
'gulinuozha': '古力娜扎',
'chenhe': '陈赫',
'chenqiaoen' :'陈乔恩',
'gutianle': '古天乐',
'yaochen': '姚晨',
'guofucheng' :'郭富城',
'zhangyixing': '张艺兴',
'yangzi': '杨紫',
'zhouhuimin' :'周慧敏',
'sunli' :'孙俪',
'mayili': '马伊俐',
'fengshaofeng' :'冯绍峰',
'jingtian': '景甜',
'liujialing' :'刘嘉玲',
'chenkun': '陈坤',
'jiangwen' :'姜文',
'pengyuyan' :'彭于晏',
'luhan' :'鹿晗',
'gaoyuanyuan' :'高圆圆',
'zhaoliying':'赵丽颖',
'wulei':'吴磊',
'zhangjiahui':'张家辉'}

#标准人脸中五个点的坐标，方便将人脸矫正
POINTS_SRC = np.array([
             [30.2946, 51.6963],
             [65.5318, 51.5014],
             [48.0252, 71.7366],
             [33.5493, 92.3655],
             [62.7299, 92.2041] ], dtype=np.float32)

#矫正的人脸的标准大小
SHAPE = [112,96] 
IMG_SIZE = 160

#识别模型地址
MODEL_DIR = '/root/sourlab/test/models/20180402-114759.pb'

class sourlab_face(object):
    #类变量，graph和txt的文件地址
    #初始化类，并加载graph和txt
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
    #返回人脸的个数
        image = cv2.imread(img_file)
        if image is None:
            print('image load error')
            return None, None
            
        #检测人脸
        result = sourlab_face._detector.detect_faces(image)
        num_face = len(result)
        points_dst = np.zeros((num_face,5,2))
        warped_face = np.zeros((num_face,SHAPE[0],SHAPE[1],3))
        
        #将检测到的人脸矫正到正常的位置
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
        #识别前首先检测和矫正人脸
        num_face, warped_face = self.detect_and_warp(img_file)
        
        #没有人或者多于2个人脸，都返回-1
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
        
        #对图片进行预处理
        face_checked = facenet.prewhiten(face_checked)
        input_data = []
        input_data.append(face_checked.reshape(-1,IMG_SIZE ,IMG_SIZE ,3))
        #提取出人脸的512维特征
        return self.extract_feature(input_data)

    #调用识别模型，得到用户图片的512维特征向量
    def  extract_feature(self, input_data):
    #返回抽取到的512维的特征
        with sourlab_face._graph.as_default():
            image_placeholder = sourlab_face._graph.get_tensor_by_name("input:0")
            embedding = sourlab_face._graph.get_tensor_by_name('embeddings:0')
            phase_train_placeholder = sourlab_face._graph.get_tensor_by_name("phase_train:0")
            embedding_size = embedding.get_shape()[1]
            embed_array = np.zeros((1,embedding_size))
            with sourlab_face._sess.as_default():
                embed_array[0] = sourlab_face._sess.run(embedding, feed_dict={image_placeholder: input_data[0], phase_train_placeholder: False })
                return embed_array
                
    #静态方法加载feature
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
                
    #根据人脸找到最近的人脸位置
    def find_nearest(self,feature):
    #返回明星的名字，得分，和图片的地址
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
