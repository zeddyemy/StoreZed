"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from flask import Blueprint, render_template

api_bp: Blueprint = Blueprint('api', __name__, url_prefix='/api')

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