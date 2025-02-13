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


def get_all_nav_items() -> NavigationBarItem:
    """
    Gets all Navigation Item rows from database
    """
    nav_items = NavigationBarItem.query.order_by(asc('order'))
    
    return nav_items


# Create a cache with a Time-To-Live (TTL) of 5 minutes (300 seconds)
cache = TTLCache(maxsize=100, ttl=300)

@cached(cache)
def get_cached_nav_items() -> list[dict[str, str]]:
    """
    Gets cached Navigation Items
    """
    return [nav_item.to_dict() for nav_item in get_all_nav_items()]