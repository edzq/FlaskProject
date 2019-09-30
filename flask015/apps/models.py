import uuid
from datetime import datetime

from werkzeug.security import generate_password_hash

from apps import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    face = db.Column(db.String(255), unique=True, nullable=False)
    jianjie = db.Column(db.TEXT)
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    albums = db.relationship('Album', backref='user')
    favors = db.relationship('AlbumFavor', backref='user')
    articles = db.relationship('Article', backref='user')
    articlefavors = db.relationship('ArticleFavor', backref='user')
    articlecomments = db.relationship('ArticleComment', backref='user')
    musicfavors = db.relationship('MusicFavor', backref='user')
    musiccomments = db.relationship('MusicComment', backref='user')
    moviefavors = db.relationship('MovieFavor', backref='user')
    moviecomments = db.relationship('MovieComment', backref='user')

    def __repr__(self):
        return '<User %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


class AlbumTag(db.Model):
    __tablename__ = 'album_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    albums = db.relationship('Album', backref='album_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<AlbumTag %r>' % self.name


class Album(db.Model):
    __tablename__ = 'album'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.TEXT)
    cover = db.Column(db.String(255), default='')
    photonum = db.Column(db.Integer, default=0)
    privacy = db.Column(db.String(20), default='public')
    recommed = db.Column(db.Integer, default=0)
    clicknum = db.Column(db.Integer, default=0)
    favornum = db.Column(db.Integer, default=0)
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    tag_id = db.Column(db.Integer, db.ForeignKey('album_tag.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    favors = db.relationship('AlbumFavor', backref='album')
    photos = db.relationship('Photo', backref='album')

    def __repr__(self):
        return '<Album %r>' % self.title


class AlbumFavor(db.Model):
    __tablename__ = 'album_favor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<AlbumFavor %r>' % self.id


class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    origname = db.Column(db.String(255), unique=True, nullable=False)  # 原图文件名
    showname = db.Column(db.String(255), unique=True, nullable=False)  # 展示图的文件名
    thumbname = db.Column(db.String(255), unique=True, nullable=False)  # 缩略图的文件名
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<Photo %r>' % self.origname


class ArticleTag(db.Model):
    __tablename__ = 'article_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    articles = db.relationship('Article', backref='article_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<ArticleTag %r>' % self.name


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.TEXT)
    cover = db.Column(db.String(255), default='')
    content = db.Column(db.TEXT)
    privacy = db.Column(db.String(20), default='public')
    recommed = db.Column(db.Integer, default=0)
    clicknum = db.Column(db.Integer, default=0)
    favornum = db.Column(db.Integer, default=0)
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    tag_id = db.Column(db.Integer, db.ForeignKey('article_tag.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    favors = db.relationship('ArticleFavor', backref='article')
    comments = db.relationship('ArticleComment', backref='article')

    def __repr__(self):
        return '<Article %r>' % self.title


class ArticleFavor(db.Model):
    __tablename__ = 'article_favor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<ArticleFavor %r>' % self.id


class ArticleComment(db.Model):
    __tablename__ = 'article_comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    comment = db.Column(db.TEXT)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<ArticleComment %r>' % self.id


class MusicCategory(db.Model):
    __tablename__ = 'music_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    tags = db.relationship('MusicTag', backref='music_category')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicCategory %r>' % self.name


class MusicTag(db.Model):
    __tablename__ = 'music_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('music_category.id'))
    # musics = db.relationship('Music', backref='music_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicTag %r,%r>' % (self.category_id, self.name)


# 音乐语种标签库
class MusicLangTag(db.Model):
    __tablename__ = 'music_lang_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    musics = db.relationship('Music', backref='music_lang_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicLangTag %r>' % self.name


# 音乐流派标签库
class MusicStyleTag(db.Model):
    __tablename__ = 'music_style_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    musics = db.relationship('Music', backref='music_style_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicStyleTag %r>' % self.name


# 音乐主题标签库
class MusicThemeTag(db.Model):
    __tablename__ = 'music_theme_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    musics = db.relationship('Music', backref='music_theme_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicThemeTag %r>' % self.name


# 音乐心情标签库
class MusicEmotionTag(db.Model):
    __tablename__ = 'music_emotion_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    musics = db.relationship('Music', backref='music_emotion_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicEmotionTag %r>' % self.name


# 音乐场景标签库
class MusicSceneTag(db.Model):
    __tablename__ = 'music_scene_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    musics = db.relationship('Music', backref='music_scene_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicSceneTag %r>' % self.name


class Music(db.Model):
    __tablename__ = 'music'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    singer = db.Column(db.String(255), nullable=False)
    coverfile = db.Column(db.String(255), default='')
    audiofile = db.Column(db.String(255), default='')
    lrcfile = db.Column(db.String(255), default='')
    privacy = db.Column(db.String(20), default='guest')
    recommed = db.Column(db.Integer, default=0)
    clicknum = db.Column(db.Integer, default=0)
    favornum = db.Column(db.Integer, default=0)
    commtnum = db.Column(db.Integer, default=0)
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    lang_id = db.Column(db.Integer, db.ForeignKey('music_lang_tag.id'))  # 音乐语种
    style_id = db.Column(db.Integer, db.ForeignKey('music_style_tag.id'))  # 音乐流派
    theme_id = db.Column(db.Integer, db.ForeignKey('music_theme_tag.id'))  # 音乐主题
    emotion_id = db.Column(db.Integer, db.ForeignKey('music_emotion_tag.id'))  # 音乐心情
    scene_id = db.Column(db.Integer, db.ForeignKey('music_scene_tag.id'))  # 音乐场景
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    favors = db.relationship('MusicFavor', backref='music')
    comments = db.relationship('MusicComment', backref='music')

    def __repr__(self):
        return '<Music %r>' % self.title


class MusicFavor(db.Model):
    __tablename__ = 'music_favor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'))
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicFavor %r>' % self.id


class MusicComment(db.Model):
    __tablename__ = 'music_comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'))
    comment = db.Column(db.TEXT)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MusicComment %r>' % self.id


class MovieTag(db.Model):
    __tablename__ = 'movie_tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    movies = db.relationship('Movie', backref='movie_tag')
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MovieTag %r>' % self.name


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    cover = db.Column(db.String(255), default='')
    videofile = db.Column(db.String(255), default='')
    privacy = db.Column(db.String(20), default='guest')
    area = db.Column(db.String(20))
    length = db.Column(db.Integer, default=0)
    starlevel = db.Column(db.SmallInteger, default=0)
    recommed = db.Column(db.Integer, default=0)
    clicknum = db.Column(db.Integer, default=0)
    favornum = db.Column(db.Integer, default=0)
    commtnum = db.Column(db.Integer, default=0)
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    tag_id = db.Column(db.Integer, db.ForeignKey('movie_tag.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    favors = db.relationship('MovieFavor', backref='movie')
    comments = db.relationship('MovieComment', backref='movie')

    def __repr__(self):
        return '<Movie %r>' % self.title


class MovieFavor(db.Model):
    __tablename__ = 'movie_favor'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MovieFavor %r>' % self.id


class MovieComment(db.Model):
    __tablename__ = 'movie_comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    comment = db.Column(db.TEXT)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)

    def __repr__(self):
        return '<MovieComment %r>' % self.id


# 管理员权限
class AdminAuth(db.Model):
    __tablename__ = "admin_auth"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<AdminAuth %r>" % self.name


# 管理员角色
class AdminRole(db.Model):
    __tablename__ = "admin_role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    auths = db.Column(db.String(600))
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)
    admins = db.relationship("Admin", backref='admin_role')  # 每个角色会有多个管理员

    def __repr__(self):
        return "<AdminRole %r>" % self.name


# 管理员
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    pwd = db.Column(db.String(255), unique=True, nullable=False)
    is_super = db.Column(db.SmallInteger)  # 是否是超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('admin_role.id'))  # 管理员所属的角色
    uuid = db.Column(db.String(255), unique=True, nullable=False)
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)
    musics = db.relationship('Music', backref='admin')
    movies = db.relationship('Movie', backref='admin')
    loginlogs = db.relationship('AdminLoginlog', backref='admin')
    operatelogs = db.relationship('AdminOperatelog', backref='admin')

    def __repr__(self):
        return '<Admin %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 管理员登陆日志
class AdminLoginlog(db.Model):
    __tablename__ = "admin_loginlog"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 指明某条登录日志记录是属于哪个管理员的
    ip = db.Column(db.String(100))  # 登录IP地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 登陆时间

    def __repr__(self):
        return "<AdminLoginlog %r>" % self.id


# 管理员操作日志
class AdminOperatelog(db.Model):
    __tablename__ = "admin_operatelog"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 指明某条操作日志记录是属于哪个管理员的
    ip = db.Column(db.String(100))  # 操作IP地址
    operations = db.Column(db.String(600))  # 操作行为描述
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 操作时间

    def __repr__(self):
        return "<AdminOperatelog %r>" % self.id


if __name__ == "__main__":
    flag = 3
    if flag == 0:
        db.drop_all()
        db.create_all()
    if flag == 1:
        tag0 = AlbumTag(name='风景')
        tag1 = AlbumTag(name='动漫')
        tag2 = AlbumTag(name='星空')
        tag3 = AlbumTag(name='萌宠')
        tag4 = AlbumTag(name='静物')
        tag5 = AlbumTag(name='汽车')
        tag6 = AlbumTag(name='海洋')
        tag7 = AlbumTag(name='美女')
        tag8 = AlbumTag(name='城市')
        tag9 = AlbumTag(name='飞鸟')
        tag10 = AlbumTag(name='花卉')
        tag11 = AlbumTag(name='昆虫')
        tag12 = AlbumTag(name='美食')
        db.session.add(tag0)
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.add(tag3)
        db.session.add(tag4)
        db.session.add(tag5)
        db.session.add(tag6)
        db.session.add(tag7)
        db.session.add(tag8)
        db.session.add(tag9)
        db.session.add(tag10)
        db.session.add(tag11)
        db.session.add(tag12)
        db.session.commit()
    if flag == 2:
        tag1 = ArticleTag(name='新闻')
        tag2 = ArticleTag(name='娱乐')
        tag3 = ArticleTag(name='体育')
        tag4 = ArticleTag(name='财经')
        tag5 = ArticleTag(name='科技')
        tag6 = ArticleTag(name='游戏')
        tag7 = ArticleTag(name='汽车')
        tag8 = ArticleTag(name='教育')
        tag9 = ArticleTag(name='房产')
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.add(tag3)
        db.session.add(tag4)
        db.session.add(tag5)
        db.session.add(tag6)
        db.session.add(tag7)
        db.session.add(tag8)
        db.session.add(tag9)
        db.session.commit()
    if flag == 3:
        role = AdminRole(name='超级管理员', auths='1')
        db.session.add(role)
        db.session.commit()
        admin = Admin(name='super', pwd=generate_password_hash('123'),
                      is_super=1, role_id=role.id, uuid=str(uuid.uuid4().hex)[0:10])
        db.session.add(admin)
        db.session.commit()
