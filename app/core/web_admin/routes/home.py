"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from flask import render_template
from flask_login import login_required

from ....utils.decorators.auth import session_roles_required

from . import web_admin_bp

@web_admin_bp.route("/", methods=['GET'])
@session_roles_required("Super Admin", "Admin")
def index():
    return render_template('web_admin/index.html')