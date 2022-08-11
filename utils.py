#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time
from datetime import datetime
from urllib.parse import quote, unquote

import oss2
import pytz
from oss2.headers import OSS_OBJECT_TAGGING

from config import prefix


def convert_month_dir(month):
    if month:
        pass  # TODO: 分月份预览
    else:
        month = ''
        return month


def get_img_content(bucket, month):
    month = convert_month_dir(month)
    day_list = []
    element = {}
    for obj in oss2.ObjectIterator(bucket, prefix=prefix + '/' + month):
        tag = bucket.get_object_tagging(obj.key)
        pic_name = obj.key
        pic_name = pic_name.split('/')
        pic_name = pic_name[2]
        tmp_name = pic_name
        pic_name = unquote(pic_name)
        element['name'] = pic_name
        url = bucket.sign_url('GET', obj.key, 60)
        # 图片压缩，需要根据OSS设置配置启用
        # url = url.replace("?", "?x-oss-process=image/auto-orient,1/quality,q_80/format,webp&")
        element['url'] = url
        tag_list = []
        for key in tag.tag_set.tagging_rule:
            tag_list.append(tag.tag_set.tagging_rule[key])

        # 服务器时间同步
        a = time.strftime("%b %d %Y  %H:%M:%S", time.localtime(int(float(tag_list[2]))))
        b = datetime.strptime(a, "%b %d %Y %H:%M:%S")
        c = pytz.timezone("Asia/Shanghai").localize(b)
        tag_list[1] = c.strftime("%b %d, %Y  %H:%M:%S")

        element['tag'] = tag_list

        day_list.append(element)
        element = {}

    def take_tag_timestamp(elem):
        return elem['tag'][2]

    # 按照时间线倒序排列
    day_list.sort(key=take_tag_timestamp, reverse=True)

    """
    [
        {
            'name': '第一条博文', 
            'url': 'https://pic.in.oss.url', 
            'tag': ['这是博文内容！', 'Mar 05', '1583404105.9700904']
        }
    ]

    """
    return day_list


def up_to_oss(bucket, picture, des, title):
    # 上传文件到阿里云OSS
    # 图片分类打标记
    month = str(time.strftime("%b-%Y", time.localtime()))  # Apr-2020
    daytime = str(time.strftime("%b %d", time.localtime()))  # Mar 03
    timestamp = str(time.time())

    detail = str(des)

    # 转码URLCODE
    detail = quote(detail)

    # http header中设置标签信息。
    headers = dict()
    headers[OSS_OBJECT_TAGGING] = "time={}&content={}&timestamp={}".format(daytime, detail, timestamp)

    # 按月读取图片
    filename = prefix + "/" + str(month) + "/" + str(title)

    filename = quote(filename)

    # FilesStorage TO FileObject
    pic = picture.read()
    res = bucket.put_object(filename, pic, headers=headers)

    return res
