from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_uploads import IMAGES, AUDIO


class LoginForm(FlaskForm):
    admin_name = StringField(
        label="管理员帐号",
        validators=[DataRequired(message="管理员帐号不能为空！")],
        render_kw={"id": "admin_name",
                   "class": "form-control",
                   "placeholder": "输入管理员帐号",
                   }
    )
    admin_pwd = PasswordField(
        label="管理员密码",
        validators=[DataRequired(message="管理员密码不能为空！")],
        render_kw={"id": "admin_pwd",
                   "class": "form-control",
                   "placeholder": "输入管理员密码"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
            "value": "登录"
        }
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[DataRequired(message="旧密码不能为空！")],
        render_kw={"id": "old_pwd",
                   "class": "form-control",
                   "placeholder": "输入旧密码"
                   }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[DataRequired(message="新密码不能为空！")],
        render_kw={"id": "new_pwd",
                   "class": "form-control",
                   "placeholder": "输入新密码"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-info pull-right",
            "value": "提交修改"
        }
    )


class TagForm(FlaskForm):
    tag_name = StringField(
        label="标签名称",
        validators=[DataRequired(message="标签名称不能为空！")],
        render_kw={"id": "tag_name",
                   "class": "form-control",
                   "placeholder": "输入标签名称",
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-info pull-right",
            "value": "添加标签"
        }
    )


class MusicCategoryForm(FlaskForm):
    category_name = StringField(
        label="标签类别名称",
        validators=[DataRequired(message="标签类别名称不能为空！")],
        render_kw={"id": "tag_name",
                   "class": "form-control",
                   "placeholder": "输入标签类别名称",
                   }
    )
    submit_cat = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-info pull-right",
            "value": "添加标签类别"
        }
    )


class MusicTagForm(FlaskForm):
    category = SelectField(
        label="音乐标签类别",
        validators=[DataRequired(message="音乐标签类别不能为空！")],
        coerce=str,
        choices=[('lang', '语种'), ('style', '流派'), ('theme', '主题'),
                 ('emotion', '心情'), ('scene', '场景')],
        render_kw={"id": "category_name",
                   "class": "form-control"
                   }
    )
    tag_name = StringField(
        label="音乐标签名称",
        validators=[DataRequired(message="音乐标签名称不能为空！")],
        render_kw={"id": "tag_name",
                   "class": "form-control",
                   "placeholder": "输入音乐标签名称",
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-info pull-right",
            "value": "添加音乐标签"
        }
    )


class MusicForm(FlaskForm):
    music_title = StringField(
        label="音乐标题",
        validators=[DataRequired(message="音乐标题不能为空！")],
        render_kw={"id": "music_title",
                   "class": "form-control",
                   "placeholder": "输入音乐标题",
                   }
    )
    music_singer = StringField(
        label="歌唱家",
        validators=[DataRequired(message="歌唱家不能为空！")],
        render_kw={"id": "music_singer",
                   "class": "form-control",
                   "placeholder": "输入歌唱家",
                   }
    )
    music_cover = FileField(
        label='音乐封面图像',
        validators=[FileRequired(message="请选择一张图片上传作为封面!"),
                    FileAllowed(IMAGES, '只允许图像格式为:%s' % str(IMAGES))],
        render_kw={"id": "music_cover", "class": "form-control"}
    )
    music_audio = FileField(
        label='音乐音频文件',
        validators=[FileRequired(message="请选择音频文件上传!"),
                    FileAllowed(AUDIO, '只允许文件格式为:%s' % str(AUDIO))],
        render_kw={"id": "music_audio", "class": "form-control"}
    )
    music_lrc = FileField(
        label='音乐歌词文件',
        validators=[FileRequired(message="请选择歌词文件上传!"),
                    FileAllowed(['lrc'], '只允许文件格式为: lrc')],
        render_kw={"id": "music_lrc", "class": "form-control"}
    )
    music_privacy = SelectField(
        label="音乐播放权限",
        validators=[DataRequired(message="音乐播放权限不能为空！")],
        coerce=str,
        choices=[('guest', '访客可听'), ('member', '会员可听'), ('vip', 'VIP可听')],
        render_kw={"id": "music_privacy",
                   "class": "form-control"
                   }
    )
    music_recmmed = SelectField(
        label="首页推荐",
        validators=[DataRequired(message="首页推荐不能为空！")],
        coerce=int,
        choices=[(1, '不推荐到首页'), (2, '推荐到首页')],
        render_kw={"id": "music_recmmed",
                   "class": "form-control"
                   }
    )
    music_lang = SelectField(
        label="音乐语种",
        validators=[DataRequired(message="音乐语种不能为空！")],
        coerce=int,
        # choices=[(1, '不推荐到首页'), (2, '推荐到首页')],
        render_kw={"id": "music_lang",
                   "class": "form-control"
                   }
    )
    music_style = SelectField(
        label="音乐流派",
        validators=[DataRequired(message="音乐流派不能为空！")],
        coerce=int,
        # choices=[(1, '不推荐到首页'), (2, '推荐到首页')],
        render_kw={"id": "music_style",
                   "class": "form-control"
                   }
    )
    music_theme = SelectField(
        label="音乐主题",
        validators=[DataRequired(message="音乐主题不能为空！")],
        coerce=int,
        # choices=[(1, '不推荐到首页'), (2, '推荐到首页')],
        render_kw={"id": "music_theme",
                   "class": "form-control"
                   }
    )
    music_emotion = SelectField(
        label="音乐心情",
        validators=[DataRequired(message="音乐心情不能为空！")],
        coerce=int,
        # choices=[(1, '不推荐到首页'), (2, '推荐到首页')],
        render_kw={"id": "music_emotion",
                   "class": "form-control"
                   }
    )
    music_scene = SelectField(
        label="音乐场景",
        validators=[DataRequired(message="音乐场景不能为空！")],
        coerce=int,
        # choices=[(1, '不推荐到首页'), (2, '推荐到首页')],
        render_kw={"id": "music_scene",
                   "class": "form-control"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-info pull-right",
            "value": "添加音乐"
        }
    )