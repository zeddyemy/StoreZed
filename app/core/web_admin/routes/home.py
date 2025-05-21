"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from ....extensions import db
from ....utils.decorators.auth import session_roles_required
from ....utils.helpers.stats import get_stats_for_admin
from ....utils.helpers.loggers import log_exception, console_log

from .. import web_admin_bp

@web_admin_bp.route("/dashboard", methods=['GET'], strict_slashes=False)
@session_roles_required("Super Admin", "Admin")
def dashboard():
    stats = {}
    try:
        stats = get_stats_for_admin()
        console_log("stats", stats)
    except Exception as e:
        log_exception('An exception occurred fetching admin stats', e)
        flash('An unexpected error occurred. Please try again later.', 'danger')
    
    
    return render_template('web_admin/pages/dashboard/dashboard.html', stats=stats)



@web_admin_bp.route("/", methods=['GET'])
@session_roles_required("Super Admin", "Admin")
def index():
    return redirect(url_for('web_admin.dashboard'))