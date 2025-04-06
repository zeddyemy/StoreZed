"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from flask import Blueprint, render_template

web_admin_bp: Blueprint = Blueprint('web_admin', __name__, url_prefix='/shop-admin')

from .routes import home, auth, nav_menu, users, products, categories, tags, settings, orders
from .error_handlers import status_codes