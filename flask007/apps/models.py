from datetime import datetime

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

    def __repr__(self):
        return '<AlbumTag %r>' % self.name


class Album(db.Model):
    __tablename__ = 'album'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.TEXT)
    photonum = db.Column(db.Integer, default=0)
    privacy = db.Column(db.String(20), default='public')
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


class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    origname = db.Column(db.String(255), unique=True, nullable=False)  # 原图文件名
    showname = db.Column(db.String(255), unique=True, nullable=False)  # 展示图的文件名
    thumbname = db.Column(db.String(255), unique=True, nullable=False)  # 缩略图的文件名
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    addtime = db.Column(db.DATETIME, index=True, default=datetime.now)


if __name__ == "__main__":
    flag = 1
    if flag == 0:
        db.drop_all()
        db.create_all()
    if flag == 1:
        tag0 = AlbumTag(name='风景')
        tag1 = AlbumTag(name='动漫')
        tag2 = AlbumTag(name='星空')
        tag3 = AlbumTag(name='萌宠')
        tag4 = AlbumTag(name='静物')
        tag5 = AlbumTag(name='机械')
        db.session.add(tag0)
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.add(tag3)
        db.session.add(tag4)
        db.session.add(tag5)
        db.session.commit()
