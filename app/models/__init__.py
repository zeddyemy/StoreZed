"""
This package contains the database models for the Flask application.

It includes models for User, Product, Category, Role, etc. Each model corresponds to a table in the database.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from flask import Flask
from sqlalchemy.orm import aliased

from .media import Media
from .user import AppUser, Profile, Address, TempUser
from .role import Role, UserRole,  user_roles
from .wallet import Wallet
from .category import Category
from .product import Product, Tag, product_category, product_tag, productVariations
from .order import Order, OrderItem
from .payment import Payment, Transaction
from .subscription import Subscription, SubscriptionPlan
from .nav import NavigationBarItem, create_nav_items
from .settings import GeneralSetting, PaymentMethodSettings
from .defaults import create_default_super_admin, create_roles, initialize_settings, initialize_payment_method_settings


def create_db_defaults(app: Flask) -> None:
    with app.app_context():
        create_roles()
        create_default_super_admin()
        create_nav_items(True)
        initialize_settings()
        initialize_payment_method_settings()