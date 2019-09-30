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


ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp'])
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
