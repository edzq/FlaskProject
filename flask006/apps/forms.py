from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp

from flask_uploads import IMAGES


class RegistForm(FlaskForm):
    user_name = StringField(
        label="用户名",
        validators=[DataRequired(message="用户名不能为空！"),
                    Length(min=3, max=15, message="用户名长度在3到15个字符之间！")],
        render_kw={"id": "user_name",
                   "class": "form-control",
                   "placeholder": "输入用户名",
                   }
    )
    user_pwd = PasswordField(
        label="用户密码",
        validators=[DataRequired(message="用户密码不能为空！"),
                    Length(min=3, max=5, message="用户密码长度在3到5个字符之间！")],
        render_kw={"id": "user_pwd",
                   "class": "form-control",
                   "placeholder": "输入用户密码"
                   }
    )
    user_email = StringField(
        label="用户邮箱",
        validators=[DataRequired(message="用户邮箱不能为空！"),
                    Email(message="用户邮箱格式不对！")],
        render_kw={"id": "user_email",
                   "class": "form-control",
                   "placeholder": "输入用户邮箱"
                   }
    )
    user_phone = StringField(
        label="用户手机",
        validators=[DataRequired(message="用户手机不能为空！"),
                    Regexp("1[3,4,5,8]\d{9}", message="手机号码格式不准确！")],
        render_kw={"id": "user_phone",
                   "class": "form-control",
                   "placeholder": "输入用户手机"
                   }
    )
    user_face = FileField(
        label="用户头像",
        validators=[FileRequired(message="用户头像不能为空!"),
                    FileAllowed(IMAGES, '只允许图像格式为:%s' % str(IMAGES))],
        render_kw={"id": "user_face",
                   "class": "form-control",
                   "placeholder": "输入用户头像"
                   }
    )
    user_jianjie = TextAreaField(
        label="用户简介",
        validators=[],
        render_kw={"id": "user_jianjie",
                   "class": "form-control",
                   "placeholder": "输入用户简介"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-success",
            "value": "注册"
        }
    )


class LoginForm(FlaskForm):
    user_name = StringField(
        label="用户名",
        validators=[DataRequired(message="用户名不能为空！")],
        render_kw={"id": "user_name",
                   "class": "form-control",
                   "placeholder": "输入用户名",
                   }
    )
    user_pwd = PasswordField(
        label="用户密码",
        validators=[DataRequired(message="用户密码不能为空！")],
        render_kw={"id": "user_pwd",
                   "class": "form-control",
                   "placeholder": "输入用户密码"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-success",
            "value": "登录"
        }
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="用户旧密码",
        validators=[DataRequired(message="用户旧密码不能为空！")],
        render_kw={"id": "old_pwd",
                   "class": "form-control",
                   "placeholder": "输入用户旧密码"
                   }
    )
    new_pwd = PasswordField(
        label="用户新密码",
        validators=[DataRequired(message="用户新密码不能为空！")],
        render_kw={"id": "new_pwd",
                   "class": "form-control",
                   "placeholder": "输入用户新密码"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-success",
            "value": "修改"
        }
    )


class InfoForm(FlaskForm):
    user_name = StringField(
        label="用户名",
        validators=[DataRequired(message="用户名不能为空！"),
                    Length(min=3, max=15, message="用户名长度在3到15个字符之间！")],
        render_kw={"id": "user_name",
                   "class": "form-control",
                   "placeholder": "输入用户名",
                   }
    )
    user_email = StringField(
        label="用户邮箱",
        validators=[DataRequired(message="用户邮箱不能为空！"),
                    Email(message="用户邮箱格式不对！")],
        render_kw={"id": "user_email",
                   "class": "form-control",
                   "placeholder": "输入用户邮箱"
                   }
    )
    user_phone = StringField(
        label="用户手机",
        validators=[DataRequired(message="用户手机不能为空！")],
        render_kw={"id": "user_phone",
                   "class": "form-control",
                   "placeholder": "输入用户手机"
                   }
    )
    user_face = FileField(
        label="用户头像",
        validators=[FileAllowed(IMAGES, '只允许图像格式为:%s' % str(IMAGES))],
        render_kw={"id": "user_face",
                   "class": "form-control",
                   "placeholder": "输入用户头像"
                   }
    )
    user_jianjie = TextAreaField(
        label="用户简介",
        validators=[],
        render_kw={"id": "user_jianjie",
                   "class": "form-control",
                   "placeholder": "输入用户简介"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-success",
            "value": "修改"
        }
    )
