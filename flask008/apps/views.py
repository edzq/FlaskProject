import os
from functools import wraps
from random import randint
import uuid
import shutil
from flask import flash, session, make_response
from flask import request, render_template, redirect, url_for
from flask_uploads import UploadSet, IMAGES, configure_uploads, UploadNotAllowed
from werkzeug.security import generate_password_hash
from apps import app
from apps.utils import secure_filename_with_uuid, check_filestorages_extension, ALLOWED_IMAGE_EXTENSIONS, \
    create_thumbnail, create_show
from apps.forms import LoginForm, RegistForm, PwdForm, InfoForm, PhotoAddForm
from apps.forms import AlbumInfoForm, AlbumUploadForm
from apps.models import User, Album, Photo, AlbumTag, AlbumFavor
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

        user_x = User.query.filter_by(email=form.user_email.data).first()
        if user_x:
            flash("邮箱已经被注册过！", category='err')
            return render_template('user_regist.html', form=form)
        user_x = User.query.filter_by(phone=form.user_phone.data).first()
        if user_x:
            flash("手机号已经被注册过！", category='err')
            return render_template('user_regist.html', form=form)
        # 如果用户不存在，创建一个用户类的实例
        user = User()
        user.name = form.user_name.data
        user.pwd = generate_password_hash(form.user_pwd.data)
        user.email = form.user_email.data
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
        # 查询到当前登陆的用户
        user = User.query.get_or_404(int(session.get("user_id")))
        # 删除用户上传的所有图片的记录
        for album in user.albums:
            for photo in album.photos:
                db.session.delete(photo)
                db.session.commit()
            for favor in album.favors:
                db.session.delete(favor)
                db.session.commit()
            db.session.delete(album)
            db.session.commit()
        # 删除用户在数据库的记录
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("logout"))
    return render_template("user_del.html")


# 设置给定的相册列表的每一个相册的封面
def set_cover_url(albums, isRand=True):
    for item in albums:
        if isRand:
            item.cover = item.photos[randint(0, len(item.photos) - 1)].thumbname
        folder = item.user.name + '/' + item.title
        coverimgurl = photosSet.url(filename=folder + '/' + item.cover)
        item.coverimgurl = coverimgurl


@app.route('/album/')
def album_index():
    recmm_albums = Album.query.filter(Album.privacy != 'private', Album.recommed == 2). \
                       order_by(Album.clicknum.desc()).all()[0:4]
    set_cover_url(recmm_albums)

    newest_albums = Album.query.filter(Album.privacy != 'private') \
                        .order_by(Album.addtime.desc()).all()[0:4]
    set_cover_url(newest_albums)

    hotest_albums = Album.query.filter(Album.privacy != 'private') \
                        .order_by(Album.clicknum.desc()).all()[0:8]
    set_cover_url(hotest_albums)
    return render_template("album_index.html", recmm_albums=recmm_albums,
                           newest_albums=newest_albums, hotest_albums=hotest_albums)


@app.route('/album/create', methods=["GET", "POST"])
@user_login_req
def album_create():
    form = AlbumInfoForm()
    if form.validate_on_submit():
        album_title = form.album_title.data
        existedCount = Album.query.filter(Album.user_id == session['user_id'],
                                          Album.title == album_title).count()
        if existedCount >= 1:
            flash(message="这个相册已经存在！重取个名字吧！或者更新已有相册！", category='err')
            return render_template("album_create.html", form=form)
        album_desc = form.album_desc.data
        album_privacy = form.album_privacy.data
        album_tag = form.album_tag.data
        album_recmm = form.album_recmm.data
        existed = True
        album_uuid = str(uuid.uuid4().hex)[0:10]
        # 确保UUID的唯一性
        while existed:
            if Album.query.filter_by(uuid=album_uuid).count() > 0:
                album_uuid = str(uuid.uuid4().hex)[0:10]
            else:
                existed = False
        # 使用从表单接收到的数据创建一个Album类对象，加入album数据表
        album = Album(title=album_title, desc=album_desc,
                      privacy=album_privacy, tag_id=album_tag,
                      uuid=album_uuid, recommed=album_recmm,
                      user_id=int(session.get("user_id")))
        db.session.add(album)
        db.session.commit()
        return redirect(url_for("album_upload"))
    return render_template("album_create.html", form=form)


@app.route('/album/upload', methods=["GET", "POST"])
@user_login_req
def album_upload():
    form = AlbumUploadForm()
    albums = Album.query.filter_by(user_id=session.get("user_id")).all()
    form.album_title.choices = [(item.id, item.title) for item in albums]
    if len(form.album_title.choices) < 1:
        flash(message="请先创建一个相册！再上传照片", category='err')
        return redirect(url_for("album_create"))
    if request.method == "POST":
        # 通过 files.getlist() 获得上传的 FileStorage 文件对象列表
        fses = request.files.getlist("album_upload")
        # 检查文件扩展名，将合格的文件过滤出来
        valid_fses = check_filestorages_extension(fses, ALLOWED_IMAGE_EXTENSIONS)
        if len(valid_fses) < 1:
            flash(message="只允许上传文件类型：" + str(ALLOWED_IMAGE_EXTENSIONS), category='err')
            return redirect(url_for("album_upload"))
        else:
            files_url = []
            album_cover = ''
            # 开始遍历保存每一个合格文件
            for fs in valid_fses:
                album_title = ''
                for id, title in form.album_title.choices:
                    if id == form.album_title.data:
                        album_title = title
                folder = session.get("user_name") + '/' + album_title
                name_orig = secure_filename_with_uuid(fs.filename)
                fname = photosSet.save(fs, folder=folder, name=name_orig)
                ts_path = photosSet.config.destination + '/' + folder
                # 创建并保存缩略图
                name_thumb = create_thumbnail(path=ts_path, filename=name_orig, base_width=300)
                # 创建并保存展示图
                name_show = create_show(path=ts_path, filename=name_orig, base_width=800)
                # 把产生的Photo对象保存到数据库
                photo = Photo(origname=name_orig, showname=name_show, thumbname=name_thumb,
                              album_id=form.album_title.data)
                db.session.add(photo)
                db.session.commit()
                # 设置封面文件
                album_cover = photo.thumbname
                # 获取刚才保存的缩略图文件的url
                furl = photosSet.url(folder + '/' + name_thumb)
                files_url.append(furl)

            album = Album.query.filter_by(id=form.album_title.data).first()
            album.photonum += len(valid_fses)
            album.cover = album_cover
            db.session.add(album)
            db.session.commit()
            message = "成功保存：" + str(len(valid_fses)) + "张图像; "
            message += "当前相册共有：" + str(album.photonum) + "张图像"
            flash(message=message, category='ok')
            return render_template("album_upload.html", form=form, files_url=files_url)
    return render_template("album_upload.html", form=form)


@app.route('/album/list/<int:page>', methods=["GET"])
def album_list(page):
    albumtags = AlbumTag.query.all()
    tagid = request.args.get('tag', 'all')
    if tagid == 'all':
        albums = Album.query.filter(Album.privacy != 'private'). \
            order_by(Album.addtime.desc()).paginate(page=page, per_page=8)
    else:
        albums = Album.query.filter(Album.privacy != 'private', Album.tag_id == int(tagid)). \
            order_by(Album.addtime.desc()).paginate(page=page, per_page=8)
    for album in albums.items:
        album.cover = album.photos[randint(0, len(album.photos) - 1)].thumbname
        folder = album.user.name + '/' + album.title
        coverimgurl = photosSet.url(filename=folder + '/' + album.cover)
        album.coverimgurl = coverimgurl
    return render_template("album_list.html", albumtags=albumtags, albums=albums)


@app.route('/album/browse/<int:id>', methods=["GET"])
def album_browse(id):
    # 取出相册的基本信息
    album = Album.query.get_or_404(int(id))
    # 增加对应相册的浏览量
    album.clicknum += 1
    db.session.add(album)
    db.session.commit()
    # 查询推荐相册
    recommed_albums = Album.query.filter(Album.tag_id == album.tag_id,
                                         Album.id != album.id,
                                         Album.privacy != 'private').all()
    # 给每个推荐相册随机挑选一个封面图像
    for recmm in recommed_albums:
        recmm.cover = recmm.photos[randint(0, len(recmm.photos) - 1)].thumbname
        folder = recmm.user.name + '/' + recmm.title
        coverimgurl = photosSet.url(filename=folder + '/' + recmm.cover)
        recmm.coverimgurl = coverimgurl
    # 准备我的收藏列表
    favor_albums = []
    if 'user_id' in session:
        user = User.query.get_or_404(int(session.get('user_id')))
        for favor in user.favors:
            favor_albums.append(favor.album)
        for falbum in favor_albums:
            falbum.cover = falbum.photos[randint(0, len(falbum.photos) - 1)].thumbname
            folder = falbum.user.name + '/' + falbum.title
            coverimgurl = photosSet.url(filename=folder + '/' + falbum.cover)
            falbum.coverimgurl = coverimgurl
    # 取出作者头像的url
    userface_url = photosSet.url(filename=album.user.name + '/' + album.user.face)
    # 取出该相册下面的所有图像
    for photo in album.photos:
        photo_folder = album.user.name + '/' + album.title + '/'
        photo.url = photosSet.url(filename=photo_folder + photo.showname)
    # 用查询到的数据填充渲染页面
    return render_template("album_browse.html", album=album,
                           userface_url=userface_url,
                           recommed_albums=recommed_albums,
                           favor_albums=favor_albums)


@app.route('/album/favor/', methods=["GET"])
def album_favor():
    # 获取参数
    aid = request.args.get('aid')
    uid = request.args.get('uid')
    act = request.args.get('act')
    if act == 'add':
        # 用户不能收藏自己的相册
        album = Album.query.get_or_404(int(aid))
        if album.user_id == session.get('user_id'):
            res = {'ok': -1}
        else:
            # 查询数据库是否已经存在这样一个记录
            existedCount = AlbumFavor.query.filter_by(user_id=uid, album_id=aid).count()
            if existedCount >= 1:
                res = {'ok': 0}
            else:
                # 如果没有收藏，就添加到收藏数据库
                favor = AlbumFavor(user_id=uid, album_id=aid)
                db.session.add(favor)
                db.session.commit()
                res = {'ok': 1}
                # 累计该相册的收藏量
                album.favornum += 1
                db.session.add(album)
                db.session.commit()
    if act == 'del':
        favor = AlbumFavor.query.filter_by(user_id=uid, album_id=aid).first_or_404()
        db.session.delete(favor)
        db.session.commit()
        res = {'ok': 2}
        album = Album.query.get_or_404(int(aid))
        album.favornum -= 1
        db.session.add(album)
        db.session.commit()
    import json
    return json.dumps(res)


@app.route('/user/album/favor/<int:page>', methods=["GET"])
def user_album_favor(page):
    albumtags = AlbumTag.query.all()
    tagid = request.args.get('tag', 'all')
    if tagid == 'all':
        albums = Album.query.join(AlbumFavor). \
            filter(Album.privacy != 'private',
                   AlbumFavor.user_id == int(session.get('user_id'))). \
            order_by(Album.addtime.desc()).paginate(page=page, per_page=6)
    else:
        albums = Album.query.join(AlbumFavor).filter(
            Album.privacy != 'private', Album.tag_id == int(tagid),
            AlbumFavor.user_id == int(session.get('user_id'))). \
            order_by(Album.addtime.desc()).paginate(page=page, per_page=6)
    for album in albums.items:
        album.cover = album.photos[randint(0, len(album.photos) - 1)].thumbname
        folder = album.user.name + '/' + album.title
        coverimgurl = photosSet.url(filename=folder + '/' + album.cover)
        album.coverimgurl = coverimgurl
    return render_template("user_album_favor.html", albumtags=albumtags, albums=albums)


@app.route('/user/album/mine/<int:page>', methods=["GET"])
def user_album_mine(page):
    albumtags = AlbumTag.query.all()
    tagid = request.args.get('tag', 'all')
    if tagid == 'all':
        albums = Album.query.filter(
            Album.user_id == int(session.get('user_id'))). \
            order_by(Album.addtime.desc()).paginate(page=page, per_page=6)
    else:
        albums = Album.query.filter(Album.tag_id == int(tagid),
                                    Album.user_id == int(session.get('user_id'))). \
            order_by(Album.addtime.desc()).paginate(page=page, per_page=6)
    for album in albums.items:
        # album.cover = album.photos[randint(0, len(album.photos) - 1)].thumbname
        folder = album.user.name + '/' + album.title
        coverimgurl = photosSet.url(filename=folder + '/' + album.cover)
        album.coverimgurl = coverimgurl
    return render_template("user_album_mine.html", albumtags=albumtags, albums=albums)


@app.route('/user/album/mine/modify/<int:id>', methods=["GET", "POST"])
def user_album_mine_modify(id):
    form = AlbumInfoForm()
    album = Album.query.get_or_404(id)
    if request.method == "GET":
        form.album_title.data = album.title
        form.album_desc.data = album.desc
        form.album_privacy.data = album.privacy
        form.album_tag.data = album.tag_id
        form.album_recmm.data = album.recommed
    if form.validate_on_submit():
        album.desc = form.album_desc.data
        album.privacy = form.album_privacy.data
        album.tag_id = int(form.album_tag.data)
        album.recommed = int(form.album_recmm.data)
        db.session.add(album)
        db.session.commit()
        return redirect(url_for('user_album_mine', page=1))
    return render_template("user_album_mine_modify.html", form=form)


@app.route('/user/album/mine/cover/<int:id>', methods=["GET"])
def user_album_mine_cover(id):
    photo = Photo.query.get_or_404(id)
    photo.album.cover = photo.thumbname
    db.session.add(photo.album)
    db.session.commit()
    return redirect(url_for('user_album_mine', page=1))


@app.route('/user/album/mine/del/<int:id>', methods=["GET"])
def user_album_mine_del(id):
    album = Album.query.get_or_404(id)
    folder = album.user.name + '/' + album.title
    # 删除相册下面的所有图像，同时清除photo表中的记录
    for photo in album.photos:
        img1path = photosSet.path(folder + '/' + photo.origname)
        img2path = photosSet.path(folder + '/' + photo.showname)
        img3path = photosSet.path(folder + '/' + photo.thumbname)
        os.remove(path=img1path)
        os.remove(path=img2path)
        os.remove(path=img3path)
        db.session.delete(photo)
        db.session.commit()
        album.photonum -= 1
    # 删除相册的收藏记录
    for favor in album.favors:
        db.session.delete(favor)
        db.session.commit()
        album.favornum -= 1
    # 删除相册文件夹
    album_path = photosSet.config.destination + '/' + folder
    shutil.rmtree(album_path)
    # 删除相册本身
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for('user_album_mine', page=1))


@app.route('/user/album/mine/add/photo/<int:id>', methods=["GET", "POST"])
def user_album_mine_photo_add(id):
    album = Album.query.get_or_404(id)
    if request.method == 'GET':
        folder = album.user.name + '/' + album.title
        for photo in album.photos:
            photo.url = photosSet.url(folder + '/' + photo.thumbname)
    if request.method == "POST":
        # 通过 files.getlist() 获得上传的 FileStorage 文件对象列表
        fses = request.files.getlist("album_upload")
        # 检查文件扩展名，将合格的文件过滤出来
        valid_fses = check_filestorages_extension(fses, ALLOWED_IMAGE_EXTENSIONS)
        if len(valid_fses) < 1:
            flash(message="只允许上传文件类型：" + str(ALLOWED_IMAGE_EXTENSIONS), category='err')
            return redirect(url_for("user_album_mine_adddel", id=id))
        else:
            # 开始遍历保存每一个合格文件
            for fs in valid_fses:
                folder = session.get("user_name") + '/' + album.title
                name_orig = secure_filename_with_uuid(fs.filename)
                fname = photosSet.save(fs, folder=folder, name=name_orig)
                ts_path = photosSet.config.destination + '/' + folder
                # 创建并保存缩略图
                name_thumb = create_thumbnail(path=ts_path, filename=name_orig, base_width=300)
                # 创建并保存展示图
                name_show = create_show(path=ts_path, filename=name_orig, base_width=800)
                # 把产生的Photo对象保存到数据库
                photo = Photo(origname=name_orig, showname=name_show, thumbname=name_thumb,
                              album_id=album.id)
                db.session.add(photo)
                db.session.commit()
            album.photonum += len(valid_fses)
            db.session.add(album)
            db.session.commit()
            message = "成功保存：" + str(len(valid_fses)) + "张图像; "
            message += "当前相册共有：" + str(album.photonum) + "张图像"
            flash(message=message, category='ok')
        return redirect(url_for("user_album_mine_photo_add", id=id))
    return render_template('user_album_mine_adddel.html',
                           album=album, form=PhotoAddForm())


@app.route('/user/album/mine/del/photo/<int:id>', methods=["GET"])
def user_album_mine_photo_del(id):
    photo = Photo.query.get_or_404(id)
    album = photo.album
    folder = photo.album.user.name + '/' + photo.album.title
    img1path = photosSet.path(folder + '/' + photo.origname)
    img2path = photosSet.path(folder + '/' + photo.showname)
    img3path = photosSet.path(folder + '/' + photo.thumbname)
    os.remove(path=img1path)
    os.remove(path=img2path)
    os.remove(path=img3path)
    db.session.delete(photo)
    db.session.commit()
    album.photonum -= 1
    db.session.add(album)
    db.session.commit()
    return redirect(url_for('user_album_mine', page=1))


@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    return resp
