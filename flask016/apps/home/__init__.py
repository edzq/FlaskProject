# _*_ coding:utf-8 _*_
from flask import Blueprint

home_bp = Blueprint(name='home', import_name=__name__)

import apps.home.views
