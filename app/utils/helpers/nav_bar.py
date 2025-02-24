"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from sqlalchemy import asc
from cachetools import cached, TTLCache

from ...extensions import db
from ...models import NavigationBarItem
from .loggers import console_log


def get_all_nav_items(parent_only=True) -> NavigationBarItem:
    """
    Gets all Navigation Item rows from database
    """
    nav_items_query = NavigationBarItem.query
    if parent_only:
        nav_items_query = nav_items_query.filter(NavigationBarItem.parent_id == None)
    
    nav_items = nav_items_query.order_by(asc('order'))
    
    return nav_items


# Create a cache with a Time-To-Live (TTL) of 5 minutes (300 seconds)
cache = TTLCache(maxsize=100, ttl=300)

@cached(cache)
def get_cached_nav_items(parent_only=True) -> list[dict[str, str]]:
    """
    Gets cached Navigation Items
    """
    return [nav_item.to_dict(include_children=True) for nav_item in get_all_nav_items(parent_only)]