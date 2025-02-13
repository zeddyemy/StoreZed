'''
This package contains the main routes for the Flask application.

A Flask blueprint named 'main' is created to group these routes.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
'''
from flask import Blueprint, render_template

web_front_bp: Blueprint = Blueprint('web_front', __name__)

from . import auth, home, top_up, orders