from datetime import timedelta
from flask import current_app
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError )
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError

from ....utils.helpers.http_response import error_response, success_response
from ....utils.helpers.settings import get_general_setting
from ....utils.helpers.loggers import log_exception, console_log

class BasicsController:
    @staticmethod
    def site_info():
        """
        Returns basic site information from settings.
        """
        try:
            info = {
                "site_name": get_general_setting("site_title", "My Store"),
                "tagline": get_general_setting("tagline", ""),
                "currency": get_general_setting("currency", "NGN"),
            }
            
            api_response = success_response("site info fetch successfully", 200, extra_data=info)
        except Exception as e:
            log_exception()
            api_response = error_response("", 500)
            
        return api_response