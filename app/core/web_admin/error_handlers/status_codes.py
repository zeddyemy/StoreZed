from flask import render_template

from .. import web_admin_bp
from ....extensions import db


@web_admin_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("web_admin/errors/codes/404.html", error=error), 404

@web_admin_bp.app_errorhandler(401)
def unauthorized_error(error):
    return render_template("web_admin/errors/codes/401.html", error=error), 401

@web_admin_bp.app_errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("web_admin/errors/codes/500.html", error=error), 500