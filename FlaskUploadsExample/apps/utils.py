import os


def creat_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, os.O_RDWR)
