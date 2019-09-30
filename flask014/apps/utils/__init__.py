import os
import uuid
from datetime import datetime

from werkzeug.utils import secure_filename


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, os.O_RDWR)


# 修改文件名称
def change_filename_with_timestamp_uuid(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + \
               str(uuid.uuid4().hex) + fileinfo[-1].lower()
    return filename


# 确保文件名安全性并添加时间戳
def secure_filename_with_timestamp(filename):
    fileinfo = os.path.splitext(filename)
    filename_prefix = secure_filename(fileinfo[0])
    filename = filename_prefix + "_" + datetime.now().strftime("%Y%m%d%H%M%S") \
               + fileinfo[-1].lower()
    return filename


# 确保文件名安全性并添加随机uuid
def secure_filename_with_uuid(filename):
    fileinfo = os.path.splitext(filename)
    filename_prefix = secure_filename(fileinfo[0])
    filename = filename_prefix + "_" + str(uuid.uuid4().hex)[0:6] + fileinfo[-1].lower()
    return filename


ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4', 'avi'])
ALLOWED_AUDIO_EXTENSIONS = set(['mp3', 'm4a'])


# 检查上传控件上传的(多个)文件的后缀名是否符合指定的要求
def check_files_extension(filenameslist, allowed_extensions):
    for fname in filenameslist:
        check_state = '.' in fname and \
                      fname.rsplit('.', 1)[1].lower() in allowed_extensions
        # 只要发现一个文件不合格立即返回False,不去检查剩下的文件
        if not check_state:
            return False
    return True


# 检查上传控件上传的(多个)文件的后缀名是否符合指定的要求
def check_filestorages_extension(filestoragelist, allowed_extensions):
    ext_valid_fs = []
    for fs in filestoragelist:
        check_state = '.' in fs.filename and \
                      fs.filename.rsplit('.', 1)[1].lower() in allowed_extensions
        # 只要发现一个文件不合格立即返回False,不去检查剩下的文件
        if check_state:
            ext_valid_fs.append(fs)
    return ext_valid_fs


import PIL

from PIL import Image


def create_thumbnail(path, filename, base_width=300):
    imgname, ext = os.path.splitext(filename)
    newfilename = imgname + '_thumb_' + ext  # 缩略图的文件名
    img = Image.open(os.path.join(path, filename))  # 根据指定的路径打开图像文件
    # 如果图片宽度大于base_width，将其缩放到basewith,并保持图像原来的宽高比
    if img.size[0] > base_width:
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(os.path.join(path, newfilename))
    return newfilename


def create_show(path, filename, base_width=800):
    imgname, ext = os.path.splitext(filename)
    newfilename = imgname + '_show_' + ext  # 展示图的文件名
    img = Image.open(os.path.join(path, filename))  # 根据指定的路径打开图像文件
    # 如果图片宽度大于base_width，将其缩放到basewith,并保持图像原来的宽高比
    if img.size[0] < base_width:
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(os.path.join(path, newfilename))
    return newfilename
