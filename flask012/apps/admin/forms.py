from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


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
