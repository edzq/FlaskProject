import os
from functools import wraps

import shutil
from flask import render_template, redirect, url_for, request, flash, session
from flask_uploads import IMAGES, UploadSet
from werkzeug.security import generate_password_hash

from apps import app, db
from apps.admin import admin_bp as admin
from apps.admin.forms import LoginForm, PwdForm, TagForm
from apps.models import Admin, ArticleTag, Article, AlbumTag, Album, User, AlbumFavor, ArticleFavor

# 创建 UploadSet 类的实例
photosSet = UploadSet(name='photos', extensions=IMAGES)


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


@admin.route('/music/tags/', methods=["GET", "POST"])
@admin_login_req
def music_tag():
    return render_template('admin/music_tag.html')


@admin.route('/music/list/', methods=["GET"])
@admin_login_req
def music_list():
    return render_template('admin/music_list.html')


@admin.route('/music/add/', methods=["GET", "POST"])
@admin_login_req
def music_add():
    return render_template('admin/music_add.html')


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
    #删除当前用户的收藏列表
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
