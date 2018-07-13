## 环境准备

tensorflow>=1.4,opencv>=3.2, python3,运行前请先配置好这些环境，tensorflow推荐使用gpu版的.

## 图片爬虫

使用craw.py，可以爬取百度的明星照片，craw.py的详细注释在代码中

## 图片准备

在star_images，准备每个明星的照片若干张，每个明星单独一个文件夹，文件的目录如下所示，文件的名称用拼音表示

  --star_images

​       --liuyifei  刘亦菲的照片文件

​       --liudehua  刘德华的照片文件

## 特征抽取

运行export_embedding,该方法将会检测明星的人脸，并且从人脸中抽取出512维的特征向量，特征向量在txt文件当中.

txt文件中的特征格式如下：

img_path:  $x_1$, ......$x_{512}$

其中img_path表示的是图片的地址， x1表示第一维特征向量，一直到512维，每一行一个记录



## 人脸检测

人脸检测用到的方法是MTCNN，MTCNN的原理请参考论文:MTCNN: Joint Face Detection and Alignment Using Multitask Cascaded Convolutional Networks，识别用到的网络是inception-resnet-v1.

下面的过程展示了使用MTCNN的方法：

```
>>> from mtcnn.mtcnn import MTCNN
>>> import cv2
>>>
>>> img = cv2.imread("ivan.jpg")
>>> detector = MTCNN()
>>> print(detector.detect_faces(img))
[{'box': [277, 90, 48, 63], 'keypoints': {'nose': (303, 131), 'mouth_right': (313, 141), 'right_eye': (314, 114), 'left_eye': (291, 117), 'mouth_left': (296, 143)}, 'confidence': 0.99851983785629272}]
```

bounding box的格式是[x,y,width,height]，分数表示框中有人脸的概率，其余的表示人脸的五个关键点

## 人脸矫正

人脸检测之后，需要对人脸进行矫正,人脸矫正的详细，请参考

https://zhuanlan.zhihu.com/p/29515986

## 人脸比对

人脸比对是对每个检测出的人脸抽取512维的向量，再和数据库中抽取好的特征向量进行比对，找到相近的人脸

人脸比对的函数在sourlab_face类中的find_nearest中，人脸评分相似度的方法是,因为观察到相似的明星，不同的照片，距离在0.6-0.8,不同的人脸的距离在1.1以上，所以，我们的评分函数如下:

当距离小于0.6的时候， $score=90+10*(0.6-dist)$

当距离在大于0.6，小于0.8的时候,$score=75+10*(0.8-dist)$

当距离大于0.8的时候:$score=20+55/(max(dist)-0.8)*(max(dist)-dist)$

其中$max(dist)$表示的是所有距离的最大值















##  