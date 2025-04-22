from typing import List, Optional
from flask import request, Response
from sqlalchemy.exc import ( DataError, DatabaseError, IntegrityError )
from flask_sqlalchemy.pagination import Pagination

from config import Config
from ....extensions import db
from ....models import Cart, CartItem
from ....utils.helpers.cart import add_to_cart, get_cart_items, get_user_cart
from ....utils.helpers.http_response import error_response, success_response
from ....utils.helpers.loggers import console_log, log_exception

class CartController:
    @staticmethod
    def add_to_cart():
        """Add product to cart"""
        try:
            data = request.get_json()
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            variant_id = data.get('variant_id')
            
            cart = add_to_cart(product_id, quantity, variant_id)
            
            if not cart:
                return error_response("Failed to add item to cart", 400)
            
            
            api_response = success_response("Item added to cart successfully", 200)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred adding item to cart', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred adding item to cart:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response
    
    @staticmethod
    def get_cart_items():
        """Get all items in a cart"""
        try:
            page_num = request.args.get("page", 1, type=int)
            search_term = request.args.get("search", "").strip()
            
            # Get the cart ID from the request
            cart_id = request.args.get('cart_id')
            
            if not cart_id:
                return error_response("Cart ID is required", 400)
            
            # Fetch all items in the cart
            pagination = get_cart_items(cart_id=cart_id, page_num=page_num, search_term=search_term)
            
            extra_data = {
                'total_items': pagination.total,
                'total_pages': pagination.pages,
                'current_page': pagination.page,
                'items_per_page': pagination.per_page,
                "cart_items": pagination.items
            }
            
            api_response = success_response("Items fetched successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching cart items', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred fetching cart items:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response

