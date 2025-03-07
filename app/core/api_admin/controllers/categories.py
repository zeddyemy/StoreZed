from typing import List, Optional
from flask import request, Response
from sqlalchemy.exc import ( DataError, DatabaseError, IntegrityError )
from flask_sqlalchemy.pagination import Pagination

from config import Config
from ....extensions import db
from ....models import Category
from ....utils.helpers.category import fetch_all_categories, fetch_category, save_category
from ....utils.helpers.http_response import error_response, success_response
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.forms.web_admin.products import generate_category_field

class AdminCategoryController:
    @staticmethod
    def fetch_all_categories():
        try:
            page_num = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)
            search_term = request.args.get("search", "").strip()
            
            pagination: Pagination = fetch_all_categories(page_num=page_num, paginate=True, search_term=search_term)
            
            # Extract paginated categories and pagination info
            categories: List[Category] = pagination.items
            current_categories: List[dict] = [cat.to_dict() for cat in categories]
            extra_data = {
                "total": pagination.total,
                "categories": current_categories,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            api_response = success_response("Categories fetched successfully", 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching categories', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting categories:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response
    
    @staticmethod
    def fetch_category(identifier):
        try:
            category: Category = fetch_category(identifier)
            
            if not category:
                return error_response("Category not found", 404)
            
            extra_data = {"category": category.to_dict()}
            
            api_response = success_response("Category fetched successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching category', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting category:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response
    
    @staticmethod
    def add_new_category():
        try:
            form_data = request.form
            new_category = save_category(form_data)
            
            if not new_category:
                return error_response("Category couldn't get added", 500)
            
            # Parse 'add_select' query parameter
            add_select = request.args.get("add_select", "").lower() in {'true', '1'}
            
            extra_data = {
                "category": new_category.to_dict(),
            }
            
            if add_select:
                extra_data['select_field'] = generate_category_field(format='select')
            
            api_response = success_response("new category successfully", 200, extra_data)
        except (IntegrityError) as e:
            log_exception('Database integrity error adding category', e)
            api_response = error_response("Category already exists", 409)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred adding new category', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred adding new category:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response
    
    
    @staticmethod
    def edit_category(identifier):
        try:
            category: Category = fetch_category(identifier)
            
            if not category:
                return error_response("Category not found", 404)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred editing category', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred editing category:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response
    
    
    @staticmethod
    def delete_category(identifier):
        try:
            category: Category = fetch_category(identifier)
            
            if not category:
                return error_response("Category not found", 404)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred deleting category', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred deleting category:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response

    @staticmethod
    def fetch_category_suggestions():
        try:
            pass
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching category suggestions', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting category suggestions:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response



