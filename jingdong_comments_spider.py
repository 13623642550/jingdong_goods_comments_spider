'''
爬取京东某款显示器的商品评价
显示器页面：https://item.jd.com/1409795.html
'''

import requests
import json
import os
import time
import datetime
import random
import jieba
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from wordcloud import WordCloud

# 评论数据保存的文件路径
COMMENT_FILE_PATH = 'jingdong_comment.txt'
# 词云图片的路径
WC_MASK_IMG = 'man.jpg'
# 词云字体
WC_FONT_PATH = 'C:\Windows\Fonts\simsun.ttc'
# 生成的词云图片保存路径
XSQ_CLOUD_IMAGE = 'xsq-cloud.jpg'


def spider_comment(page=0):
    '''
    获取评论内容并写入文件
    :param page:
    :return:
    '''
    # 评价的url
    url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv1569&productId=1409795&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1' % page
    try:
        kv = {
            'Referer': 'https://item.jd.com/1409795.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
        }
        r = requests.get(url, headers=kv)
        r.raise_for_status()
    except Exception as e:
        print('！！！爬取失败，出现异常！！！')
        raise e

    # 获取json字符串
    r_json_str = r.text[len('fetchJSON_comment98vv1569('):-2]
    # 字符串转json对象
    r_json_obj = json.loads(r_json_str)
    # 提取comments属性值，值为所有评论对象的集合
    r_json_comments = r_json_obj['comments']

    # 获取每条评论的内容，写入文件
    for r_json_comment in r_json_comments:
        with open(COMMENT_FILE_PATH, 'a+') as file:
            file.write(r_json_comment['content'] + '\n')
            print('写入文件内容：' + r_json_comment['content'])


def batch_get_comment():
    '''
    循环请求数据，写入文件
    :return:
    '''
    # 写入数据前先清空之前的数据
    if os.path.exists(COMMENT_FILE_PATH):
        # 有数据
        os.remove(COMMENT_FILE_PATH)
        print('清空文件原有数据')

    start = datetime.datetime.now()
    for i in range(100):
        spider_comment(i)
        # 随即暂停，防止ip被禁，参数单位为秒
        # random.random()为0-1之间的随机数
        time.sleep(random.random() * 5)
    end = datetime.datetime.now()
    print('爬虫并写文件耗时==> ' + str(end - start))
    print('数据写入文件完毕')


def cut_word():
    '''
    将结果进行分词
    :return:
    '''
    with open(COMMENT_FILE_PATH) as file:
        comment_txt = file.read()
        wordList = jieba.cut(comment_txt, cut_all=True)
        wl = ' '.join(wordList)
        print(wl)
        return wl


def create_word_cloud():
    '''
    生成词云
    :return:
    '''
    # 设置词云图片形状
    wc_mask = np.array(Image.open(WC_MASK_IMG))
    wc = WordCloud(
        background_color='white',
        max_words=200,
        # wc_mask在上面读取了一张图片，则生成的结果会以这张图片为底图来制作词云形状，否则则使用默认的形状
        mask=wc_mask,
        scale=4,
        max_font_size=50,
        random_state=30,
        font_path=WC_FONT_PATH
    )

    # 生成词云
    wc.generate(cut_word())
    # 保存结果图片
    wc.to_file(XSQ_CLOUD_IMAGE)

    # 在只设置mask的情况下，你将会得到一个拥有图片形状的词云
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.figure()
    plt.show()


if __name__ == '__main__':
    # 1.获取评论
    batch_get_comment()
    # 2.生成词云图
    create_word_cloud()
