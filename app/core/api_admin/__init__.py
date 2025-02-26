"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from flask import Blueprint

admin_api_bp: Blueprint = Blueprint('admin_api', __name__, url_prefix='/api/admin')

from .routes import base