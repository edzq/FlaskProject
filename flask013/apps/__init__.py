import os

from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql

from apps.utils import create_folder

app = Flask(__name__)
app.debug = True

app.config["SECRET_KEY"] = 'who am i ? do you know?'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flasker.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/flasker"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

APPS_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(APPS_DIR, 'static')
app.config["UPLOADS_RELATIVE"] = 'uploads'
app.config["UPLOADS_FOLDER"] = os.path.join(STATIC_DIR, app.config["UPLOADS_RELATIVE"])
# 第一步：配置 上传文件保存地址
app.config['UPLOADED_PHOTOS_DEST'] = app.config["UPLOADS_FOLDER"]
app.config['UPLOADED_IMGS_DEST'] = app.config["UPLOADS_FOLDER"]
app.config['UPLOADED_FILES_DEST'] = app.config["UPLOADS_FOLDER"]
app.config['UPLOADED_MUSICCOVERS_DEST'] = app.config["UPLOADS_FOLDER"]
app.config['UPLOADED_MUSICAUDIOS_DEST'] = app.config["UPLOADS_FOLDER"]
app.config['UPLOADED_MUSICLRCS_DEST'] = app.config["UPLOADS_FOLDER"]

create_folder(app.config["UPLOADS_FOLDER"])

from apps.admin import admin_bp
from apps.home import home_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(home_bp)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/page_not_found.html'), 404
