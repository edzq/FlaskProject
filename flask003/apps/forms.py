from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange


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
    user_edge = IntegerField(
        label="用户年龄",
        validators=[DataRequired(message="用户年龄不能为空！"),
                    NumberRange(min=18, max=70, message="用户年龄在18到70之间！")],
        render_kw={"id": "user_edge",
                   "class": "form-control",
                   "placeholder": "输入用户年龄"
                   }
    )
    user_birthday = StringField(
        label="用户生日",
        validators=[DataRequired(message="用户生日不能为空！")],
        render_kw={"id": "user_birthday",
                   "class": "form-control",
                   "placeholder": "输入用户生日"
                   }
    )
    user_face = FileField(
        label="用户头像",
        validators=[DataRequired(message="用户头像不能为空！")],
        render_kw={"id": "user_face",
                   "class": "form-control",
                   "placeholder": "输入用户头像"
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
    user_edge = IntegerField(
        label="用户年龄",
        validators=[DataRequired(message="用户年龄不能为空！"),
                    NumberRange(min=18, max=70, message="用户年龄在18到70之间！")],
        render_kw={"id": "user_edge",
                   "class": "form-control",
                   "placeholder": "输入用户年龄"
                   }
    )
    user_birthday = StringField(
        label="用户生日",
        validators=[DataRequired(message="用户生日不能为空！")],
        render_kw={"id": "user_birthday",
                   "class": "form-control",
                   "placeholder": "输入用户生日"
                   }
    )
    user_face = FileField(
        label="用户头像",
        validators=[],
        render_kw={"id": "user_face",
                   "class": "form-control",
                   "placeholder": "输入用户头像"
                   }
    )
    submit = SubmitField(
        label="提交表单",
        render_kw={
            "class": "btn btn-success",
            "value": "修改"
        }
    )
