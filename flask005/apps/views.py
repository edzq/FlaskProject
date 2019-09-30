import os
from functools import wraps

import shutil
from flask import flash, session, make_response
from flask import request, render_template, redirect, url_for
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed

from apps import app
from apps.utils import secure_filename_with_uuid

# 登陆装饰器检查登录状态
from apps.forms import LoginForm, RegistForm, PwdForm, InfoForm
from apps.model import User
from apps.sqlite3_manage import query_user_by_name, query_users_from_db, \
    insert_user_to_db, delete_user_by_name, update_user_by_name

# 创建 UploadSet 类的实例
photosSet = UploadSet(name='photos', extensions=IMAGES)

# 配置FlaskUpLoad 和 app
configure_uploads(app, photosSet)


def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_name" not in session:
            return redirect(url_for("user_login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    users = query_users_from_db()
    for user in users:
        print(user.toList())
    return render_template("index.html")


@app.route('/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form["user_name"]
        userpwd = request.form["user_pwd"]
        # 查看用户名是否存在
        user_x = query_user_by_name(username)
        if not user_x:
            flash("用户名不存在！", category='err')
            return render_template('user_login.html', form=form)
        else:
            if str(userpwd) != str(user_x.pwd):
                flash("用户密码输入错误！", category='err')
                return render_template('user_login.html', form=form)
            else:
                # flash("登陆成功！", category='ok')
                session["user_name"] = user_x.name
                return redirect(url_for("index"))
    return render_template('user_login.html', form=form)


@app.route('/logout')
@user_login_req
def logout():
    # remove the username from the session if it's there
    session.pop('user_name', None)
    return redirect(url_for('index'))


@app.route('/regist/', methods=['GET', 'POST'])
def user_regist():
    form = RegistForm()
    if form.validate_on_submit():
        # 查看用户名是否已经存在
        user_name = form.user_name.data
        user_x = query_user_by_name(user_name)
        if user_x:
            flash("用户名已经存在！", category='err')
            return render_template('user_regist.html', form=form)
        # 如果用户不存在，执行注册
        user = User()
        user.name = form.user_name.data
        user.pwd = form.user_pwd.data
        user.email = form.data['user_email']
        user.age = form.user_edge.data
        user.birthday = form.data["user_birthday"]
        filestorage = request.files["user_face"]
        user.face = secure_filename_with_uuid(filestorage.filename)
        # 如果用户不存在，执行插入操作
        insert_user_to_db(user)
        # 保存用户头像文件
        try:
            photosSet.save(storage=filestorage, folder=user.name, name=user.face)
            flash("用户注册成功！", category='ok')
            return redirect(url_for("user_login", username=user.name))
        except UploadNotAllowed:
            flash("头像文件格式不对！", category='err')
            return render_template('user_regist.html', form=form)

    return render_template('user_regist.html', form=form)


@app.route('/center/')
@user_login_req
def user_center():
    return render_template("user_center.html")


@app.route('/detail/')
@user_login_req
def user_detail():
    user = query_user_by_name(session.get("user_name"))
    face_url = photosSet.url(user.name + '/' + user.face)
    return render_template("user_detail.html", user=user, face_url=face_url)


@app.route('/pwd/', methods=["GET", "POST"])
@user_login_req
def user_pwd():
    form = PwdForm()
    if form.validate_on_submit():
        old_pwd = form.old_pwd.data
        new_pwd = form.data["new_pwd"]
        user = query_user_by_name(session.get("user_name"))
        if str(old_pwd) == str(user.pwd):
            user.pwd = new_pwd
            update_user_by_name(user.name, user)
            session.pop("user_name", None)
            flash(message="修改密码成功，请重新登录！", category='ok')
            return redirect(url_for("user_login", username=user.name))
        else:
            flash(message="旧密码输入错误！", category='err')
            return render_template("user_pwd.html", form=form)
    return render_template("user_pwd.html", form=form)


@app.route('/info/', methods=["GET", "POST"])
@user_login_req
def user_info():
    form = InfoForm()
    user = query_user_by_name(session.get("user_name"))
    if form.validate_on_submit():
        old_name = user.name
        user.name = form.data["user_name"]
        user.email = form.data["user_email"]
        user.age = form.data["user_edge"]
        user.birthday = form.data["user_birthday"]
        filestorage = form.user_face.data
        # 判断用户是否上传了新的头像文件
        if filestorage.filename != "":
            # 如果上传了符合要求的新的头像文件，则首先删除旧的，再保存新的
            userface_path = photosSet.path(filename=user.face, folder=old_name)
            os.remove(path=userface_path)
            # 更新 user.face 中保存的头像文件名
            user.face = secure_filename_with_uuid(filestorage.filename)
            photosSet.save(storage=filestorage, folder=old_name, name=user.face)

        # 如果用户修改了用户名， 就修改用户的上传文件夹
        if old_name != user.name:
            os.rename(os.path.join(app.config["UPLOADS_FOLDER"], old_name),
                      os.path.join(app.config["UPLOADS_FOLDER"], user.name))
        # 更新数据项
        update_user_by_name(old_name, user)
        session["user_name"] = user.name
        return redirect(url_for("user_detail"))
    return render_template("user_info.html", user=user, form=form)


@app.route('/del/', methods=["GET", "POST"])
@user_login_req
def user_del():
    if request.method == "POST":
        # 删除用户的上传的文件资源
        del_path = os.path.join(app.config["UPLOADS_FOLDER"],
                                session.get("user_name"))
        shutil.rmtree(del_path, ignore_errors=True)
        # 删除用户在数据库的记录
        delete_user_by_name(session.get("user_name"))
        return redirect(url_for("logout"))
    return render_template("user_del.html")


@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    return resp
