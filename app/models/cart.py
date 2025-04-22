from decimal import Decimal
from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Query, joinedload
from sqlalchemy import event, Index, CheckConstraint

from ..extensions import db
from ..utils.date_time import DateTimeUtils
from ..enums import OrderStatus, PaymentStatus
from .user import AppUser
from .product import Product


class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)

    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    app_user = db.relationship('AppUser', backref='carts', lazy=True)
    
    def __repr__(self):
        return f"<Cart {self.id} ({self.app_user.username})>"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)
    
    
    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    def to_dict(self, include_user:bool = False, include_items: bool = False):
        """Serialize cart to dictionary with options"""
        
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "item_count": self.item_count,
            "created_at": self.created_at.strftime("%b %d, %Y - %I:%M %p"),
            "updated_at": self.updated_at.strftime("%b %d, %Y - %I:%M %p"),
        }
        
        if include_user:
            data["user"] = self.app_user.to_dict()
        
        if include_items:
            data["items"] = [item.to_dict() for item in self.items]
        return data


class CartItem(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    cart_id = db.Column(db.Integer(), db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'), nullable=False)
    variant_id = db.Column(db.Integer(), db.ForeignKey('product_variant.id'), nullable=True)
    quantity = db.Column(db.Integer(), default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Price at time of adding
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)

    # Relationships
    product = db.relationship('Product', backref='cart_items', lazy=True)
    variant = db.relationship('ProductVariant', backref='cart_items', lazy=True)

    @property
    def subtotal(self):
        return self.price * self.quantity
    
    
    @staticmethod
    def add_search_filters(query: Query, search_term: str) -> Query:
        """Add search filters to the query"""
        if search_term:
            search_term = f"%{search_term}%"
            
            query = query.outerjoin(CartItem.product)
            
            query = query.options(
                joinedload(CartItem.product)
                ).filter(
                or_(
                    CartItem.price.ilike(search_term),
                    Product.name.ilike(search_term),
                )
            )
        return query
    
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    
    def to_dict(self) -> dict:
        """Serialize order cart_item to dictionary"""
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "quantity": self.quantity,
            "subtotal": str(self.subtotal),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

