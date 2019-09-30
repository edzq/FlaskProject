import os

from flask import Flask

from apps.utils import create_folder

app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = 'who i am ? do you know?'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

APPS_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(APPS_DIR, 'static')

app.config["DATABASE"] = os.path.join(APPS_DIR, 'database.db')

app.config["UPLOADS_RELATIVE"] = 'uploads'
app.config["UPLOADS_FOLDER"] = os.path.join(STATIC_DIR, app.config["UPLOADS_RELATIVE"])

create_folder(app.config["UPLOADS_FOLDER"])

import apps.views
