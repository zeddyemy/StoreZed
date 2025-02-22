from decimal import Decimal
from typing import Optional

from ..extensions import db
from ..utils.date_time import DateTimeUtils
from ..enums.orders import OrderStatus

class Order(db.Model):
    """
    Model representing a customer order.
    
    Attributes:
        id: Unique identifier
        order_number: Human-readable order identifier
        total_amount: Total order amount
        status: Current order status
        shipping_address: Shipping address details
        billing_address: Billing address details (if different)
        meta_info: Additional order data
    """
    __tablename__ = "order"

    id = db.Column(db.Integer(), primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=OrderStatus.PENDING.value)
    shipping_address = db.Column(db.JSON, nullable=True)
    billing_address = db.Column(db.JSON, nullable=True)
    meta_info = db.Column(db.JSON, default=dict)
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)

    # Relationships
    user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    app_user = db.relationship('AppUser', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    payment = db.relationship('Payment', back_populates='order', uselist=False)

    def __repr__(self):
        return f'<Order {self.order_number}>'

    def update(self, commit=True, **kwargs):
        """Update order attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        """Delete order."""
        db.session.delete(self)
        if commit:
            db.session.commit()

    @property
    def currency_code(self):
        """Get currency code from user's wallet."""
        return self.app_user.wallet.currency_code


class OrderItem(db.Model):
    """
    Model representing individual items within an order.
    
    Attributes:
        id: Unique identifier
        quantity: Number of items ordered
        unit_price: Price per unit
        subtotal: Total price for this item (quantity * unit_price)
        meta_info: Additional item data (e.g., selected options)
    """
    __tablename__ = "order_item"

    id = db.Column(db.Integer(), primary_key=True)
    quantity = db.Column(db.Integer(), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    meta_info = db.Column(db.JSON, default=dict)
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)

    # Relationships
    order_id = db.Column(db.Integer(), db.ForeignKey('order.id'), nullable=False)
    order = db.relationship('Order', back_populates='items')
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product')

    def __repr__(self) -> str:
        return f'<OrderItem {self.id} - Order {self.order_id}>'