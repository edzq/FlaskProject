import os
import uuid
from functools import wraps

import shutil
from random import randint

from flask import render_template, session, redirect, url_for, request, flash, jsonify
from flask_uploads import UploadNotAllowed, IMAGES, AUDIO, ARCHIVES, DOCUMENTS
from werkzeug.security import generate_password_hash
from flask_wtf.file import FileAllowed

from apps import app, db, photosSet, imgsSet, filesSet, musicCoversSet, musicLrcsSet, musicAudiosSet, movieCoversSet, \
    movieVideosSet
from apps.home import home_bp as home
from apps.home.forms import LoginForm, RegistForm, PwdForm, InfoForm, AlbumInfoForm, AlbumSelectForm, PhotoAddForm, \
    ArticleInfoForm, ArticleWriteForm, MusicCommentForm, MovieCommentForm
from apps.models import User, Album, Photo, AlbumTag, AlbumFavor, ArticleTag, Article, ArticleFavor, MusicLangTag, \
    MusicStyleTag, MusicThemeTag, MusicEmotionTag, MusicSceneTag, Music, MusicFavor, MusicComment, Movie, MovieTag, \
    MovieFavor, MovieComment
from apps.utils import secure_filename_with_uuid, create_thumbnail, create_show, check_filestorages_extension, \
    ALLOWED_IMAGE_EXTENSIONS


def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_name" not in session:
            return redirect(url_for("home.user_login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@home.route('/')
def index():
    return render_template("home/index.html")


@home.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form["user_name"]
        userpwd = request.form["user_pwd"]
        # 查看用户名是否存在
        user_x = User.query.filter_by(name=username).first()
        if not user_x:
            flash("用户名不存在！", category='err')
            return render_template('home/user_login.html', form=form)
        else:
            if not user_x.check_pwd(str(userpwd)):
                flash("用户密码输入错误！", category='err')
                return render_template('home/user_login.html', form=form)
            else:
                # flash("登陆成功！", category='ok')
                session["user_name"] = user_x.name
                session["user_id"] = user_x.id
                return redirect(url_for("home.index"))
    return render_template('home/user_login.html', form=form)


@home.route('/user/logout')
@user_login_req
def logout():
    # remove the username from the session if it's there
    session.pop('user_name', None)
    session.pop('user_id', None)
    return redirect(url_for('home.index'))


@home.route('/user/regist/', methods=['GET', 'POST'])
def user_regist():
    form = RegistForm()
    if form.validate_on_submit():
        # 查看用户名是否已经存在
        user_name = form.user_name.data
        user_x = User.query.filter_by(name=user_name).first()
        if user_x:
            flash("用户名已经存在！", category='err')
            return render_template('home/user_regist.html', form=form)
        user_x = User.query.filter_by(email=form.user_email.data).first()
        if user_x:
            flash("邮箱已经被注册过！", category='err')
            return render_template('home/user_regist.html', form=form)
        user_x = User.query.filter_by(phone=form.user_phone.data).first()
        if user_x:
            flash("手机号已经被注册过！", category='err')
            return render_template('home/user_regist.html', form=form)
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
            return redirect(url_for("home.user_login", username=user.name))
        except UploadNotAllowed:
            flash("头像文件格式不对！", category='err')
            return render_template('home/user_regist.html', form=form)
    return render_template('home/user_regist.html', form=form)


@home.route('/user/center/')
@user_login_req
def user_center():
    return render_template("home/user_center.html")


@home.route('/user/detail/')
@user_login_req
def user_detail():
    user = User.query.get_or_404(int(session.get("user_id")))
    face_url = photosSet.url(user.name + '/' + user.face)
    return render_template("home/user_detail.html", user=user, face_url=face_url)


@home.route('/user/pwd/', methods=["GET", "POST"])
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
            return redirect(url_for("home.user_login", username=user.name))
        else:
            flash(message="旧密码输入错误！", category='err')
            return render_template("home/user_pwd.html", form=form)
    return render_template("home/user_pwd.html", form=form)


@home.route('/user/info/', methods=["GET", "POST"])
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
        return redirect(url_for("home.user_detail"))
    return render_template("home/user_info.html", user=user, form=form)


@home.route('/user/del/', methods=["GET", "POST"])
@user_login_req
def user_del():
    if request.method == "POST":
        # 删除用户的上传的文件资源
        del_path = os.path.join(app.config["UPLOADS_FOLDER"], session.get("user_name"))
        shutil.rmtree(del_path, ignore_errors=True)
        # 查询到当前登陆的用户
        user = User.query.get_or_404(int(session.get("user_id")))
        # 删除用户上传的所有图片，相册，相册收藏的记录,
        for album in user.albums:
            for photo in album.photos:
                db.session.delete(photo)
                # db.session.commit()
            for favor in album.favors:
                db.session.delete(favor)
                # db.session.commit()
            db.session.delete(album)
            # db.session.commit()
        # 删除与当前用户的所有文章相关的所有记录
        for article in user.articles:
            for favor in article.favors:
                db.session.delete(favor)
                # db.session.commit()
            db.session.delete(article)
            # db.session.commit()
        # 删除当前用户的收藏列表
        album_favors = AlbumFavor.query.filter_by(user_id=user.id).all()
        for item in album_favors:
            db.session.delete(item)
        article_favors = ArticleFavor.query.filter_by(user_id=user.id).all()
        for item in article_favors:
            db.session.delete(item)
        # 删除用户在数据库的记录
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("home.logout"))
    return render_template("home/user_del.html")


# 设置给定的相册列表的每一个相册的封面
def set_cover_url(albums, isRand=True):
    for item in albums:
        if isRand:
            item.cover = item.photos[randint(0, len(item.photos) - 1)].thumbname
        folder = item.user.name + '/' + item.title
        coverimgurl = photosSet.url(filename=folder + '/' + item.cover)
        item.coverimgurl = coverimgurl


@home.route('/album/')
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
    return render_template("home/album_index.html", recmm_albums=recmm_albums,
                           newest_albums=newest_albums, hotest_albums=hotest_albums)


@home.route('/album/create', methods=["GET", "POST"])
@user_login_req
def album_create():
    form = AlbumInfoForm()
    album_tags = AlbumTag.query.order_by(AlbumTag.addtime.desc()).all()
    form.album_tag.choices = [(tag.id, tag.name) for tag in album_tags]
    if form.validate_on_submit():
        album_title = form.album_title.data
        existedCount = Album.query.filter(Album.user_id == session['user_id'],
                                          Album.title == album_title).count()
        if existedCount >= 1:
            flash(message="这个相册已经存在！重取个名字吧！或者更新已有相册！", category='err')
            return render_template("home/album_create.html", form=form)
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
        return redirect(url_for("home.album_upload"))
    return render_template("home/album_create.html", form=form)


@home.route('/album/upload', methods=["GET", "POST"])
@user_login_req
def album_upload():
    form = AlbumSelectForm()
    albums = Album.query.filter_by(user_id=session.get("user_id")).all()
    form.album_title.choices = [(item.id, item.title) for item in albums]
    if len(form.album_title.choices) < 1:
        flash(message="请先创建一个相册！再上传照片", category='err')
        return redirect(url_for("home.album_create"))
    if request.method == "POST":
        fs_keys = request.files.keys()
        album_id = int(request.args.get('aid'))
        for key in fs_keys:
            fs = request.files.get(key)
            album_title = ''
            for id, title in form.album_title.choices:
                if id == album_id:
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
                          album_id=album_id)
            db.session.add(photo)
            db.session.commit()
            # 设置封面文件
            album_cover = photo.thumbname
        # 更新相册的信息
        album = Album.query.get_or_404(album_id)
        album.photonum += 1
        album.cover = album_cover
        db.session.add(album)
        db.session.commit()
        # message = "成功保存：" + str(1) + "张图像; "
        # message += "当前相册共有：" + str(album.photonum) + "张图像"
        # flash(message=message, category='ok')
        return redirect(url_for('home.album_upload'))
    return render_template("home/album_upload_dropzone.html", form=form)


@home.route('/album/list/<int:page>', methods=["GET"])
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
    return render_template("home/album_list.html", albumtags=albumtags, albums=albums)


@home.route('/album/browse/<int:id>', methods=["GET"])
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
    return render_template("home/album_browse.html", album=album,
                           userface_url=userface_url,
                           recommed_albums=recommed_albums,
                           favor_albums=favor_albums)


@home.route('/album/favor/', methods=["GET"])
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


@home.route('/album/favors/<int:page>', methods=["GET"])
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
    return render_template("home/user_album_favor.html", albumtags=albumtags, albums=albums)


@home.route('/album/mine/<int:page>', methods=["GET"])
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
    return render_template("home/user_album_mine.html", albumtags=albumtags, albums=albums)


@home.route('/album/mine/modify/<int:id>', methods=["GET", "POST"])
def user_album_mine_modify(id):
    form = AlbumInfoForm()
    album_tags = AlbumTag.query.order_by(AlbumTag.addtime.desc()).all()
    form.album_tag.choices = [(tag.id, tag.name) for tag in album_tags]
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
        return redirect(url_for('home.user_album_mine', page=1))
    return render_template("home/user_album_mine_modify.html", form=form)


@home.route('/album/mine/cover/<int:id>', methods=["GET"])
def user_album_mine_cover(id):
    photo = Photo.query.get_or_404(id)
    photo.album.cover = photo.thumbname
    db.session.add(photo.album)
    db.session.commit()
    return redirect(url_for('home.user_album_mine', page=1))


@home.route('/album/mine/del/<int:id>', methods=["GET"])
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
    return redirect(url_for('home.user_album_mine', page=1))


@home.route('/album/mine/add/photo/<int:id>', methods=["GET", "POST"])
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
            return redirect(url_for("home.user_album_mine_adddel", id=id))
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
        return redirect(url_for("home.user_album_mine_photo_add", id=id))
    return render_template('home/user_album_mine_adddel.html',
                           album=album, form=PhotoAddForm())


@home.route('/album/mine/del/photo/<int:id>', methods=["GET"])
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
    return redirect(url_for('home.user_album_mine', page=1))


# 设置给定的文章列表的每一个文章的封面
def set_article_cover_url(articles):
    for item in articles:
        coverimgurl = photosSet.url(filename=item.cover)
        item.coverimgurl = coverimgurl
        userface_url = photosSet.url(filename=item.user.name + '/' + item.user.face)
        item.userface_url = userface_url


@home.route('/article/')
def article_index():
    recmm_articles = Article.query.filter(Article.privacy != 'private', Article.recommed == 2). \
                         order_by(Article.clicknum.desc()).all()[0:4]
    set_article_cover_url(recmm_articles)

    newest_articles = Article.query.filter(Article.privacy != 'private') \
                          .order_by(Article.addtime.desc()).all()[0:4]
    set_article_cover_url(newest_articles)

    hotest_articles = Article.query.filter(Article.privacy != 'private') \
                          .order_by(Article.clicknum.desc()).all()[0:8]
    set_article_cover_url(hotest_articles)
    return render_template("home/article_index.html", recmm_articles=recmm_articles,
                           newest_articles=newest_articles, hotest_articles=hotest_articles)


@home.route('/article/list/<int:page>', methods=['GET'])
def article_list(page):
    articletags = ArticleTag.query.all()
    # 获得筛选标签，
    tag_id = request.args.get('tid', 'all')
    if tag_id == 'all':
        articles = Article.query.filter(Article.privacy != 'private'). \
            order_by(Article.addtime.desc()).paginate(page=page, per_page=6)
    else:
        articles = Article.query.filter(Article.tag_id == int(tag_id),
                                        Article.privacy != 'private'). \
            order_by(Article.addtime.desc()).paginate(page=page, per_page=6)
    # 设置每个文章的封面图像和作者头像
    set_article_cover_url(articles.items)
    return render_template("home/article_list.html",
                           articletags=articletags,
                           articles=articles)


@home.route('/article/create', methods=["GET", "POST"])
@user_login_req
def article_create():
    form = ArticleInfoForm()
    article_tags = ArticleTag.query.all()
    form.article_tag.choices = [(tag.id, tag.name) for tag in article_tags]
    if form.validate_on_submit():
        article = Article()
        article.title = form.article_title.data
        article.abstract = form.article_abstract.data
        article.privacy = form.article_privacy.data
        article.tag_id = form.article_tag.data
        article.recommed = form.article_recmm.data
        article.content = ""
        article.user_id = int(session.get("user_id"))
        article.uuid = str(uuid.uuid4().hex)[0:15]
        fs = request.files.get(form.article_cover.name)
        if fs.filename != '':
            covername = secure_filename_with_uuid(fs.filename)
            subfolder = session.get("user_name") + '/' + article.uuid
            article.cover = photosSet.save(fs, folder=subfolder, name=covername)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for("home.article_write", aid=article.id))
    return render_template("home/article_create.html", form=form)


@home.route('/article/write', methods=["GET", "POST"])
@user_login_req
def article_write():
    form = ArticleWriteForm()
    articles = Article.query.filter_by(user_id=session.get('user_id')).all()
    if len(articles) < 1:
        flash(message='请先创建文章，再来写作！', category='err')
        return redirect(url_for('home.article_create'))
    form.article_title.choices = [(item.id, item.title) for item in articles]
    if request.method == "GET":
        aid = int(request.args.get('aid', form.article_title.choices[0][0]))
        for item in articles:
            if item.id == aid:
                form.article_title.data = aid
                form.article_content.data = item.content
    if form.validate_on_submit():
        article_id = form.article_title.data
        article = Article.query.get_or_404(int(article_id))
        article.content = form.article_content.data
        db.session.add(article)
        db.session.commit()
        return redirect(url_for("home.article_list", page=1))
    return render_template('home/article_write.html', form=form)


@home.route('/article/read/<int:id>/', methods=["GET", "POST"])
def article_read(id):
    article = Article.query.get_or_404(id)
    article.clicknum += 1
    db.session.add(article)
    db.session.commit()
    userface_url = photosSet.url(filename=article.user.name + '/' + article.user.face)
    # 读取文章收藏列表(使用ORM方式或联合查表方式)
    favor_articles = []
    if 'user_id' in session:
        # user = User.query.get_or_404(int(session.get('user_id')))
        # for favor in user.articlefavors:
        #     item = favor.article
        #     item.coverimgurl = photosSet.url(filename=item.cover)
        #     favor_articles.append(item)
        favor_articles = Article.query.join(ArticleFavor). \
            filter(ArticleFavor.user_id == session.get('user_id')).all()
        for item in favor_articles:
            item.coverimgurl = photosSet.url(filename=item.cover)
    # 读取文章推荐列表
    recommed__articles = Article.query.filter(Article.tag_id == article.tag_id,
                                              Article.id != article.id,
                                              Article.privacy != 'private').all()
    for item in recommed__articles:
        item.coverimgurl = photosSet.url(filename=item.cover)
    return render_template('home/article_read.html',
                           article=article,
                           userface_url=userface_url,
                           favor_articles=favor_articles,
                           recommed__articles=recommed__articles)


@home.route('/article/favor/', methods=["GET"])
def article_favor():
    # 获取参数
    aid = request.args.get('aid')
    uid = request.args.get('uid')
    act = request.args.get('act')
    if act == 'add':
        # 用户不能收藏自己的文章
        article = Article.query.get_or_404(int(aid))
        if article.user_id == session.get('user_id'):
            res = {'ok': -1}
        else:
            # 查询数据库是否已经存在这样一个记录
            existedCount = ArticleFavor.query.filter_by(user_id=uid, article_id=aid).count()
            if existedCount >= 1:
                res = {'ok': 0}
            else:
                # 如果没有收藏，就添加到收藏数据库
                favor = ArticleFavor(user_id=uid, article_id=aid)
                db.session.add(favor)
                db.session.commit()
                res = {'ok': 1}
                # 累计该相册的收藏量
                article.favornum += 1
                db.session.add(article)
                db.session.commit()
    if act == 'del' or act == 'cancel':
        favor = ArticleFavor.query.filter_by(user_id=uid, article_id=aid).first_or_404()
        db.session.delete(favor)
        db.session.commit()
        res = {'ok': 2}
        article = Article.query.get_or_404(int(aid))
        article.favornum -= 1
        db.session.add(article)
        db.session.commit()
    if act == 'cancel':
        return redirect(url_for('home.user_article_favor', page=1))
    import json
    return json.dumps(res)


@home.route('/article/recieve/image/', methods=["GET", "POST"])
@user_login_req
def recieve_image():
    if request.method == "POST":
        # 获取CKeditor的JS回调函数reference
        CKEditorFuncNum = request.args.get('CKEditorFuncNum')
        # 获取当前正在编辑的文章ID
        articleId = request.args.get('aid')
        # 从数据库查询正在编辑的文章
        article = Article.query.get_or_404(int(articleId))
        # 获取POST请求中的files中的FileStorage对象，并保存到指定的目录
        keys = request.files.keys()
        for key in keys:
            fs = request.files.get(key)
            if fs.filename != '':
                try:
                    subfolder = session.get('user_name') + '/' + article.uuid
                    newfname = secure_filename_with_uuid(fs.filename)
                    fname = imgsSet.save(fs, folder=subfolder, name=newfname)
                    # 获取刚刚保存的文件的url
                    file_url = imgsSet.url(filename=fname)
                    # 把文件的url返回给CKEditor
                    message = '文件上传成功！'
                    # 把文件的url返回给CKEditor
                    ret_js = "<script type='text/javascript'> " \
                             "window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');" \
                             "</script>" % (CKEditorFuncNum, file_url, message)
                    return ret_js
                except UploadNotAllowed:
                    message = '扩展名不正确！只接受：' + str(IMAGES)
    return message


@home.route('/article/recieve/file/', methods=["GET", "POST"])
@user_login_req
def recieve_file():
    if request.method == "POST":
        # 获取CKeditor的JS回调函数reference
        CKEditorFuncNum = request.args.get('CKEditorFuncNum')
        # 获取当前正在编辑的文章ID
        articleId = request.args.get('aid')
        # 从数据库查询正在编辑的文章
        article = Article.query.get_or_404(int(articleId))
        # 获取POST请求中的files中的FileStorage对象，并保存到指定的目录
        fs = request.files.get('upload')
        if fs.filename != '':
            try:
                subfolder = session.get('user_name') + '/' + article.uuid
                newfname = secure_filename_with_uuid(fs.filename)
                fname = filesSet.save(fs, folder=subfolder, name=newfname)
                # 获取刚刚保存的文件的url
                file_url = imgsSet.url(filename=fname)
                # 把文件的url返回给CKEditor
                message = '文件上传成功！'
                # 把文件的url返回给CKEditor
                ret_js = "<script type='text/javascript'> " \
                         "window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');" \
                         "</script>" % (CKEditorFuncNum, file_url, message)
                return ret_js
            except UploadNotAllowed:
                message = '扩展名不正确！只接受：' + str(AUDIO + DOCUMENTS + ARCHIVES)
    return message


@home.route('/article/browse/file/', methods=["GET", "POST"])
@user_login_req
def article_browse_file():
    # 获取CKeditor的JS回调函数reference
    CKEditorFuncNum = request.args.get('CKEditorFuncNum')
    if request.args.get('type') == 'images':
        albums = Album.query.filter(Album.privacy != 'private').all()
        albumId = request.args.get('aid')
        selected_photos = []
        if albumId:
            for album in albums:
                if int(albumId) == album.id:
                    for phitem in album.photos:
                        subfolder = album.user.name + '/' + album.title + '/'
                        phitem.url = photosSet.url(filename=subfolder + phitem.thumbname)
                        selected_photos.append(phitem)
        photoId = request.args.get('phid')
        if photoId:
            photo = Photo.query.get_or_404(int(photoId))
            subfolder = photo.album.user.name + '/' + photo.album.title + '/'
            photo_url = photosSet.url(filename=subfolder + photo.origname)
            # 把文件的url返回给CKEditor
            ret_js = "<script type='text/javascript'> " \
                     "window.opener.CKEDITOR.tools.callFunction(%s, '%s');" \
                     "window.close();</script>" % (CKEditorFuncNum, photo_url)
            return ret_js
    return render_template('home/article_browse_file.html',
                           type=request.args.get('type'),
                           CKEditorFuncNum=CKEditorFuncNum,
                           albums=albums, selected_photos=selected_photos)


@home.route('/article/recieve/pasted/', methods=["GET", "POST"])
@home.route('/article/recieve/dragged/', methods=["GET", "POST"])
@user_login_req
def recieve_dragged_pasted():
    if request.method == 'POST':
        # 获取POST请求中的files中的FileStorage对象，并保存到指定的目录
        keys = request.files.keys()
        articleId = request.args.get('aid')
        article = Article.query.get_or_404(int(articleId))
        for key in keys:
            fs = request.files.get(key)
            if fs.filename != '':
                if request.args.get('type') == 'images':
                    uploadSet = imgsSet
                if request.args.get('type') == 'files':
                    uploadSet = filesSet
                try:
                    subfolder = session.get('user_name') + '/' + article.uuid
                    newfname = secure_filename_with_uuid(fs.filename)
                    fname = uploadSet.save(fs, folder=subfolder, name=newfname)
                    # 获取刚刚保存的文件的url
                    file_url = uploadSet.url(filename=fname)
                    # 把文件的url返回给CKEditor
                    res = {
                        "uploaded": 1,
                        "fileName": fname,
                        "url": file_url,
                    }
                    return jsonify(res)
                except UploadNotAllowed:
                    message = '扩展名不正确！只接受：' + str(IMAGES + AUDIO + ARCHIVES + DOCUMENTS)
                    res = {
                        "uploaded": 0,
                        "error": {
                            "message": message
                        }
                    }
                    return jsonify(res)
        return 'ok'


@home.route('/article/favors/<int:page>', methods=["GET"])
@user_login_req
def user_article_favor(page):
    articletags = ArticleTag.query.all()
    tagid = request.args.get('tag', 'all')
    if tagid == 'all':
        articles = Article.query.join(ArticleFavor). \
            filter(Article.privacy != 'private',
                   ArticleFavor.user_id == int(session.get('user_id'))). \
            order_by(Article.addtime.desc()).paginate(page=page, per_page=6)
    else:
        articles = Article.query.join(ArticleFavor). \
            filter(Article.privacy != 'private', Article.tag_id == int(tagid),
                   ArticleFavor.user_id == int(session.get('user_id'))). \
            order_by(Article.addtime.desc()).paginate(page=page, per_page=6)
    for article in articles.items:
        article.coverimgurl = photosSet.url(filename=article.cover)
    return render_template("home/user_article_favor.html", articletags=articletags, articles=articles)


@home.route('/article/mine/<int:page>', methods=["GET"])
@user_login_req
def user_article_mine(page):
    articletags = ArticleTag.query.all()
    tagid = request.args.get('tag', 'all')
    if tagid == 'all':
        articles = Article.query.filter(Article.user_id == int(session.get('user_id'))). \
            order_by(Article.addtime.desc()).paginate(page=page, per_page=6)
    else:
        articles = Article.query.filter(Article.user_id == int(session.get('user_id')),
                                        Article.tag_id == int(tagid)). \
            order_by(Article.addtime.desc()).paginate(page=page, per_page=6)
    for article in articles.items:
        article.coverimgurl = photosSet.url(filename=article.cover)
    return render_template("home/user_article_mine.html", articletags=articletags, articles=articles)


@home.route('/article/mine/modify/<int:id>', methods=["GET", "POST"])
def user_article_mine_modify(id):
    form = ArticleInfoForm()
    article_tags = ArticleTag.query.all()
    form.article_tag.choices = [(tag.id, tag.name) for tag in article_tags]
    form.article_cover.validators = [FileAllowed(IMAGES, '只允许图像格式为:%s' % str(IMAGES)), ]
    article = Article.query.get_or_404(id)
    if request.method == "GET":
        form.article_title.data = article.title
        form.article_abstract.data = article.abstract
        form.article_privacy.data = article.privacy
        form.article_tag.data = article.tag_id
        form.article_recmm.data = article.recommed
    if form.validate_on_submit():
        article.title = form.article_title.data
        article.abstract = form.article_abstract.data
        article.privacy = form.article_privacy.data
        article.tag_id = int(form.article_tag.data)
        article.recommed = int(form.article_recmm.data)
        # 保存新的封面图像
        fs = request.files.get(form.article_cover.name)
        if fs.filename != '':
            # 删除原来的封面图像
            coverpath = photosSet.path(filename=article.cover)
            if os.path.isfile(coverpath):
                os.remove(coverpath)
            covername = secure_filename_with_uuid(fs.filename)
            subfolder = session.get("user_name") + '/' + article.uuid
            article.cover = photosSet.save(fs, folder=subfolder, name=covername)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('home.user_article_mine', page=1))
    return render_template("home/user_article_mine_modify.html", form=form)


@home.route('/article/mine/del/<int:id>', methods=["GET"])
def user_article_mine_del(id):
    article = Article.query.get_or_404(id)
    # 删除文章的收藏记录
    for favor in article.favors:
        db.session.delete(favor)
        db.session.commit()
        article.favornum -= 1
    # 删除文章文件夹
    folder = article.user.name + '/' + article.uuid
    article_path = imgsSet.config.destination + '/' + folder
    shutil.rmtree(article_path)
    # 删除文章记录
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('home.user_article_mine', page=1))


@home.route('/music/')
def music_index():
    # 获取形象首页的推荐音乐
    recmd_musics = Music.query.filter(Music.recommed == 2).order_by(Music.clicknum.desc()).all()[0:4]
    for ritem in recmd_musics:
        ritem.cover_url = musicCoversSet.url(filename=ritem.coverfile)
        ritem.audio_url = musicAudiosSet.url(filename=ritem.audiofile)
    # 获取最新发布的音乐
    newest_musics = Music.query.order_by(Music.addtime.desc()).all()[0:4]
    for nitem in newest_musics:
        nitem.cover_url = musicCoversSet.url(filename=nitem.coverfile)
        nitem.audio_url = musicAudiosSet.url(filename=nitem.audiofile)
    # 获取最火的音乐
    hotest_musics = Music.query.order_by(Music.clicknum.desc()).all()[0:8]
    for hitem in hotest_musics:
        hitem.cover_url = musicCoversSet.url(filename=hitem.coverfile)
        hitem.audio_url = musicAudiosSet.url(filename=hitem.audiofile)
    return render_template('home/music_index.html', recmd_musics=recmd_musics,
                           newest_musics=newest_musics, hotest_musics=hotest_musics)


@home.route('/music/list/<int:page>')
def music_list(page):
    lang_tags = MusicLangTag.query.all()
    style_tags = MusicStyleTag.query.all()
    theme_tags = MusicThemeTag.query.all()
    emotion_tags = MusicEmotionTag.query.all()
    scene_tags = MusicSceneTag.query.all()
    lid = int(request.args.get('lid', '0'))
    sid = int(request.args.get('sid', '0'))
    tid = int(request.args.get('tid', '0'))
    eid = int(request.args.get('eid', '0'))
    scid = int(request.args.get('scid', '0'))
    p = {'lid': lid, 'sid': sid, 'tid': tid, 'eid': eid, 'scid': scid}
    musics = Music.query
    if lid != 0:
        musics = musics.filter_by(lang_id=lid)
    if sid != 0:
        musics = musics.filter_by(style_id=sid)
    if tid != 0:
        musics = musics.filter_by(theme_id=tid)
    if eid != 0:
        musics = musics.filter_by(emotion_id=eid)
    if scid != 0:
        musics = musics.filter_by(scene_id=scid)
    # 把按条件过滤得到的最终结果排序分页
    musics = musics.order_by(Music.addtime.desc()).paginate(page=page, per_page=8)
    for mitem in musics.items:
        mitem.audio_url = musicAudiosSet.url(filename=mitem.audiofile)
        mitem.cover_url = musicCoversSet.url(filename=mitem.coverfile)
    return render_template('home/music_list.html', lang_tags=lang_tags,
                           style_tags=style_tags, theme_tags=theme_tags,
                           emotion_tags=emotion_tags, scene_tags=scene_tags, musics=musics,
                           p=p)


@home.route('/music/listen/<int:id>')
def music_listen(id):
    # 获取当前音乐对象
    music = Music.query.get_or_404(id)
    # 更新播放量
    music.clicknum += 1
    db.session.add(music)
    db.session.commit()
    # 获取当前音乐文件的url
    music.audio_url = musicAudiosSet.url(music.audiofile)
    music.cover_url = musicAudiosSet.url(music.coverfile)
    # 读取歌词文件
    lrc_path = musicLrcsSet.path(filename=music.lrcfile)
    lrcf = open(file=lrc_path, mode='r', encoding='utf8')
    music.lrc = []
    for lrcline in lrcf.readlines():
        lrcline = lrcline.strip('\n')
        # print(lrcline)
        idx = lrcline.find(']') + 1  # 分割时间戳和歌词内容
        timestamp = lrcline[0:idx]
        lrccontent = lrcline[idx:]
        tidx = timestamp.find(':')  # 分割时间戳内的分钟数和秒数
        midum = timestamp[tidx - 2:tidx]
        second = timestamp[tidx + 1:tidx + 3]
        if midum == 'ti' or midum == 'ar' or midum == 'al' or midum == 'by':
            continue
        else:
            timestamp = int(midum) * 60 + int(second)  # 把时间戳转换成秒数
        # 把处理好的一行歌词添加到列表
        music.lrc.append((timestamp, lrccontent))
    # 获取推荐音乐和url
    recmm_lang_musics = Music.query.filter(Music.lang_id == music.lang_id,
                                           Music.id != music.id).all()[0:6]
    for recmm_lang in recmm_lang_musics:
        recmm_lang.cover_url = musicCoversSet.url(filename=recmm_lang.coverfile)
    # 按音乐流派推荐
    recmm_style_musics = Music.query.filter(Music.style_id == music.style_id,
                                            Music.id != music.id).all()[0:6]
    for recmm_style in recmm_style_musics:
        recmm_style.cover_url = musicCoversSet.url(filename=recmm_style.coverfile)
    # 按音乐主题推荐
    recmm_theme_musics = Music.query.filter(Music.theme_id == music.theme_id,
                                            Music.id != music.id).all()[0:6]
    for recmm_theme in recmm_theme_musics:
        recmm_theme.cover_url = musicCoversSet.url(filename=recmm_theme.coverfile)
    # 按音乐心情推荐
    recmm_emotion_musics = Music.query.filter(Music.emotion_id == music.emotion_id,
                                              Music.id != music.id).all()[0:6]
    for recmm_emotion in recmm_emotion_musics:
        recmm_emotion.cover_url = musicCoversSet.url(filename=recmm_emotion.coverfile)
    # 按音乐场景推荐
    recmm_scene_musics = Music.query.filter(Music.scene_id == music.scene_id,
                                            Music.id != music.id).all()[0:6]
    for recmm_scene in recmm_scene_musics:
        recmm_scene.cover_url = musicCoversSet.url(filename=recmm_scene.coverfile)
    # 按音乐歌手推荐
    recmm_singer_musics = Music.query.filter(Music.singer == music.singer,
                                             Music.id != music.id).all()[0:6]
    for recmm_singer in recmm_singer_musics:
        recmm_singer.cover_url = musicCoversSet.url(filename=recmm_singer.coverfile)
    # 获取评论列表,以及用户头像
    music_comments = MusicComment.query.filter_by(music_id=music.id). \
        order_by(MusicComment.addtime.desc()).all()
    for cmmt in music_comments:
        cmmt.userface_url = photosSet.url(filename=cmmt.user.name + '/' + cmmt.user.face)
    return render_template('home/music_listen.html', form=MusicCommentForm(),
                           music=music, recmm_lang_musics=recmm_lang_musics,
                           recmm_style_musics=recmm_style_musics,
                           recmm_theme_musics=recmm_theme_musics,
                           recmm_emotion_musics=recmm_emotion_musics,
                           recmm_scene_musics=recmm_scene_musics,
                           recmm_singer_musics=recmm_singer_musics,
                           music_comments=music_comments)


@home.route('/music/favor/', methods=["GET"])
def music_favor():
    mid = request.args.get('mid')
    uid = request.args.get('uid')
    act = request.args.get('act')
    if act == 'check':
        existed = MusicFavor.query.filter_by(user_id=int(uid), music_id=int(mid)).first()
        if existed:
            res = {'isfavor': 1}
        else:
            res = {'isfavor': 0}
        return jsonify(res)
    if act == 'add':
        favor = MusicFavor(user_id=int(uid), music_id=int(mid))
        db.session.add(favor)
        music = Music.query.get_or_404(int(mid))
        music.favornum += 1
        db.session.add(music)
        db.session.commit()
        return jsonify(isfavor=1)
    if act == 'del' or act == 'cancel':
        favor = MusicFavor.query.filter_by(user_id=int(uid), music_id=int(mid)).first()
        music = Music.query.get_or_404(int(mid))
        music.favornum -= 1
        db.session.add(music)
        db.session.delete(favor)
        db.session.commit()
        if act == 'del':
            return jsonify(isfavor=0)
        if act == 'cancel':
            return redirect(url_for("home.user_music_favor", page=1))


@home.route('/music/comment/', methods=["GET", "POST"])
def music_comment():
    action = request.args.get('action')
    if action == 'config':
        return jsonify(CONFIG={})
    form = MusicCommentForm()
    if request.method == "POST":
        user_id = int(request.args.get('uid'))
        music_id = int(request.args.get('mid'))
        content = request.form['comment_content']
        if form.validate():
            comment = MusicComment(user_id=user_id, music_id=music_id, comment=content)
            db.session.add(comment)
            music = Music.query.get_or_404(music_id)
            music.commtnum += 1
            db.session.add(music)
            db.session.commit()
            return redirect(url_for("home.music_listen", id=music_id))
        else:
            flash(message=form.comment_content.errors[0], category='error')
            return redirect(url_for("home.music_listen", id=music_id))
    return 'ok'


@home.route('/music/favors/<int:page>', methods=["GET"])
@user_login_req
def user_music_favor(page):
    musics = Music.query.join(MusicFavor). \
        filter(MusicFavor.user_id == int(session.get('user_id'))). \
        paginate(page=page, per_page=5)
    for item in musics.items:
        item.coverimgurl = musicCoversSet.url(filename=item.coverfile)
    return render_template("home/user_music_favor.html", musics=musics)


@home.route('/movie/')
def movie_index():
    # 获取形象首页的推荐电影
    recmd_movies = Movie.query.filter(Movie.recommed == 2).order_by(Movie.clicknum.desc()).all()[0:4]
    for ritem in recmd_movies:
        ritem.cover_url = movieCoversSet.url(filename=ritem.cover)
        ritem.video_url = movieVideosSet.url(filename=ritem.videofile)
    # 获取最新发布的电影
    newest_movies = Movie.query.order_by(Movie.addtime.desc()).all()[0:4]
    for nitem in newest_movies:
        nitem.cover_url = movieCoversSet.url(filename=nitem.cover)
        nitem.video_url = movieVideosSet.url(filename=nitem.videofile)
    # 获取最火的音乐
    hotest_movies = Movie.query.order_by(Movie.clicknum.desc()).all()[0:8]
    for hitem in hotest_movies:
        hitem.cover_url = movieCoversSet.url(filename=hitem.cover)
        hitem.video_url = movieVideosSet.url(filename=hitem.videofile)
    return render_template("home/movie_index.html", recmd_movies=recmd_movies,
                           newest_movies=newest_movies, hotest_movies=hotest_movies)


@home.route('/movie/list/<int:page>')
def movie_list(page):
    movie_tags = MovieTag.query.all()
    area = request.args.get('area', '0')
    tag = int(request.args.get('tag', '0'))
    star = int(request.args.get('star', '0'))
    p = {'area': area, 'tag': tag, 'star': star}
    movies = Movie.query
    if area != '0':
        movies = movies.filter_by(area=area)
    if tag != 0:
        movies = movies.filter_by(tag_id=tag)
    if star != 0:
        movies = movies.filter_by(starlevel=star)
    movies = movies.order_by(Movie.addtime.desc()).paginate(page=page, per_page=8)
    for item in movies.items:
        item.cover_url = movieCoversSet.url(filename=item.cover)
    return render_template("home/movie_list.html", movies=movies, movie_tags=movie_tags, p=p)


@home.route('/movie/play/<int:id>')
def movie_play(id):
    movie = Movie.query.get_or_404(id)
    movie.clicknum += 1
    db.session.add(movie)
    db.session.commit()
    movie.cover_url = movieCoversSet.url(filename=movie.cover)
    movie.video_url = movieVideosSet.url(filename=movie.videofile)
    # 获取推荐列表
    recmm_area_movies = Movie.query.filter(Movie.area == movie.area, Movie.id != movie.id). \
                            order_by(Movie.clicknum.desc()).all()[0:6]
    for ram in recmm_area_movies:
        ram.cover_url = movieCoversSet.url(filename=ram.cover)
    recmm_tag_movies = Movie.query.filter(Movie.tag_id == movie.tag_id, Movie.id != movie.id). \
                           order_by(Movie.clicknum.desc()).all()[0:6]
    for rtm in recmm_tag_movies:
        rtm.cover_url = movieCoversSet.url(filename=rtm.cover)
    # 获取评论列表
    movie_comments = MovieComment.query.filter_by(movie_id=movie.id). \
        order_by(MovieComment.addtime.desc()).all()
    for mcmmt in movie_comments:
        mcmmt.userface_url = photosSet.url(filename=mcmmt.user.name + '/' + mcmmt.user.face)
    return render_template("home/movie_play.html", movie=movie,
                           recmm_area_movies=recmm_area_movies,
                           recmm_tag_movies=recmm_tag_movies, movie_comments=movie_comments)


@home.route('/movie/favor/', methods=["GET"])
def movie_favor():
    mid = request.args.get('mid')
    uid = request.args.get('uid')
    act = request.args.get('act')
    if act == 'check':
        existed = MovieFavor.query.filter_by(user_id=int(uid), movie_id=int(mid)).first()
        if existed:
            res = {'isfavor': 1}
        else:
            res = {'isfavor': 0}
        return jsonify(res)
    if act == 'add':
        favor = MovieFavor(user_id=int(uid), movie_id=int(mid))
        db.session.add(favor)
        movie = Movie.query.get_or_404(int(mid))
        movie.favornum += 1
        db.session.add(movie)
        db.session.commit()
        return jsonify(isfavor=1)
    if act == 'del' or act == 'cancel':
        favor = MovieFavor.query.filter_by(user_id=int(uid), movie_id=int(mid)).first()
        movie = Movie.query.get_or_404(int(mid))
        movie.favornum -= 1
        db.session.add(movie)
        db.session.delete(favor)
        db.session.commit()
        if act == 'del':
            return jsonify(isfavor=0)
        if act == 'cancel':
            return redirect(url_for("home.user_movie_favor", page=1))


@home.route('/movie/comment/', methods=["GET"])
def movie_comment():
    mid = request.args.get('mid')
    uid = request.args.get('uid')
    content = request.args.get('content')
    comment = MovieComment(user_id=int(uid), movie_id=int(mid), comment=content)
    movie = Movie.query.get_or_404(int(mid))
    movie.commtnum += 1
    db.session.add(comment)
    db.session.add(movie)
    db.session.commit()
    # 实现评论列表的局部刷新
    user = comment.user
    userface_url = photosSet.url(filename=user.name + '/' + user.face)
    # 构造一条评论记录
    cmmLi = """<li class="item cl">
                        <a>
                            <i class="avatar size-L radius">
                                <img src="%s"
                                     class="img-circle" style="border:1px solid #abcdef;
                                         width: 50px;height: 50px;">
                            </i>
                        </a>
                        <div class="comment-main">
                            <header class="comment-header">
                                <div class="comment-meta">
                                    <a class="comment-author">%s</a>
                                    评论于
                                    <time title="2016-12-07 09:12:51" datetime="2016-12-07 09:12:51">
                                        %s
                                    </time>
                                </div>
                            </header>
                            <div class="comment-body">
                                %s
                            </div>
                        </div>
                    </li>
    """ % (userface_url, user.name, comment.addtime, comment.comment)
    return jsonify(ok=1, cmmLi=cmmLi)


@home.route('/movie/favors/<int:page>', methods=["GET"])
@user_login_req
def user_movie_favor(page):
    movies = Movie.query.join(MovieFavor). \
        filter(MovieFavor.user_id == int(session.get('user_id'))). \
        paginate(page=page, per_page=5)
    for item in movies.items:
        item.cover_url = movieCoversSet.url(filename=item.cover)
    return render_template("home/user_movie_favor.html", movies=movies)
