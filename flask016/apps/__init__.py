# _*_ coding:utf-8 _*_
import os

from flask import Flask
from flask import render_template
from flask_uploads import UploadSet, IMAGES, AUDIO, configure_uploads, DOCUMENTS, ARCHIVES
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import pymysql

from apps.utils import create_folder

app = Flask(__name__)
app.debug = True

app.config["SECRET_KEY"] = 'who am i ? do you know?'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

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
app.config['UPLOADED_MOVIECOVERS_DEST'] = app.config["UPLOADS_FOLDER"]
app.config['UPLOADED_MOVIEVIDEOS_DEST'] = app.config["UPLOADS_FOLDER"]
# 创建 UploadSet 类的实例
photosSet = UploadSet(name='photos', extensions=IMAGES)
imgsSet = UploadSet(name='imgs', extensions=IMAGES)
filesSet = UploadSet(name='files', extensions=AUDIO + ARCHIVES + DOCUMENTS)
musicCoversSet = UploadSet(name='musiccovers', extensions=IMAGES)
musicAudiosSet = UploadSet(name='musicaudios', extensions=AUDIO)
musicLrcsSet = UploadSet(name='musiclrcs', extensions=('lrc',))
movieCoversSet = UploadSet(name='moviecovers', extensions=IMAGES)
movieVideosSet = UploadSet(name='movievideos', extensions=('mp4',))
# 配置FlaskUpLoad 和 app
configure_uploads(app, photosSet)
configure_uploads(app, imgsSet)
configure_uploads(app, filesSet)
configure_uploads(app, musicCoversSet)
configure_uploads(app, musicAudiosSet)
configure_uploads(app, musicLrcsSet)
configure_uploads(app, movieCoversSet)
configure_uploads(app, movieVideosSet)

create_folder(app.config["UPLOADS_FOLDER"])

from apps.admin import admin_bp
from apps.home import home_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(home_bp)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/page_not_found.html'), 404
