from flask import request, jsonify
from flask_jwt_extended import jwt_required

from .. import admin_api_bp
from ....utils.decorators.auth import roles_required
from ..controllers import NavMenuController


@admin_api_bp.route('/nav-menus',methods=["GET", "POST"])
@roles_required("Super Admin", "Admin", "junior Admin", "moderator")
def manage_nav_menus():
    """
    manage nav menus
    """
    if request.method == "GET":
        return NavMenuController.fetch_nav_menus()
    elif request.method == "POST":
        return NavMenuController.add_nav_menu()


@admin_api_bp.route('/nav-menus/<identifier>', methods=["GET", "PUT", "DELETE"])
@roles_required("Super Admin", "Admin", "junior Admin", "moderator")
def manage_nav_menu(identifier):
    """Get, update or delete a specific nav menu."""
    if request.method == "GET":
        return NavMenuController.fetch_nav_menu(identifier)
    if request.method == "PUT":
        return NavMenuController.edit_nav_menu(identifier)
    if request.method == "DELETE":
        return NavMenuController.delete_nav_menu(identifier)


@admin_api_bp.route('/nav-menus/<identifier>/save-items', methods=['POST'])
@roles_required("Super Admin", "Admin", "junior Admin", "moderator")
def save_nav_menu_items(identifier):
    """
    Save changes made to a navigation menu.
    """
    return NavMenuController.save_nav_menu_items(identifier)
