"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from flask import render_template
from flask_login import login_required

from ....utils.decorators.auth import login_required

from . import web_front_bp

@web_front_bp.route("/top-up", methods=['GET'])
@login_required
def top_up():
    return render_template('web_front/pages/top_up/top_up.html')