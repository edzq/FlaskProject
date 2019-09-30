from flask import Blueprint

admin_bp = Blueprint(name='admin', import_name=__name__)

import apps.admin.views
