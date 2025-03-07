from decimal import Decimal
from flask import request, jsonify, json
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError )
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError

from ....extensions import db
from ....utils.helpers.user import get_current_user
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.helpers.http_response import error_response, success_response

from ....models import Category, Product


class CategoryController:
    
    @staticmethod
    def fetch_categories():
        pass
    
    @staticmethod
    def fetch_category(identifier):
        pass
    
    @staticmethod
    def edit_category(identifier):
        pass
    
    @staticmethod
    def delete_category(identifier):
        pass