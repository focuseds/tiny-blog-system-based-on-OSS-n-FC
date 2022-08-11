#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
from datetime import timedelta
from functools import wraps

import oss2
from flask import Flask, render_template, request, redirect, session
from webassets import Bundle

from config import AccessKey_ID, AccessKeySecret, site_domain, OSS_TEST_BUCKET, OSS_TEST_ENDPOINT
from flask_assets import Environment
from utils import get_img_content, up_to_oss

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', AccessKey_ID)
access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', AccessKeySecret)
bucket_name = os.getenv('OSS_TEST_BUCKET', OSS_TEST_BUCKET)
endpoint = os.getenv('OSS_TEST_ENDPOINT', OSS_TEST_ENDPOINT)

# 确认参数
for param in (access_key_id, access_key_secret, bucket_name, endpoint):
    assert '<' not in param, '请设置参数：' + param

# 创建Bucket对象
bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)


def is_login(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            return redirect(site_domain + '/login/')

    return check_login


# @app.before_request
# def before_request():
#     if request.url.startswith('http://'):
#         url = request.url.replace('http://', 'https://', 1)
#         return redirect(url, code=301)


@app.route('/login/', methods=['GET', 'POST'], strict_slashes=False)
def login():
    """
    认证函数
    """
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'welcome':
            session['user_id'] = os.urandom(8)
            # print(session['user_id'])
            return redirect(site_domain)
        else:
            return redirect(site_domain + '/login/')


@app.route('/files/', methods=['GET', 'POST'], strict_slashes=False)
@is_login
def files():
    """
    上传文件到OSS
    """
    picture = request.files['picture']
    title = request.form.get('title')
    content = request.form.get('content')

    if picture is None:
        return '没有检索到文件'
    else:
        # 上传文件到阿里云OSS
        res = up_to_oss(bucket, picture, content, title)

        if res.status == 200:
            # 上传成功，返回成功页
            return render_template('success.html')
        else:
            return redirect('/uploads/')


@app.route('/uploads/', methods=['GET'], strict_slashes=False)
@is_login
def uploads():
    """
    上传入口
    """
    return render_template('uploads.html')


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
@is_login
def get_list():
    o = request.args.get('o')
    p = request.args.get('p')
    q = request.args.get('q')

    display = 1 if q == 'on' else 0
    image_btn = 0 if display == 1 else 1
    full_btn = 0 if p == 'all' else 1

    # 获取OSS所有打卡信息
    day_list = get_img_content(bucket, o)

    if not full_btn:
        # 全部展示
        return render_template('index.html',
                               day_list=day_list,
                               #    daily_content=daily_content,
                               daily_content="",
                               display=display,
                               image_btn=image_btn,
                               full_btn=full_btn
                               )
    else:
        # 默认展示前n条
        day_list = day_list[:4:1]

        return render_template('index.html',
                               day_list=day_list,
                               #    daily_content=daily_content,
                               daily_content="",
                               display=display,
                               image_btn=image_btn,
                               full_btn=full_btn
                               )


@app.route('/logout/', methods=['GET'], strict_slashes=False)
@is_login
def logout():
    session.pop('user_id', None)
    return redirect('/login/')


# Flask-Assets's config
# Can not compress the CSS/JS on Dev environment.
app.config['ASSETS_DEBUG'] = False

# Create the Flask-Assets's instance
assets_env = Environment(app)

# Define the set for js and css file.
css = Bundle(
    'css/style.css',
    'css/uploads.css',
    filters='cssmin',
    output='assets/css/common.css')

js = Bundle(
    # 'js/index.js',
    filters='jsmin',
    output='assets/js/common.js')

# register
assets_env.register('js', js)
assets_env.register('css', css)

if __name__ == '__main__':
    app.run()


def handler(environ, start_response):
    return app(environ, start_response)
