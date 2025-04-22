from flask_jwt_extended import jwt_required
from flask import request

from .. import api_bp
from ....utils.decorators.auth import roles_required
from ..controllers import CartController


@api_bp.route("/cart", methods=["GET" ,"POST"])
def manage_cart():
    """Manage Cart"""
    if request.method == "GET":
        return CartController.get_cart_items()
    elif request.method == "POST":
        return CartController.add_to_cart()