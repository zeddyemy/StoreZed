"""
This package contains the database models for the Flask application.

It includes models for User, Product, Category, Role, etc. Each model corresponds to a table in the database.

Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""
from flask import Flask
from sqlalchemy.orm import aliased

from .media import Media
from .user import AppUser, Profile, Address, TempUser
from .role import Role, UserRole,  user_roles
from .wallet import Wallet
from .category import Category
from .product import Product, Tag, product_category, product_tag, ProductVariant
from .order import CustomerOrder, OrderItem
from .cart import Cart, CartItem
from .payment import Payment, Transaction
from .subscription import Subscription, SubscriptionPlan
from .nav_menu import NavigationMenu, NavMenuItem
from .settings import GeneralSetting, PaymentMethodSettings
from .defaults import create_default_super_admin, create_roles, initialize_settings, initialize_payment_method_settings, initialize_nav_menu


def create_db_defaults(app: Flask) -> None:
    with app.app_context():
        create_roles()
        create_default_super_admin()
        initialize_nav_menu()
        initialize_settings()
        initialize_payment_method_settings()