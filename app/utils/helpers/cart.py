import uuid
import json
from typing import Optional
from sqlalchemy import desc
from sqlalchemy.orm import Query
from flask_sqlalchemy.pagination import Pagination # Import Pagination if needed
from flask import Flask, request, jsonify, session, make_response

from ...extensions import db
from ...models import Cart, CartItem, AppUser, Product, ProductVariant
from .basics import int_or_none, generate_slug
from .loggers import console_log, log_exception
from .user import get_current_user
from .http_response import success_response



def get_user_cart(user_id: int = None) -> Cart:
    """Get or create cart for current user"""
    cart = None
    
    if user_id:
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            return cart

        # Create new cart for user
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    
    
    return cart


def get_cart_items(
        cart_id: int,
        page_num: Optional[int] = None,
        search_term: Optional[str] = None,
        paginate: bool = True,
    ) -> Pagination | list[CartItem]:
    """Get all items in a cart"""
    if not page_num:
        page_num = request.args.get("page", 1, type=int)
    
    if not search_term:
        search_term = request.args.get("search", "").strip()
    
    # Base query with eager loading
    query: Query = CartItem.query.filter_by(cart_id=cart_id).options(
        db.selectinload(CartItem.product),
        db.selectinload(CartItem.variant)
    )
    
    # Apply search filters
    query = CartItem.add_search_filters(query, search_term)
    
    # Apply consistent ordering
    query = query.order_by(CartItem.created_at.desc())
    
    # Execute query with/without pagination
    if paginate:
        pagination: Pagination = query.paginate(page=page_num, per_page=10, error_out=False)
        return pagination
    
    
    return query.all()


def add_to_cart(product_id: int, quantity: int = 1, variant_id: int = None):
    """Add item to cart"""
    current_user = get_current_user()
    if not current_user:
        raise ValueError("User not authenticated")
    
    user_id = current_user.id
    cart = get_user_cart(user_id)
    
    if not cart:
        raise ValueError("Cart not found")
    
    
    # Check if product exists
    product: Product = Product.query.get_or_404(product_id)
    variant: ProductVariant = ProductVariant.query.get(variant_id) if variant_id else None
    
    # Get price
    price = variant.selling_price if variant else product.selling_price
    
    # Check if item already in cart
    cart_item: CartItem = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id,
        variant_id=variant_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
        cart_item.price = price
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            variant_id=variant_id,
            quantity=quantity,
            price=price
        )
        db.session.add(cart_item)

    db.session.commit()
    return cart


def sync_guest_cart():
    """Transfer guest cart items to user cart upon login"""
    cookie_cart = CookieCart()
    
    current_user = get_current_user()
    if not current_user:
        raise ValueError("User not authenticated")
    
    if cookie_cart.items:
        user_cart:Cart = get_user_cart(current_user.id)
        if not user_cart:
            user_cart = Cart(user_id=current_user.id)
            db.session.add(user_cart)
        
        for item_key, item_data in cookie_cart.items.items():
            cart_item: CartItem = CartItem.query.filter_by(cart_id=user_cart.id, product_id=item_data['product_id']).first()
            
            if cart_item:
                cart_item.quantity += item_data['quantity']
            else:
                cart_item = CartItem(
                    cart=user_cart,
                    product_id=item_data['product_id'],
                    variant_id=item_data['variant_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                db.session.add(cart_item)
        
        db.session.commit()
        
        # Clear the cookie cart
        response = cookie_cart.clear_cart()
        return response


class CookieCart:
    """Handles guest cart storage in cookies"""
    
    def __init__(self):
        self.items = self._load_cart()
    
    def _load_cart(self):
        """Load cart data from cookie"""
        cart_data = request.cookies.get('cart_items', '{}')
        try:
            return json.loads(cart_data)
        except:
            return {}
    
    def save(self):
        """Save cart data to cookie"""
        response = success_response("cart saved successfully")
        response.set_cookie('cart_items', json.dumps(self.items), max_age=60*60*24*30)  # 30 days
        return response

    def add_item(self, product_id, quantity=1, variant_id=None):
        """Add item to cart"""
        item_key = f"{product_id}-{variant_id}" if variant_id else str(product_id)
        
        if item_key in self.items:
            self.items[item_key]['quantity'] += quantity
        else:
            product = Product.query.get_or_404(product_id)
            variant = ProductVariant.query.get(variant_id) if variant_id else None
            
            self.items[item_key] = {
                'product_id': product_id,
                'variant_id': variant_id,
                'quantity': quantity,
                'price': float(variant.price if variant else product.price)
            }
        
        return self.save()

    def clear_cart():
        response = make_response('')
        response.delete_cookie('cart_items')
        return response
    
    @property
    def total(self):
        return sum(item['price'] * item['quantity'] for item in self.items.values())

    @property
    def item_count(self):
        return sum(item['quantity'] for item in self.items.values())