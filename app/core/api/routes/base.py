from flask import render_template

from .. import api_bp
from ..controllers import BasicsController


@api_bp.route("/", methods=["GET"])
def index():
    return render_template("api/index.html")

@api_bp.route("/info")
def site_info():
    """
    Returns basic site information from settings.
    """
    return BasicsController.site_info()