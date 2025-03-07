from flask_jwt_extended import jwt_required

from .. import admin_api_bp
from ....utils.decorators.auth import roles_required
from ..controllers import AdminTagController

@admin_api_bp.route('/tags', methods=['GET'])
def fetch_all_tags():
    return AdminTagController.fetch_all_tags()

@admin_api_bp.route('/tags/<identifier>', methods=['GET'])
def fetch_tag(identifier):
    return AdminTagController.fetch_tag(identifier)

@admin_api_bp.route('/tags/new', methods=['POST'])
def add_new_tag():
    return AdminTagController.add_new_tag()


@admin_api_bp.route('/tags/edit/<identifier>', methods=['PUT'])
def edit_tag(identifier):
    return AdminTagController.edit_tag(identifier)


@admin_api_bp.route('/tags/edit/<identifier>', methods=['DELETE'])
def delete_tag(identifier):
    return AdminTagController.delete_tag(identifier)

@admin_api_bp.route('/tags/suggestions', methods=['GET'])
def fetch_tag_suggestions():
    return AdminTagController.fetch_tag_suggestions()

