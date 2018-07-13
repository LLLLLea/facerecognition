# coding=utf-8
#根据搜索词下载百度图


import re
import sys
import urllib
import requests
import os
import pinyin
from PIL import Image

def to_pinyin(hanzi):
    if isinstance(hanzi, str):
        if hanzi == 'None':
            return ""
        else:
            return pinyin.get(hanzi,format='strip',delimiter="")
def get_onepage_urls(onepageurl):
    """
    获取单个翻页的所有图片的urls+当前翻页的下一翻页的url

    输入：
         onepageurl:解析的url地址
    返回:
         pic_urls:图片地址
        fanye_url:翻页地址
    """
    if not onepageurl:
        print('已到最后一页, 结束')
        return [], ''
    try:
        #得到网页内容
        html = requests.get(onepageurl).text
    except Exception as e:
        print(e)
        pic_urls = []
        fanye_url = ''
        return pic_urls, fanye_url
    #找到图片和下一页的url
    pic_urls = re.findall('"objURL":"(.*?)",', html, re.S)
    fanye_urls = re.findall(re.compile(r'<a href="(.*)" class="n">下一页</a>'), html, flags=0)
    fanye_url = 'http://image.baidu.com' + fanye_urls[0] if fanye_urls else ''
    return pic_urls, fanye_url


def down_pic(pic_root, pic_urls):
    """
    给出图片链接列表, 下载所有图片
     输入：
         pic_urls:图片的url地址
         pic_root:图片存储文件的名称
    """
    if not os.path.exists(pic_root):
        os.mkdir(pic_root)
    num = 10
    for i, pic_url in enumerate(pic_urls):
        if i>=num:
            break
        try:
            pic = requests.get(pic_url, timeout=15)
            string = pic_root + str(i + 1) + '.jpg'
            with open(string, 'wb') as f:
                f.write(pic.content)
                print('成功下载第%s张图片: %s' % (str(i + 1), str(pic_url)))
            '''
          img = Image.open(string)
          shape = img.size
          img.close()
          #分辨率小于800*600删除掉
          if shape[0]*shape[1]<600*800:
              os.remove(string)
          '''

        except Exception as e:
            print('下载第%s张图片时失败: %s' % (str(i + 1), str(pic_url)))
            print(e)
            continue


if __name__ == '__main__':
    # 关键词, 改为你想输入明星的名字,
    '''
    keyword = ['李易峰','周冬雨','徐峥','姜文','彭于晏','赵又廷','冯绍峰','林更新','刘嘉玲','邓超','孙俪','黄渤','舒淇','王宝强','张艺兴',\
              '刘昊然','韩庚','陈坤','鹿晗','黄子韬','韩东君','周杰伦','张学友','刘德华','黎明','郭富城','迪丽热巴','赵丽颖','杨幂','高圆圆',\
               '范冰冰','杨颖','倪妮','宋茜','古力娜扎','佟丽娅','邱淑贞','张柏芝','刘亦菲','刘诗诗','唐嫣','谢娜','景甜','王祖贤','张敏','张曼玉','关之琳','朱茵',\
               '李嘉欣','周慧敏','李若彤','林青霞']
    '''
    keyword = ['徐峥','吴磊','梁家辉','刘嘉玲','沈腾', '陈赫' , '娄艺潇' ,'甄子丹' ,'陈乔恩' , '古天乐','张智霖', '姚晨', '马伊琍', '张家辉', '杨紫', '周润发','郭富城' ]


    for word in keyword:
        url_init_first = r'http://image.baidu.com/search/flip?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1497491098685_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&ctd=1497491098685%5E00_1519X735&word='
        # 对关键字进行编码
        url_init = url_init_first + urllib.quote(word, safe='/')
        #存储所有图片地址
        all_pic_urls = []
        onepage_urls, fanye_url = get_onepage_urls(url_init)
        all_pic_urls.extend(onepage_urls)
        #对应明星的拼音
        pic_root = './'+to_pinyin(word)+'/'
        # 累计翻页数
        page_count = 0
        while page_count<1:
            onepage_urls, fanye_url = get_onepage_urls(fanye_url)
            page_count += 1
            print('第%s页' % page_count)
            #没有图片或者没有下一页图片
            if fanye_url == '' and onepage_urls == []:
                break
            all_pic_urls.extend(onepage_urls)

        down_pic(pic_root, list(set(all_pic_urls)))