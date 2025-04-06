from flask_login import current_user

from .utils.helpers.loggers import console_log
from .utils.helpers.settings import get_all_general_settings
from .utils.helpers.category import get_cached_categories
from .utils.helpers.user import get_app_user_info
from .utils.helpers.nav_menu import get_cached_menu_items, get_all_nav_menus
from .utils.helpers.money import format_monetary_value
from .extensions import db

def app_context_Processor():
    user_id = current_user.id if current_user.is_authenticated else None
    
    current_user_info = get_app_user_info(user_id)
    general_settings = get_all_general_settings()
    
    nav_menus = get_all_nav_menus()  # NavigationMenu objects
    
    # For backward compatibility, you extract a default menu:
    default_menu = nav_menus[0].to_dict(include_items=True, items_children=True) if nav_menus else {}
    
    return {
        'CURRENT_USER': current_user_info,
        'GENERAL_SETTINGS': general_settings,
        'SITE_INFO': {
            "site_title": general_settings.get("site_title", "My Store"),
            "site_tagline": general_settings.get("tagline", ""),
            "currency": general_settings.get("currency", "NGN"),
        },
        'NAV_MENUS': nav_menus, # unified navigation menus
        'MENU_ITEMS': default_menu.get("items") if default_menu else [],
        'format_monetary_value': format_monetary_value
        
    }