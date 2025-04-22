"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""
from sqlalchemy import asc
from cachetools import cached, TTLCache

from ...extensions import db
from ...models import NavigationMenu, NavMenuItem
from .loggers import console_log


def get_all_menu_items(parent_only=True) -> NavMenuItem:
    """
    Gets all Navigation Item rows from database
    """
    menu_items_query = NavMenuItem.query
    if parent_only:
        menu_items_query = menu_items_query.filter(NavMenuItem.parent_id == None)
    
    menu_items = menu_items_query.order_by(asc('order')).all()
    
    return menu_items


# Create a cache with a Time-To-Live (TTL) of 5 minutes (300 seconds)
cache = TTLCache(maxsize=100, ttl=300)

@cached(cache)
def get_cached_menu_items(parent_only=True) -> list[dict[str, str]]:
    """
    Gets cached Navigation Items
    """
    menu_items = get_all_menu_items(parent_only)
    return [
        nav_item.to_dict(include_children=True)
        for nav_item in menu_items
    ]


def get_nav_menu(identifier: int | str) -> NavigationMenu:
    nav_menu = None
    try:
        # Check if identifier is an integer
        id = int(identifier)
        
        # Fetch the Nave Menu by id
        nav_menu = NavigationMenu.query.filter_by(id=id).first()
    except ValueError:
        # If not an integer, treat it as a string
        nav_menu = NavigationMenu.query.filter_by(slug=identifier).first()
    
    return nav_menu

cache_nav_menus = TTLCache(maxsize=50, ttl=300)

@cached(cache_nav_menus)
def get_all_nav_menus() -> list[NavigationMenu]:
    """
    Returns all NavigationMenu objects ordered by creation or order.
    """
    return NavigationMenu.query.order_by(NavigationMenu.created_at.asc()).all()