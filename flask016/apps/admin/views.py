# _*_ coding:utf-8 _*_
import os
import uuid
from functools import wraps

import shutil
from flask import render_template, redirect, url_for, request, flash, session, abort
from werkzeug.security import generate_password_hash

from apps import app, db, musicAudiosSet, musicCoversSet, musicLrcsSet, photosSet, movieCoversSet, movieVideosSet
from apps.admin import admin_bp as admin
from apps.admin.forms import LoginForm, PwdForm, TagForm, MusicTagForm, MusicForm, MovieForm, AuthForm, RoleForm, \
    AdminForm
from apps.models import Admin, ArticleTag, Article, AlbumTag, Album, User, AlbumFavor, ArticleFavor, \
    MusicLangTag, MusicStyleTag, MusicThemeTag, MusicEmotionTag, MusicSceneTag, Music, MusicComment, MovieTag, Movie, \
    MovieComment, AdminLoginlog, AdminOperatelog, AdminAuth, AdminRole, UserMessage, TimelineItem


def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_name" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin = Admin.query.get_or_404(int(session.get("admin_id")))
        if admin.is_super == 1:
            return f(*args, **kwargs)
        authes = admin.admin_role.auths
        allowed_urls = []
        for item in authes.split(','):
            auth = AdminAuth.query.get(int(item))
            allowed_urls.append(auth.url)
        rule = request.url_rule
        print(allowed_urls)
        print(rule)
        if str(rule) not in allowed_urls:
            return redirect(url_for("admin.index"))
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
                # 记录管理员登陆日志
                loginlog = AdminLoginlog(admin_id=admin_x.id, ip=request.remote_addr)
                db.session.add(loginlog)
                db.session.commit()
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
@admin_auth
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
@admin_auth
def article_tag_del(id):
    tag = ArticleTag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash(message='标签删除成功！', category='ok')
    return redirect(url_for('admin.article_tag', page=1))


@admin.route('/article/tags/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
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
@admin_auth
def article_list(page):
    articles = Article.query.filter(Article.privacy != 'private'). \
        order_by(Article.addtime.desc()).paginate(page=page, per_page=5)
    return render_template('admin/article_list.html', articles=articles)


@admin.route('/article/read/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def article_read(id):
    article = Article.query.get_or_404(id)
    return render_template("admin/article_read.html", article=article)


@admin.route('/article/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
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
@admin_auth
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
@admin_auth
def album_tag_del(id):
    tag = AlbumTag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash(message='标签删除成功！', category='ok')
    return redirect(url_for('admin.album_tag', page=1))


@admin.route('/album/tags/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
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
@admin_auth
def album_list(page):
    albums = Album.query.filter(Album.privacy != 'private'). \
        order_by(Album.addtime.desc()).paginate(page=page, per_page=5)
    photoNums = []
    for item in albums.items:
        photoNums.append(len(item.photos))
    return render_template('admin/album_list.html', albums=albums, photoNums=photoNums)


@admin.route('/album/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
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
@admin_auth
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
@admin_auth
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
@admin_auth
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
@admin_auth
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
@admin_auth
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
        # 记录操作日志
        operateLog = AdminOperatelog(admin_id=session.get("admin_id"), ip=request.remote_addr,
                                     operations='添加一条音乐')
        db.session.add(operateLog)
        db.session.commit()
        flash(message='音乐添加成功！', category='ok')
        return redirect(url_for('admin.music_list', page=1))
    return render_template('admin/music_add.html', form=form)


@admin.route('/music/list/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
def music_list(page):
    musics = Music.query.order_by(Music.addtime.desc()).paginate(page=page, per_page=6)
    return render_template('admin/music_list.html', musics=musics)


@admin.route('/music/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
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
    # 记录操作日志
    operateLog = AdminOperatelog(admin_id=session.get("admin_id"), ip=request.remote_addr,
                                 operations='删除一条音乐记录')
    db.session.add(operateLog)
    db.session.commit()
    return redirect(url_for('admin.music_list', page=1))


@admin.route('/music/listen/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
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
@admin_login_req
@admin_auth
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


@admin.route('/music/comments/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
def music_comments(page):
    comments = MusicComment.query.order_by(MusicComment.addtime.desc()). \
        paginate(page=page, per_page=6)
    return render_template('admin/music_comments.html', comments=comments)


@admin.route('/music/comments/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def music_comments_del(id):
    comment = MusicComment.query.get_or_404(id)
    music = Music.query.get_or_404(comment.music_id)
    music.commtnum -= 1
    db.session.delete(comment)
    db.session.add(music)
    # 记录操作日志
    operateLog = AdminOperatelog(admin_id=session.get("admin_id"), ip=request.remote_addr,
                                 operations='删除一条音乐评论')
    db.session.add(operateLog)
    # 给前台用户发送一条通知消息
    message = UserMessage(admin_id=session.get("admin_id"), user_id=comment.user_id,
                          category='music_comments_del', content=comment.comment)
    db.session.add(message)
    db.session.commit()
    # 把用户受到后台消息的事件记录到时间轴上
    user = User.query.get_or_404(comment.user_id)
    timeline_item = TimelineItem(sender=session.get("admin_name"), reciever=user.name,
                                 category='user_message', content=str(message.id))
    db.session.add(timeline_item)
    db.session.commit()
    return redirect(url_for("admin.music_comments", page=1))


@admin.route('/movie/tags/<int:page>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def movie_tag(page):
    form = TagForm()
    movietags = MovieTag.query.order_by(MovieTag.addtime.desc()). \
        paginate(page=page, per_page=5)
    for item in movietags.items:
        item.moviecount = len(item.movies)
    if form.validate_on_submit():
        tag_name = form.tag_name.data
        existed = MovieTag.query.filter_by(name=tag_name).first()
        if not existed:
            tag = MovieTag(name=tag_name)
            db.session.add(tag)
            db.session.commit()
            flash(message='标签名称添加成功！', category='ok')
            return redirect(url_for("admin.movie_tag", page=1))
        else:
            flash(message='标签名称已经存在！', category='error')
            return redirect(url_for("admin.movie_tag", page=1))
    return render_template('admin/movie_tag.html', form=form, movietags=movietags)


@admin.route('/movie/tags/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def movie_tag_del(id):
    tag = MovieTag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash(message='标签删除成功！', category='ok')
    return redirect(url_for('admin.movie_tag', page=1))


@admin.route('/movie/tags/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def movie_tag_change(id):
    form = TagForm()
    old_tag = MovieTag.query.get_or_404(id)
    if form.validate_on_submit():
        new_tag_name = form.tag_name.data
        existed = MovieTag.query.filter_by(name=new_tag_name).first()
        if existed:
            flash(message='该标签名称已经存在！', category='error')
            return render_template("admin/movie_tag_change.html", form=form, old_tag=old_tag)
        else:
            flash(message='标签名称修改成功！', category='ok')
            old_tag.name = new_tag_name
            db.session.add(old_tag)
            db.session.commit()
            return redirect(url_for('admin.movie_tag', page=1))
    return render_template("admin/movie_tag_change.html", form=form, old_tag=old_tag)


# 设置电影类对象的属性
def set_movie_attrs(form, movie, isuuid=True):
    movie.title = form.movie_title.data
    movie.area = form.movie_area.data
    movie.length = form.movie_length.data
    movie.starlevel = form.movie_star.data
    movie.privacy = form.movie_privacy.data
    movie.recommed = form.movie_recmmed.data
    movie.tag_id = form.movie_tag.data
    movie.admin_id = session.get("admin_id")
    if not isuuid:
        return
    movie.uuid = str(uuid.uuid4().hex)[0:15]


@admin.route('/movie/add/', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def movie_add():
    form = MovieForm()
    movietags = MovieTag.query.all()
    form.movie_tag.choices = [(item.id, item.name) for item in movietags]
    if form.validate_on_submit():
        movie = Movie()
        set_movie_attrs(form, movie)
        cover_fs = form.movie_cover.data
        video_fs = form.movie_video.data
        subfolder = 'movies' + '/' + movie.uuid
        movie.cover = movieCoversSet.save(cover_fs, folder=subfolder, name=cover_fs.filename)
        movie.videofile = movieVideosSet.save(video_fs, folder=subfolder, name=video_fs.filename)
        db.session.add(movie)
        db.session.commit()
        return redirect(url_for("admin.movie_list", page=1))
    return render_template('admin/movie_add.html', form=form)


@admin.route('/movie/list/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
def movie_list(page):
    movies = Movie.query.order_by(Movie.addtime.desc()). \
        paginate(page=page, per_page=6)
    return render_template('admin/movie_list.html', movies=movies)


@admin.route('/movie/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def movie_del(id):
    movie = Movie.query.get_or_404(id)
    # 删除电影的收藏记录
    for favor in movie.favors:
        db.session.delete(favor)
        # db.session.commit()
        movie.favornum -= 1
    # 删除电影的评论记录
    for cmmt in movie.comments:
        db.session.delete(cmmt)
        # db.session.commit()
        movie.commtnum -= 1
    # 删除电影文件夹
    subfolder = 'movies' + '/' + movie.uuid
    movie_path = movieVideosSet.config.destination + '/' + subfolder
    shutil.rmtree(movie_path)
    # 删除相册记录
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('admin.movie_list', page=1))


@admin.route('/movie/play/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def movie_play(id):
    movie = Movie.query.get_or_404(id)
    movie.video_url = movieVideosSet.url(filename=movie.videofile)
    movie.cover_url = movieCoversSet.url(filename=movie.cover)
    return render_template("admin/movie_play.html", movie=movie)


@admin.route('/movie/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def movie_change(id):
    form = MovieForm()
    movietags = MovieTag.query.all()
    form.movie_tag.choices = [(item.id, item.name) for item in movietags]
    form.movie_cover.validators = [form.movie_cover.validators[1]]
    form.movie_video.validators = [form.movie_video.validators[1]]
    movie = Movie.query.get_or_404(id)
    if request.method == "GET":
        form.movie_title.data = movie.title
        form.movie_privacy.data = movie.privacy
        form.movie_recmmed.data = movie.recommed
        form.movie_tag.data = movie.tag_id
        form.movie_length.data = movie.length
        form.movie_star.data = movie.starlevel
        form.movie_area.data = movie.area
    if form.validate_on_submit():
        set_movie_attrs(form, movie, False)
        subfolder = 'movies' + '/' + movie.uuid
        cover_fs = form.movie_cover.data
        if cover_fs:
            cover_path = movieCoversSet.path(filename=movie.cover)
            if os.path.isfile(cover_path):
                os.remove(cover_path)
            movie.cover = musicCoversSet.save(cover_fs, folder=subfolder, name=cover_fs.filename)
        video_fs = form.movie_video.data
        if video_fs:
            video_path = movieVideosSet.path(filename=movie.videofile)
            if os.path.isfile(video_path):
                os.remove(video_path)
            movie.videofile = movieVideosSet.save(video_fs, folder=subfolder, name=video_fs.filename)
        db.session.add(movie)
        db.session.commit()
        flash(message='电影修改成功！', category='ok')
        return redirect(url_for('admin.movie_list', page=1))
    return render_template('admin/movie_change.html', movie=movie, form=form)


@admin.route('/movie/comments/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
def movie_comments(page):
    comments = MovieComment.query.order_by(MovieComment.addtime.desc()). \
        paginate(page=page, per_page=15)
    return render_template('admin/movie_comments.html', comments=comments)


@admin.route('/movie/comments/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def movie_comments_del(id):
    comment = MovieComment.query.get_or_404(id)
    movie = Movie.query.get_or_404(comment.movie_id)
    movie.commtnum -= 1
    db.session.delete(comment)
    db.session.add(movie)
    # 记录操作日志
    operateLog = AdminOperatelog(admin_id=session.get("admin_id"), ip=request.remote_addr,
                                 operations='删除一条电影评论')
    db.session.add(operateLog)
    # 给前台用户发送一条通知消息
    message = UserMessage(admin_id=session.get("admin_id"), user_id=comment.user_id,
                          category='movie_comments_del', content=comment.comment)
    db.session.add(message)
    db.session.commit()
    # 把用户受到后台消息的事件记录到时间轴上
    user = User.query.get_or_404(comment.user_id)
    timeline_item = TimelineItem(sender=session.get("admin_name"), reciever=user.name,
                                 category='user_message', content=str(message.id))
    db.session.add(timeline_item)
    db.session.commit()
    return redirect(url_for("admin.movie_comments", page=1))


@admin.route('/user/list/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
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
@admin_auth
def user_profile(id):
    user = User.query.get_or_404(id)
    user.faceurl = photosSet.url(filename=user.name + '/' + user.face)
    return render_template("admin/user_profile.html", user=user)


@admin.route('/user/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
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


@admin.route('/loginlog/list/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
def loginlog_list(page):
    loginlogs = AdminLoginlog.query.order_by(AdminLoginlog.addtime.desc()). \
        paginate(page=page, per_page=15)
    return render_template('admin/loginlog_list.html', loginlogs=loginlogs)


@admin.route('/operatelog/list/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
def operatelog_list(page):
    oplogs = AdminOperatelog.query.order_by(AdminOperatelog.addtime.desc()). \
        paginate(page=page, per_page=15)
    return render_template('admin/operatelog_list.html', oplogs=oplogs)


@admin.route('/admin/auths/<int:page>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def admin_auths(page):
    form = AuthForm()
    form.auth_name.render_kw.pop('disabled', None)
    authes = AdminAuth.query.order_by(AdminAuth.addtime.desc()).paginate(page=page, per_page=6)
    if form.validate_on_submit():
        name = form.auth_name.data
        url = form.auth_url.data
        existed = AdminAuth.query.filter_by(name=name).first()
        if not existed:
            auth = AdminAuth(name=name, url=url)
            db.session.add(auth)
            db.session.commit()
            flash(message='权限名称添加成功！', category='ok')
            return redirect(url_for('admin.admin_auths', page=1))
        else:
            flash(message='权限名称已经存在！', category='error')
            return redirect(url_for('admin.admin_auths', page=1))
    return render_template('admin/admin_auths.html', form=form, authes=authes)


@admin.route('/admin/auths/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def admin_auths_del(id):
    auth = AdminAuth.query.get_or_404(id)
    db.session.delete(auth)
    db.session.commit()
    flash(message='权限删除成功！', category='ok')
    return redirect(url_for('admin.admin_auths', page=1))


@admin.route('/admin/auths/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def admin_auths_change(id):
    form = AuthForm()
    form.auth_name.render_kw['disabled'] = 'disabled'
    form.auth_name.validators = []
    old_auth = AdminAuth.query.get_or_404(id)
    if request.method == "GET":
        form.auth_name.data = old_auth.name
        form.auth_url.data = old_auth.url
    if form.validate_on_submit():
        new_auth_url = form.auth_url.data
        existed = AdminAuth.query.filter_by(url=new_auth_url).first()
        if existed:
            flash(message='该权限地址已经被分配！', category='error')
            return render_template("admin/admin_auths_change.html", form=form)
        else:
            flash(message='权限地址修改成功！', category='ok')
            old_auth.url = form.auth_url.data
            db.session.add(old_auth)
            db.session.commit()
            return redirect(url_for('admin.admin_auths', page=1))
    return render_template("admin/admin_auths_change.html", form=form)


@admin.route('/admin/roles/<int:page>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def admin_roles(page):
    form = RoleForm()
    form.role_name.render_kw.pop('disabled', None)
    authes = AdminAuth.query.all()
    form.role_auths.choices = [(item.id, item.name) for item in authes]
    admin_roles = AdminRole.query.order_by(AdminRole.addtime.desc()).paginate(page=page, per_page=6)
    if form.validate_on_submit():
        existed = AdminRole.query.filter_by(name=form.role_name.data).first()
        if not existed:
            role = AdminRole(name=form.role_name.data,
                             auths=",".join(map(lambda v: str(v), form.role_auths.data)))
            db.session.add(role)
            db.session.commit()
            flash(message='角色名称添加成功！', category='ok')
        else:
            flash(message='角色名称已经存在！', category='error')
        return redirect(url_for('admin.admin_roles', page=1))
    return render_template('admin/admin_roles.html', form=form,
                           admin_roles=admin_roles)


@admin.route('/admin/roles/change/<int:id>', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def admin_roles_change(id):
    form = RoleForm()
    form.role_name.render_kw["disabled"] = 'disabled'
    form.role_name.validators = []
    authes = AdminAuth.query.all()
    form.role_auths.choices = [(item.id, item.name) for item in authes]
    role = AdminRole.query.get_or_404(id)
    if request.method == "GET":
        form.role_name.data = role.name
        form.role_auths.data = [int(v) for v in role.auths.split(',')]
    if form.validate_on_submit():
        role.auths = ",".join(map(lambda v: str(v), form.role_auths.data))
        db.session.add(role)
        db.session.commit()
        return redirect(url_for("admin.admin_roles", page=1))
    return render_template("admin/admin_roles_change.html", form=form)


@admin.route('/admin/roles/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def admin_roles_del(id):
    role = AdminRole.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash(message='角色删除成功！', category='ok')
    return redirect(url_for('admin.admin_roles', page=1))


@admin.route('/admin/add/', methods=["GET", "POST"])
@admin_login_req
@admin_auth
def admin_add():
    form = AdminForm()
    roles = AdminRole.query.all()
    form.admin_role.choices = [(item.id, item.name) for item in roles]
    if form.validate_on_submit():
        name = form.admin_name.data
        pwd = form.admin_pwd.data
        existed = Admin.query.filter_by(name=name).first()
        if existed:
            flash(message='管理员名称已存在！', category='error')
            return redirect(url_for("admin.admin_add"))
        else:
            pwd = generate_password_hash(pwd)
            admin = Admin(name=name, pwd=pwd, is_super=form.admin_level.data,
                          role_id=form.admin_role.data,
                          uuid=str(uuid.uuid4().hex)[0:15])
            db.session.add(admin)
            db.session.commit()
            flash(message='管理员添加成功！', category='ok')
            return redirect(url_for("admin.admin_list", page=1))
    return render_template('admin/admin_add.html', form=form)


@admin.route('/admin/list/<int:page>', methods=["GET"])
@admin_login_req
@admin_auth
def admin_list(page):
    admins = Admin.query.order_by(Admin.addtime.desc()) \
        .paginate(page=page, per_page=15)
    movieNums = []
    musicNums = []
    for item in admins.items:
        movieNums.append(len(item.movies))
        musicNums.append(len(item.musics))
    return render_template('admin/admin_list.html', admins=admins, movieNums=movieNums,
                           musicNums=musicNums)


@admin.route('/admin/del/<int:id>', methods=["GET"])
@admin_login_req
@admin_auth
def admin_del(id):
    admin = Admin.query.get_or_404(id)
    # 删除依赖记录
    for item in admin.loginlogs:
        db.session.delete(item)
    for item in admin.operatelogs:
        db.session.delete(item)
    db.session.delete(admin)
    db.session.commit()
    return redirect(url_for("admin.admin_list", page=1))
