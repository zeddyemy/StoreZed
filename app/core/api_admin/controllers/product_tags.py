from typing import List, Optional
from flask import request, Response
from sqlalchemy.exc import ( DataError, DatabaseError )

from config import Config
from ....extensions import db
from ....models import Tag
from ....utils.helpers.product_tags import fetch_all_tags, fetch_tag, get_tag_suggestions, save_tag, save_tags
from ....utils.helpers.http_response import error_response, success_response
from ....utils.helpers.loggers import console_log, log_exception

class AdminTagController:
    @staticmethod
    def fetch_all_tags():
        try:
            page_num = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)
            search_term = request.args.get("search", "").strip()
            
            pagination = fetch_all_tags(page_num=page_num, paginate=True, search_term=search_term)
            
            # Extract paginated tags and pagination info
            tags: List[Tag] = pagination.items
            current_tags: List[dict] = [tag.to_dict() for tag in tags]
            extra_data = {
                "total": pagination.total,
                "tags": current_tags,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            api_response = success_response("Tags fetched successfully", 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching tags', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting tags:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response


    @staticmethod
    def fetch_tag(identifier):
        try:
            tag: Tag = fetch_tag(identifier)
            
            if not tag:
                return error_response("Tag not found", 404)
            
            extra_data = {"tag": tag.to_dict()}
            
            api_response = success_response("Tag fetched successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching tags', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting tags:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response


    @staticmethod
    def add_new_tag():
        try:
            pass
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching tags', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting tags:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response


    @staticmethod
    def edit_tag(identifier):
        try:
            pass
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching tags', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting tags:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response


    @staticmethod
    def delete_tag(identifier):
        try:
            pass
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching tags', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting tags:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response


    @staticmethod
    def fetch_tag_suggestions():
        try:
            term = request.args.get("term", "").strip()
            
            if not term:
                return error_response("No query parameter provided")
            
            tags = get_tag_suggestions(term)
            
            extra_data = {
                "suggestions": tags
            }
            
            api_response = success_response("Suggestions fetched successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching tag suggestions', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting tag suggestions:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response