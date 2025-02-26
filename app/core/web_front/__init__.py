'''
This package contains the web_front routes for the Flask application.

A Flask blueprint named 'web_front' is created to group these routes.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
'''
from flask import Blueprint, render_template

web_front_bp: Blueprint = Blueprint('web_front', __name__)

from .routes import auth, home, top_up, orders, payments