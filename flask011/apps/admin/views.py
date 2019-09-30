from flask import render_template

from apps.admin import admin_bp as admin


@admin.route('/')
def index():
    return render_template('admin/index.html')
