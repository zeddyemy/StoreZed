from flask_login import current_user

from .utils.helpers.settings import get_all_general_settings
from .utils.helpers.category import get_cached_categories
from .utils.helpers.user import get_app_user_info
from .utils.helpers.nav_bar import get_cached_nav_items
from .utils.helpers.money import format_monetary_value
from .extensions import db

def app_context_Processor():
    user_id = current_user.id if current_user.is_authenticated else None
    
    current_user_info = get_app_user_info(user_id)
    general_settings = get_all_general_settings()
    
    all_categories = get_cached_categories()
    nav_items = get_cached_nav_items()
    
    
    return {
        'CURRENT_USER': current_user_info,
        'ALL_CATEGORIES': all_categories,
        'NAV_ITEMS': nav_items,
        'GENERAL_SETTINGS': general_settings,
        'SITE_INFO': {
            "site_title": general_settings.get("site_title", "My Store"),
            "site_tagline": general_settings.get("tagline", ""),
            "currency": general_settings.get("currency", "NGN"),
        },
        'format_monetary_value': format_monetary_value
        
    }