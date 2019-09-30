# coding: utf8
import os
import uuid
from functools import wraps

import shutil
from flask import render_template, redirect, url_for, request, flash, session
from flask_uploads import IMAGES, UploadSet, AUDIO, configure_uploads
from werkzeug.security import generate_password_hash

from apps import app, db
from apps.admin import admin_bp as admin
from apps.admin.forms import LoginForm, PwdForm, TagForm, MusicTagForm, MusicForm
from apps.models import Admin, ArticleTag, Article, AlbumTag, Album, User, AlbumFavor, ArticleFavor, \
    MusicLangTag, MusicStyleTag, MusicThemeTag, MusicEmotionTag, MusicSceneTag, Music

# 创建 UploadSet 类的实例
photosSet = UploadSet(name='photos', extensions=IMAGES)
musicCoversSet = UploadSet(name='musiccovers', extensions=IMAGES)
musicAudiosSet = UploadSet(name='musicaudios', extensions=AUDIO)
musicLrcsSet = UploadSet(name='musiclrcs', extensions=('lrc',))
# 配置FlaskUpLoad 和 app
configure_uploads(app, musicCoversSet)
configure_uploads(app, musicAudiosSet)
configure_uploads(app, musicLrcsSet)


def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_name" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@admin.route('/', methods=["GET"])
@admin_login_req
def index():
    return render_template('admin/index.html')


@admin.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        adminname = form.admin_name.data
        adminpwd = form.admin_pwd.data
        admin_x = Admin.query.filter_by(name=adminname).first()
        if not admin_x:
            flash(message='输入的管理员帐号不存在！', category='error')
            return redirect(url_for('admin.login'))
        else:
            if not admin_x.check_pwd(adminpwd):
                flash(message='输入的管理员密码不正确！', category='error')
                return redirect(url_for('admin.login'))
            else:
                session['admin_name'] = admin_x.name
                session['admin_id'] = admin_x.id
                return redirect(url_for('admin.index'))
    return render_template('admin/login.html', form=form)


@admin.route('/logout/')
@admin_login_req
def logout():
    session.pop('admin_name')
    session.pop('admin_id')
    return redirect(url_for('admin.login'))


@admin.route('/pwd/', methods=["GET", "POST"])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        old_pwd = form.old_pwd.data
        new_pwd = form.new_pwd.data
        admin = Admin.query.get_or_404(int(session.get("admin_id")))
        if admin.check_pwd(old_pwd):
            admin.pwd = generate_password_hash(new_pwd)
            db.session.add(admin)
            db.session.commit()
            session.pop("admin_name", None)
            session.pop('admin_id', None)
            flash(message="修改密码成功，请重新登录！", category='ok')
            return redirect(url_for("admin.login", admin_name=admin.name))
        else:
            flash(message="旧密码输入错误！", category='error')
            return render_template('admin/pwd.html', form=form)
    return render_template('admin/pwd.html', form=form)


@admin.route('/article/tags/<int:page>', methods=["GET", "POST"])
@admin_login_req
def article_tag(page):
    form = TagForm()
    articleNums = []
    if request.method == "GET":
        tags = ArticleTag.query.order_by(ArticleTag.addtime.desc()) \
            .paginate(page=page, per_page=5)
        for item in tags.items:
            articleNums.append(len(item.articles))
    if form.validate_on_submit():
        tag_name = form.tag_name.data
        tag = ArticleTag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = ArticleTag(name=tag_name)
            db.session.add(tag)
            db.session.commit()
            flash(message='标签名称添加成功！', category='ok')
            return redirect(url_for('admin.article_tag', page=1))
        else:
            flash(message='标签名称已经存在！', category='error')
            return redirect(url_for('admin.article_tag', page=1))
    return render_template('admin/article_tag.html',
                           form=form, tags=tags, articleNums=articleNums)


@admin.route('/article/tags/del/<int:id>', methods=["GET"])
@admin_login_req
def article_tag_del(id):
    tag = ArticleTag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash(message='标签删除成功！', category='ok')
    return redirect(url_for('admin.article_tag', page=1))


@admin.route('/article/tags/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
def article_tag_change(id):
    form = TagForm()
    old_tag = ArticleTag.query.get_or_404(id)
    if form.validate_on_submit():
        new_tag_name = form.tag_name.data
        existed = ArticleTag.query.filter_by(name=new_tag_name).first()
        if existed:
            flash(message='该标签名称已经存在！', category='error')
            return render_template("admin/article_tag_change.html", form=form, old_tag=old_tag)
        else:
            flash(message='标签名称修改成功！', category='ok')
            old_tag.name = new_tag_name
            db.session.add(old_tag)
            db.session.commit()
            return redirect(url_for('admin.article_tag', page=1))
    return render_template("admin/article_tag_change.html", form=form, old_tag=old_tag)


@admin.route('/article/list/<int:page>', methods=["GET"])
@admin_login_req
def article_list(page):
    articles = Article.query.filter(Article.privacy != 'private'). \
        order_by(Article.addtime.desc()).paginate(page=page, per_page=5)
    return render_template('admin/article_list.html', articles=articles)


@admin.route('/article/read/<int:id>', methods=["GET"])
@admin_login_req
def article_read(id):
    article = Article.query.get_or_404(id)
    return render_template("admin/article_read.html", article=article)


@admin.route('/article/del/<int:id>', methods=["GET"])
def article_del(id):
    article = Article.query.get_or_404(id)
    # 删除文章的收藏记录
    for favor in article.favors:
        db.session.delete(favor)
        db.session.commit()
        article.favornum -= 1
    # 删除文章文件夹
    folder = article.user.name + '/' + article.uuid
    article_path = app.config['UPLOADED_IMGS_DEST'] + '/' + folder
    shutil.rmtree(article_path)
    # 删除文章记录
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('admin.article_list', page=1))


@admin.route('/album/tags/<int:page>', methods=["GET", "POST"])
@admin_login_req
def album_tag(page):
    form = TagForm()
    tags = AlbumTag.query.order_by(AlbumTag.addtime.desc()). \
        paginate(page=page, per_page=5)
    counts = []
    for item in tags.items:
        counts.append(len(item.albums))
    if form.validate_on_submit():
        tag_name = form.tag_name.data
        tag = AlbumTag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = AlbumTag(name=tag_name)
            db.session.add(tag)
            db.session.commit()
            flash(message='标签名称添加成功！', category='ok')
            return redirect(url_for('admin.album_tag', page=1))
        else:
            flash(message='标签名称已经存在！', category='error')
            return redirect(url_for('admin.album_tag', page=1))
    return render_template('admin/album_tag.html', form=form, tags=tags, counts=counts)


@admin.route('/album/tags/del/<int:id>', methods=["GET"])
@admin_login_req
def album_tag_del(id):
    tag = AlbumTag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash(message='标签删除成功！', category='ok')
    return redirect(url_for('admin.album_tag', page=1))


@admin.route('/album/tags/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
def album_tag_change(id):
    form = TagForm()
    old_tag = AlbumTag.query.get_or_404(id)
    if form.validate_on_submit():
        new_tag_name = form.tag_name.data
        existed = AlbumTag.query.filter_by(name=new_tag_name).first()
        if existed:
            flash(message='该标签名称已经存在！', category='error')
            return render_template("admin/album_tag_change.html", form=form, old_tag=old_tag)
        else:
            flash(message='标签名称修改成功！', category='ok')
            old_tag.name = new_tag_name
            db.session.add(old_tag)
            db.session.commit()
            return redirect(url_for('admin.album_tag', page=1))
    return render_template("admin/album_tag_change.html", form=form, old_tag=old_tag)


@admin.route('/album/list/<int:page>', methods=["GET"])
@admin_login_req
def album_list(page):
    albums = Album.query.filter(Album.privacy != 'private'). \
        order_by(Album.addtime.desc()).paginate(page=page, per_page=5)
    photoNums = []
    for item in albums.items:
        photoNums.append(len(item.photos))
    return render_template('admin/album_list.html', albums=albums, photoNums=photoNums)


@admin.route('/album/del/<int:id>', methods=["GET"])
def album_del(id):
    album = Album.query.get_or_404(id)
    # 删除相册的收藏记录
    for favor in album.favors:
        db.session.delete(favor)
        db.session.commit()
        album.favornum -= 1
    # 删除相册文件夹
    folder = album.user.name + '/' + album.title
    album_path = app.config['UPLOADED_PHOTOS_DEST'] + '/' + folder
    shutil.rmtree(album_path)
    # 删除相册记录
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for('admin.album_list', page=1))


@admin.route('/album/browse/<int:id>', methods=["GET"])
@admin_login_req
def album_browse(id):
    album = Album.query.get_or_404(id)
    photos_url = []
    for photo in album.photos:
        photo_folder = album.user.name + '/' + album.title + '/'
        photo_url = photosSet.url(filename=photo_folder + photo.showname)
        photos_url.append(photo_url)
    return render_template("admin/album_browse.html", album=album, photos_url=photos_url)


@admin.route('/music/tags/<int:page>', methods=["GET", "POST"])
@admin_login_req
def music_tag(page):
    form = MusicTagForm()
    if form.validate_on_submit():
        category_name = form.category.data
        Taglib = ''
        if category_name == 'lang':
            Taglib = MusicLangTag
        if category_name == 'style':
            Taglib = MusicStyleTag
        if category_name == 'theme':
            Taglib = MusicThemeTag
        if category_name == 'emotion':
            Taglib = MusicEmotionTag
        if category_name == 'scene':
            Taglib = MusicSceneTag

        existed = Taglib.query.filter_by(name=form.tag_name.data).first()
        if not existed:
            tag = Taglib(name=form.tag_name.data)
            db.session.add(tag)
            db.session.commit()
            flash(message='该标签名称添加成功！', category='ok')
            return redirect(url_for('admin.music_tag', page=1, cname=category_name))
        else:
            flash(message='该标签名称已经存在！', category='error')
            return redirect(url_for('admin.music_tag', page=1, cname=category_name))
    # 获取标签表单
    cname = request.args.get('cname')
    lang_tags = MusicLangTag.query.order_by(MusicLangTag.addtime.desc()). \
        paginate(page=1, per_page=6)
    style_tags = MusicStyleTag.query.order_by(MusicStyleTag.addtime.desc()). \
        paginate(page=1, per_page=6)
    theme_tags = MusicThemeTag.query.order_by(MusicThemeTag.addtime.desc()). \
        paginate(page=1, per_page=6)
    emotion_tags = MusicEmotionTag.query.order_by(MusicEmotionTag.addtime.desc()). \
        paginate(page=1, per_page=6)
    scene_tags = MusicSceneTag.query.order_by(MusicSceneTag.addtime.desc()). \
        paginate(page=1, per_page=6)
    if cname == 'lang':
        lang_tags = MusicLangTag.query.order_by(MusicLangTag.addtime.desc()). \
            paginate(page=page, per_page=6)
    if cname == 'style':
        style_tags = MusicStyleTag.query.order_by(MusicStyleTag.addtime.desc()). \
            paginate(page=page, per_page=6)
    if cname == 'theme':
        theme_tags = MusicThemeTag.query.order_by(MusicThemeTag.addtime.desc()). \
            paginate(page=page, per_page=6)
    if cname == 'emotion':
        emotion_tags = MusicEmotionTag.query.order_by(MusicEmotionTag.addtime.desc()). \
            paginate(page=page, per_page=6)
    if cname == 'scene':
        scene_tags = MusicSceneTag.query.order_by(MusicSceneTag.addtime.desc()). \
            paginate(page=page, per_page=6)
    return render_template('admin/music_tag2.html', form=form, lang_tags=lang_tags,
                           style_tags=style_tags, theme_tags=theme_tags,
                           emotion_tags=emotion_tags, scene_tags=scene_tags)


@admin.route('/music/tags/del/<int:id>', methods=["GET"])
@admin_login_req
def music_tag_del(id):
    category_name = request.args.get('cname')
    TagLib = ''
    if category_name == 'lang':
        TagLib = MusicLangTag
    if category_name == 'style':
        TagLib = MusicStyleTag
    if category_name == 'theme':
        TagLib = MusicThemeTag
    if category_name == 'emotion':
        TagLib = MusicEmotionTag
    if category_name == 'scene':
        TagLib = MusicSceneTag
    tag = TagLib.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash(message='标签删除成功！', category='ok')
    return redirect(url_for('admin.music_tag', page=1, cname=category_name))


@admin.route('/music/tags/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
def music_tag_change(id):
    category_name = request.args.get('cname')
    TagLib = ''
    if category_name == 'lang':
        TagLib = MusicLangTag
    if category_name == 'style':
        TagLib = MusicStyleTag
    if category_name == 'theme':
        TagLib = MusicThemeTag
    if category_name == 'emotion':
        TagLib = MusicEmotionTag
    if category_name == 'scene':
        TagLib = MusicSceneTag
    old_tag = TagLib.query.get_or_404(id)
    form = MusicTagForm()
    if form.validate_on_submit():
        new_tag_name = form.tag_name.data
        existed = TagLib.query.filter_by(name=new_tag_name).first()
        if existed:
            flash(message='该标签名称已经存在！', category='error')
            return render_template("admin/music_tag_change.html", form=form,
                                   old_tag=old_tag, cname=category_name)
        else:
            flash(message='标签名称修改成功！', category='ok')
            # old_tag.category_id = form.category.data
            old_tag.name = new_tag_name
            db.session.add(old_tag)
            db.session.commit()
            return redirect(url_for('admin.music_tag', page=1, cname=category_name))
    return render_template("admin/music_tag_change.html", form=form,
                           old_tag=old_tag, cname=category_name)


# 设置音乐分类标签下拉框的choices选项
def set_music_choices(form):
    lang_tags = MusicLangTag.query.all()
    form.music_lang.choices = [(item.id, item.name) for item in lang_tags]
    style_tags = MusicStyleTag.query.all()
    form.music_style.choices = [(item.id, item.name) for item in style_tags]
    theme_tags = MusicThemeTag.query.all()
    form.music_theme.choices = [(item.id, item.name) for item in theme_tags]
    emotion_tags = MusicEmotionTag.query.all()
    form.music_emotion.choices = [(item.id, item.name) for item in emotion_tags]
    scene_tags = MusicSceneTag.query.all()
    form.music_scene.choices = [(item.id, item.name) for item in scene_tags]


# 设置音乐类实例的属性值
def set_music_attribs(form, music, chuuid=True):
    music.admin_id = session.get('admin_id')
    music.emotion_id = form.music_emotion.data
    music.lang_id = form.music_lang.data
    music.style_id = form.music_style.data
    music.theme_id = form.music_theme.data
    music.scene_id = form.music_scene.data
    music.privacy = form.music_privacy.data
    music.recommed = form.music_recmmed.data
    music.title = form.music_title.data
    music.singer = form.music_singer.data
    if chuuid:
        music.uuid = str(uuid.uuid4().hex)[0:15]


@admin.route('/music/add/', methods=["GET", "POST"])
@admin_login_req
def music_add():
    form = MusicForm()
    set_music_choices(form)
    if form.validate_on_submit():
        music = Music()
        set_music_attribs(form, music, True)
        cover_fs = request.files.get(form.music_cover.name)
        audio_fs = request.files.get(form.music_audio.name)
        lrc_fs = request.files.get(form.music_lrc.name)
        subfolder = 'musics' + '/' + music.uuid
        music.coverfile = musicCoversSet.save(cover_fs, folder=subfolder, name=cover_fs.filename)
        music.audiofile = musicAudiosSet.save(audio_fs, folder=subfolder, name=audio_fs.filename)
        music.lrcfile = musicLrcsSet.save(lrc_fs, folder=subfolder, name=lrc_fs.filename)
        db.session.add(music)
        db.session.commit()
        flash(message='音乐添加成功！', category='ok')
        return redirect(url_for('admin.music_list', page=1))
    return render_template('admin/music_add.html', form=form)


@admin.route('/music/list/<int:page>', methods=["GET"])
@admin_login_req
def music_list(page):
    musics = Music.query.order_by(Music.addtime.desc()).paginate(page=page, per_page=6)
    return render_template('admin/music_list.html', musics=musics)


@admin.route('/music/del/<int:id>', methods=["GET"])
def music_del(id):
    music = Music.query.get_or_404(id)
    # 删除音乐的收藏记录
    for favor in music.favors:
        db.session.delete(favor)
        # db.session.commit()
        music.favornum -= 1
    # 删除音乐的评论记录
    for cmmt in music.comments:
        db.session.delete(cmmt)
        # db.session.commit()
        music.commtnum -= 1
    # 删除音乐文件夹
    subfolder = 'musics' + '/' + music.uuid
    music_path = musicAudiosSet.config.destination + '/' + subfolder
    shutil.rmtree(music_path)
    # 删除相册记录
    db.session.delete(music)
    db.session.commit()
    return redirect(url_for('admin.music_list', page=1))


@admin.route('/music/listen/<int:id>', methods=["GET"])
def music_listen(id):
    music = Music.query.get_or_404(id)
    music.audio_url = musicAudiosSet.url(filename=music.audiofile)
    music.cover_url = musicCoversSet.url(filename=music.coverfile)
    music.lrc_url = musicLrcsSet.url(filename=music.lrcfile)
    lrc_path = musicLrcsSet.path(filename=music.lrcfile)
    lrcf = open(file=lrc_path, mode='r', encoding='utf8')
    music.lrc = lrcf.readlines()
    return render_template("admin/music_listen.html", music=music)


@admin.route('/music/change/<int:id>', methods=["GET", "POST"])
def music_change(id):
    form = MusicForm()
    set_music_choices(form)
    form.music_cover.validators = [form.music_cover.validators[1]]
    form.music_audio.validators = [form.music_audio.validators[1]]
    form.music_lrc.validators = [form.music_lrc.validators[1]]
    music = Music.query.get_or_404(id)
    if request.method == "GET":
        form.music_title.data = music.title
        form.music_singer.data = music.singer
        form.music_singer.data = music.singer
        form.music_privacy.data = music.privacy
        form.music_recmmed.data = music.recommed
        form.music_lang.data = music.lang_id
        form.music_style.data = music.style_id
        form.music_theme.data = music.theme_id
        form.music_emotion.data = music.emotion_id
        form.music_scene.data = music.scene_id
    if form.validate_on_submit():
        set_music_attribs(form, music, False)
        subfolder = 'musics' + '/' + music.uuid
        cover_fs = form.music_cover.data
        if cover_fs:
            cover_path = musicCoversSet.path(filename=music.coverfile)
            if os.path.isfile(cover_path):
                os.remove(cover_path)
            music.coverfile = musicCoversSet.save(cover_fs, folder=subfolder, name=cover_fs.filename)
        audio_fs = form.music_audio.data
        if audio_fs:
            audio_path = musicAudiosSet.path(filename=music.audiofile)
            if os.path.isfile(audio_path):
                os.remove(audio_path)
            music.audiofile = musicAudiosSet.save(audio_fs, folder=subfolder, name=audio_fs.filename)
        lrc_fs = form.music_lrc.data
        if lrc_fs:
            lrc_path = musicLrcsSet.path(filename=music.lrcfile)
            if os.path.isfile(lrc_path):
                os.remove(lrc_path)
            music.lrcfile = musicLrcsSet.save(lrc_fs, folder=subfolder, name=lrc_fs.filename)
        db.session.add(music)
        db.session.commit()
        flash(message='音乐修改成功！', category='ok')
        return redirect(url_for('admin.music_list', page=1))
    return render_template('admin/music_change.html', music=music, form=form)


@admin.route('/music/comments/', methods=["GET"])
@admin_login_req
def music_comments():
    return render_template('admin/music_comments.html')


@admin.route('/movie/tags/', methods=["GET", "POST"])
@admin_login_req
def movie_tag():
    return render_template('admin/movie_tag.html')


@admin.route('/movie/add/', methods=["GET", "POST"])
@admin_login_req
def movie_add():
    return render_template('admin/movie_add.html')


@admin.route('/movie/list/', methods=["GET"])
@admin_login_req
def movie_list():
    return render_template('admin/movie_list.html')


@admin.route('/movie/comments/', methods=["GET"])
@admin_login_req
def movie_comments():
    return render_template('admin/movie_comments.html')


@admin.route('/user/list/<int:page>', methods=["GET"])
@admin_login_req
def user_list(page):
    users = User.query.order_by(User.addtime.desc()) \
        .paginate(page=page, per_page=8)
    articleNums = []
    albumNums = []
    musicCmmtNums = []
    MovieCmmtNums = []

    for item in users.items:
        articleNums.append(len(item.articles))
        albumNums.append(len(item.albums))
        musicCmmtNums.append(len(item.musiccomments))
        MovieCmmtNums.append(len(item.moviecomments))
    return render_template('admin/user_list.html', users=users, articleNums=articleNums,
                           albumNums=albumNums, musicCmmtNums=musicCmmtNums, MovieCmmtNums=MovieCmmtNums)


@admin.route('/user/profile/<int:id>', methods=["GET"])
@admin_login_req
def user_profile(id):
    user = User.query.get_or_404(id)
    user.faceurl = photosSet.url(filename=user.name + '/' + user.face)
    return render_template("admin/user_profile.html", user=user)


@admin.route('/user/del/<int:id>', methods=["GET"])
@admin_login_req
def user_del(id):
    user = User.query.get_or_404(id)
    # 删除用户的上传的文件资源
    del_path = os.path.join(app.config["UPLOADS_FOLDER"], user.name)
    shutil.rmtree(del_path, ignore_errors=True)
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
    return redirect(url_for("admin.user_list", page=1))


@admin.route('/loginlog/list/', methods=["GET"])
@admin_login_req
def loginlog_list():
    return render_template('admin/loginlog_list.html')


@admin.route('/operatelog/list/', methods=["GET"])
@admin_login_req
def operatelog_list():
    return render_template('admin/operatelog_list.html')


@admin.route('/admin/auths/', methods=["GET", "POST"])
@admin_login_req
def admin_auths():
    return render_template('admin/admin_auths.html')


@admin.route('/admin/roles/', methods=["GET", "POST"])
@admin_login_req
def admin_roles():
    return render_template('admin/admin_roles.html')


@admin.route('/admin/add/', methods=["GET", "POST"])
@admin_login_req
def admin_add():
    return render_template('admin/admin_add.html')


@admin.route('/admin/list/', methods=["GET"])
@admin_login_req
def admin_list():
    return render_template('admin/admin_list.html')
