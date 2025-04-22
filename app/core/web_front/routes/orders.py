"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""

from flask import render_template
from flask_login import login_required

from ....utils.decorators.auth import login_required

from .. import web_front_bp

@web_front_bp.route("/orders", methods=['GET'])
@login_required
def orders():
    return render_template('web_front/pages/orders/orders.html')