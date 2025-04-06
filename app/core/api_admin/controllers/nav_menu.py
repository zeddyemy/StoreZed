from typing import List, Optional
from flask import request, Response, url_for
from sqlalchemy.exc import ( DataError, DatabaseError, IntegrityError )
from flask_sqlalchemy.pagination import Pagination

from config import Config
from ....extensions import db
from ....models import NavigationMenu, NavMenuItem, Category, Tag
from ....utils.helpers.pages import get_predefined_pages
from ....utils.helpers.nav_menu import get_nav_menu
from ....utils.helpers.category import fetch_all_categories, fetch_category, save_category
from ....utils.helpers.http_response import error_response, success_response
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.helpers.basics import generate_slug
from ....utils.forms.web_admin.products import generate_category_field

class NavMenuController:
    @staticmethod
    def fetch_nav_menus():
        """Fetch all nav menus with optional pagination."""
        try:
            page_num = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 10, type=int)
            search_term = request.args.get("search", "").strip()
            
            nav_menus = NavigationMenu.query.order_by(NavigationMenu.created_at.asc()).all()
            
            console_log("nav_menus", nav_menus)
            
            extra_data = {
                "nav_menus": [nav_menu.to_dict() for nav_menu in nav_menus],
            }
            
            api_response = success_response("Nav menus fetched successfully", 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching nav menus', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting nav menus:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response
    
    @staticmethod
    def fetch_nav_menu(identifier):
        """Fetch a single nav menu by ID or slug."""
        try:
            # Retrieve the navigation menu based on the provided identifier.
            nav_menu: NavigationMenu = get_nav_menu(identifier)
            if not nav_menu:
                return error_response("Navigation menu not found", 404)
            
            
            extra_data = {"nav_menu": nav_menu.to_dict()}
            
            api_response = success_response("Navigation menu fetched successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            log_exception('Database error occurred fetching nav menu', e)
            api_response = error_response('Database Error.', 500)
        except Exception as e:
            log_exception("An exception occurred getting nav menu:", e)
            api_response = error_response("An unexpected error occurred.", 500)
        
        return api_response
    
    @staticmethod
    def add_nav_menu():
        """Create a new Nav menu."""
        # TODO: Implement logic to add nav menu
        return success_response("Implementation still in progress", 200)
    
    
    @staticmethod
    def edit_nav_menu(identifier):
        # TODO: Implement logic to edit nav menu
        return success_response("Implementation still in progress", 200)
    
    
    @staticmethod
    def delete_nav_menu(identifier):
        # TODO: Implement logic to delete nav menu
        return success_response("Implementation still in progress", 200)


    @staticmethod
    def save_nav_menu_items(identifier):
        try:
            nav_menu = get_nav_menu(identifier)
            if not nav_menu:
                return error_response("Navigation menu not found", 404)
            
            data = request.get_json()
            if not data or 'items' not in data:
                return error_response("No menu items provided", 400)
            
            console_log("data", data)
            
            # First pass: Create all items without parent relationships
            item_map: dict[str, NavMenuItem] = {}  # Map ref_ids to new DB items
            
            with db.session.begin_nested():  # Use savepoint
                # Clear existing items (simple approach)
                for item in list(nav_menu.items):
                    db.session.delete(item)
                db.session.flush()
                
                # First create all items (without parents)
                for item_data in data['items']:
                    item_key = item_data.get('key')
                    parent_key = item_data.get('parent_key', None)  # Reference to parent's key
                    ref_id = int(item_data.get('ref_id'))
                    
                    name = item_data.get('name').strip()
                    label = item_data.get('label').strip()
                    item_type = item_data.get('type')
                    order = item_data.get('order')
                    provided_url = item_data.get('url')
                    
                    # If URL is not provided, calculate it based on the item type
                    if not provided_url:
                        if item_type == "category":
                            category: Category = Category.query.get(ref_id)
                            if category:
                                # Build URL using the category slug
                                provided_url = url_for('web_front.category_products', identifier=category.slug)
                        elif item_type == "page":
                            pages = get_predefined_pages()
                            page = next((p for p in pages if p["id"] == ref_id), None)
                            if page:
                                provided_url = url_for(page["endpoint"])
                        elif item_type == "tag":
                            tag: Tag = Tag.query.get(ref_id)
                            if tag:
                                provided_url = url_for('web_front.tag_products', identifier=tag.slug)
                        else:
                            provided_url = ""
                    
                    new_item = NavMenuItem.create(
                        name=name,
                        label=label,
                        url=provided_url,
                        order=order,
                        is_active=True,
                        item_type=item_type,
                        ref_id=ref_id,
                        menu_id=nav_menu.id,
                        commit=False,
                    )
                    db.session.add(new_item)
                    item_map[item_key] = new_item
                
                # Flush to get IDs
                db.session.flush()
                
                # Second pass: Set up parent relationships
                for item_data in data['items']:
                    item_key = item_data.get('key')
                    parent_key = item_data.get('parent_key', None)  # Reference to parent's key
                    
                    if parent_key:
                        current_item = item_map.get(item_key)
                        parent_item = item_map.get(parent_key)
                        if current_item and parent_item:
                            current_item.parent_id = parent_item.id
            
                db.session.commit()
                
            return success_response("Navigation menu saved successfully", 200)
        except Exception as e:
            db.session.rollback()
            log_exception(f"Error saving navigation menu '{identifier}': {str(e)}", e)
            return error_response("Error saving navigation menu", 500)


