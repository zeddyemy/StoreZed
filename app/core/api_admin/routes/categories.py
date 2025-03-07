from flask_jwt_extended import jwt_required

from .. import admin_api_bp
from ....utils.decorators.auth import roles_required
from ..controllers import AdminCategoryController

@admin_api_bp.route('/categories', methods=['GET'])
def fetch_all_categories():
    return AdminCategoryController.fetch_all_categories()

@admin_api_bp.route('/categories/<identifier>', methods=['GET'])
def fetch_category(identifier):
    return AdminCategoryController.fetch_category(identifier)

@admin_api_bp.route('/categories/new', methods=['POST'])
def add_new_category():
    return AdminCategoryController.add_new_category()


@admin_api_bp.route('/categories/edit/<identifier>', methods=['PUT'])
def edit_category(identifier):
    return AdminCategoryController.edit_category(identifier)


@admin_api_bp.route('/categories/edit/<identifier>', methods=['DELETE'])
def delete_category(identifier):
    return AdminCategoryController.delete_category(identifier)

@admin_api_bp.route('/categories/suggestions', methods=['GET'])
def fetch_category_suggestions():
    return AdminCategoryController.fetch_category_suggestions()

