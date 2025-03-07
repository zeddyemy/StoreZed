from flask_jwt_extended import jwt_required
from flask import request

from .. import admin_api_bp
from ....utils.decorators.auth import roles_required
from ..controllers import AdminCategoryController


@admin_api_bp.route('/categories/suggestions', methods=['GET'])
def fetch_category_suggestions():
    """Get category suggestions for autocomplete."""
    return AdminCategoryController.fetch_category_suggestions()


@admin_api_bp.route('/categories', methods=["GET", "POST"])
@roles_required("Super Admin", "Admin", "junior Admin", "moderator")
def manage_categories():
    """Get all categories or create a new one."""
    if request.method == "GET":
        return AdminCategoryController.fetch_all_categories()
    elif request.method == "POST":
        return AdminCategoryController.add_new_category()

@admin_api_bp.route('/categories/<identifier>', methods=["GET", "PUT", "DELETE"])
@roles_required("Super Admin", "Admin", "junior Admin", "moderator")
def manage_category(identifier):
    """Get, update or delete a specific category."""
    if request.method == "GET":
        return AdminCategoryController.fetch_category(identifier)
    if request.method == "PUT":
        return AdminCategoryController.edit_category(identifier)
    if request.method == "DELETE":
        return AdminCategoryController.delete_category(identifier)


