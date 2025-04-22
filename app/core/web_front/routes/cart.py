"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""

from flask import render_template, request, flash, redirect, abort, url_for
from flask_login import login_required

from ....utils.decorators.auth import login_required
from ....utils.helpers.loggers import console_log
from ....utils.helpers.cart import get_cart_items
from ....utils.helpers.user import get_current_user
from ....utils.helpers.cart import get_user_cart
from ....models import CartItem

from .. import web_front_bp

@web_front_bp.route("/cart", methods=['GET'])
@login_required
def view_cart():
    current_user = get_current_user()
    user_id = current_user.id if current_user else None
    cart = get_user_cart(user_id)
    
    page_num = request.args.get("page", 1, type=int)
    search_term = request.args.get("search", "").strip()
    
    pagination = get_cart_items(cart_id=cart.id, page_num=page_num, search_term=search_term)
    
    return render_template('web_front/pages/cart/cart.html', cart=cart, pagination=pagination, search_term=search_term)