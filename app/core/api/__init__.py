"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from flask import Blueprint

api_bp: Blueprint = Blueprint('api', __name__, url_prefix='/api')

from .routes import base, auth, categories, payments, products, settings, tags, cart