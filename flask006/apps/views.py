import os
from functools import wraps
import uuid
import shutil
from flask import flash, session, make_response
from flask import request, render_template, redirect, url_for
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from werkzeug.security import generate_password_hash
from apps import app
from apps.utils import secure_filename_with_uuid
from apps.forms import LoginForm, RegistForm, PwdForm, InfoForm
from apps.models import User
from apps import db

# 创建 UploadSet 类的实例
photosSet = UploadSet(name='photos', extensions=IMAGES)

# 配置FlaskUpLoad 和 app
configure_uploads(app, photosSet)


# 登陆装饰器检查登录状态
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_name" not in session:
            return redirect(url_for("user_login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form["user_name"]
        userpwd = request.form["user_pwd"]
        # 查看用户名是否存在
        user_x = User.query.filter_by(name=username).first()
        if not user_x:
            flash("用户名不存在！", category='err')
            return render_template('user_login.html', form=form)
        else:
            if not user_x.check_pwd(str(userpwd)):
                flash("用户密码输入错误！", category='err')
                return render_template('user_login.html', form=form)
            else:
                # flash("登陆成功！", category='ok')
                session["user_name"] = user_x.name
                session["user_id"] = user_x.id
                return redirect(url_for("index"))
    return render_template('user_login.html', form=form)


@app.route('/user/logout')
@user_login_req
def logout():
    # remove the username from the session if it's there
    session.pop('user_name', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user/regist/', methods=['GET', 'POST'])
def user_regist():
    form = RegistForm()
    if form.validate_on_submit():
        # 查看用户名是否已经存在
        user_name = form.user_name.data
        user_x = User.query.filter_by(name=user_name).first()
        if user_x:
            flash("用户名已经存在！", category='err')
            return render_template('user_regist.html', form=form)
        # 如果用户不存在，创建一个用户类的实例
        user = User()
        user.name = form.user_name.data
        user.pwd = generate_password_hash(form.user_pwd.data)
        user.email = form.data['user_email']
        user.phone = form.user_phone.data
        user.jianjie = form.user_jianjie.data
        user.uuid = str(uuid.uuid4().hex)[0:10]  # 给每个用户分配一个10个字符的身份标识符
        filestorage = request.files["user_face"]
        user.face = secure_filename_with_uuid(filestorage.filename)
        # 保存用户头像文件，执行插入操作
        try:
            photosSet.save(storage=filestorage, folder=user.name, name=user.face)
            db.session.add(user)
            db.session.commit()
            flash("用户注册成功！", category='ok')
            return redirect(url_for("user_login", username=user.name))
        except UploadNotAllowed:
            flash("头像文件格式不对！", category='err')
            return render_template('user_regist.html', form=form)
    return render_template('user_regist.html', form=form)


@app.route('/user/center/')
@user_login_req
def user_center():
    return render_template("user_center.html")


@app.route('/user/detail/')
@user_login_req
def user_detail():
    user = User.query.get_or_404(int(session.get("user_id")))
    face_url = photosSet.url(user.name + '/' + user.face)
    return render_template("user_detail.html", user=user, face_url=face_url)


@app.route('/user/pwd/', methods=["GET", "POST"])
@user_login_req
def user_pwd():
    form = PwdForm()
    if form.validate_on_submit():
        old_pwd = form.old_pwd.data
        new_pwd = form.data["new_pwd"]
        user = User.query.get_or_404(int(session.get("user_id")))
        if user.check_pwd(old_pwd):
            user.pwd = generate_password_hash(new_pwd)
            db.session.add(user)
            db.session.commit()
            session.pop("user_name", None)
            session.pop('user_id', None)
            flash(message="修改密码成功，请重新登录！", category='ok')
            return redirect(url_for("user_login", username=user.name))
        else:
            flash(message="旧密码输入错误！", category='err')
            return render_template("user_pwd.html", form=form)
    return render_template("user_pwd.html", form=form)


@app.route('/user/info/', methods=["GET", "POST"])
@user_login_req
def user_info():
    form = InfoForm()
    user = User.query.get_or_404(int(session.get("user_id")))
    if request.method == "GET":
        form.user_jianjie.data = user.jianjie
    if form.validate_on_submit():
        old_name = user.name
        user.name = form.data["user_name"]
        user.email = form.data["user_email"]
        user.phone = form.data["user_phone"]
        user.jianjie = form.user_jianjie.data
        filestorage = request.files["user_face"]
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
        db.session.add(user)
        db.session.commit()
        session["user_name"] = user.name
        session["user_id"] = user.id
        return redirect(url_for("user_detail"))
    return render_template("user_info.html", user=user, form=form)


@app.route('/user/del/', methods=["GET", "POST"])
@user_login_req
def user_del():
    if request.method == "POST":
        # 删除用户的上传的文件资源
        del_path = os.path.join(app.config["UPLOADS_FOLDER"], session.get("user_name"))
        shutil.rmtree(del_path, ignore_errors=True)
        # 删除用户在数据库的记录
        user = User.query.get_or_404(int(session.get("user_id")))
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("logout"))
    return render_template("user_del.html")


@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    return resp
