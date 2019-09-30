import os

from flask import flash
from flask import render_template, request, url_for, send_from_directory
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed

from apps import app

# 第二步：产生UploadSet类对象的实例，用来管理上传集合
photosSet = UploadSet('photos', IMAGES)

# 第三步：绑定 app 与 UploadSet对象实例
configure_uploads(app, (photosSet,))


@app.route('/index', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        fs = request.files["image_upload"]
        if fs.filename != "":
            # 这个使用 FileStorage 的save 方法保存文件
            # file_path = os.path.join(app.config["ABS_UPLOAD_FOLDER"], fs.filename)
            # fs.save(file_path)

            # 第四步：使用 UploadSet 的save 方法保存文件
            fname = photosSet.save(fs)
            file_url = url_for("static", filename="uploads/" + fname)
            file_url2 = url_for("uploaded_file", filename=fname)
            # 第五步：使用 UploadSet 的 url 方法获得文件的url
            file_url3 = photosSet.url(fname)
            return render_template("index.html",
                                   file_url=file_url,
                                   file_url2=file_url2,
                                   file_url3=file_url3)
    return render_template("index.html")


@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["ABS_UPLOAD_FOLDER"], filename)


@app.route('/', methods=["GET", "POST"])
def index2():
    if request.method == "POST":
        folder = request.form["image_folder"]
        fs = request.files["image_file"]
        if fs.filename != "":
            try:
                fname = photosSet.save(storage=fs, folder=folder, name=fs.filename)
                print(fname)
            except UploadNotAllowed:
                flash(message="上传文件失败！", category='err')
                return render_template("index2.html")
            else:
                # fpath = photosSet.path(filename="啦啦啦啦.jpg", folder=folder)
                # os.remove(fpath)
                furl = photosSet.url(fname)
                print(furl)
                flash(message="上传文件成功！", category='ok')
                return render_template("index2.html", file_url=furl)
    return render_template("index2.html")
