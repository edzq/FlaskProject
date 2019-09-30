import os

from flask import Flask

from apps.utils import creat_folder

app = Flask(__name__)

app.debug = True

app.config["SECRET_KEY"] = "我有一个小秘密，就不告诉你！"

APPS_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(APPS_DIR, "static")

app.config['UPLOAD_FOLDER'] = "uploads"
app.config['ABS_UPLOAD_FOLDER'] = \
    os.path.join(STATIC_DIR, app.config['UPLOAD_FOLDER'])

# 第一步：配置 上传文件保存地址
app.config['UPLOADED_PHOTOS_DEST'] = app.config['ABS_UPLOAD_FOLDER']

creat_folder(app.config['ABS_UPLOAD_FOLDER'])

import apps.views
