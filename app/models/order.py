from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Query
from sqlalchemy import event, Index, CheckConstraint

from ..extensions import db
from ..utils.date_time import DateTimeUtils
from ..enums import OrderStatus, PaymentStatus

class CustomerOrder(db.Model):
    """
    Model representing a customer order with enhanced features.
    
    Attributes:
        id: Unique identifier
        order_number: Human-readable order identifier
        total_amount: Total order amount
        status: Current order status
        shipping_address: Shipping address details
        billing_address: Billing address details (if different)
        meta_info: Additional order data
    """
    __tablename__ = "customer_order"

    id = db.Column(db.Integer(), primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, doc="Total order amount including taxes and shipping")
    status = db.Column(db.String(20), nullable=False, default=str(OrderStatus.PENDING), index=True)
    
    shipping_address = db.Column(db.JSON, nullable=True, doc="Structured shipping address information")
    billing_address = db.Column(db.JSON, nullable=True, doc="Structured billing address if different from shipping")
    meta_info = db.Column(db.JSON, default=dict, doc="Additional order metadata (e.g., source, notes)")
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)

    # Relationships
    user_id = db.Column(db.Integer(), db.ForeignKey("app_user.id"), nullable=False, index=True)
    app_user = db.relationship("AppUser", back_populates="customer_orders")
    items = db.relationship("OrderItem", back_populates="customer_order", cascade="all, delete-orphan", lazy="select")
    
    # NOTE: Current payment system assumes 1:1 relationship with customer order
    # To extend later, to have one-to-many relationship.
    # making a customer order have many payments. to address concerns like:
    # - Payment history. 
    # - Split payments.
    payment = db.relationship("Payment", back_populates="customer_order", uselist=False)
    
    __table_args__ = (
        Index('ix_order_user_status', 'user_id', 'status'),
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
    )

    def __repr__(self):
        return f"<CustomerOrder {self.order_number} ({self.status})>"
    
    def update_status(self, new_status: OrderStatus, commit=True):
        """Safely update customer order status with validation"""
        if not isinstance(new_status, OrderStatus):
            raise ValueError("Invalid customer order status")
        self.status = str(new_status)
        if commit:
            db.session.commit()
    
    def recalculate_total(self):
        """Recalculate total from order items"""
        self.total_amount = sum(
            Decimal(item.subtotal) for item in self.items
        )
        db.session.commit()

    def update(self, commit=True, **kwargs):
        """Update customer_order attributes."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            db.session.commit()

    def delete(self, commit=True):
        """Delete customer order."""
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    @property
    def payment_status(self) -> str:
        """Calculate payment status based on associated payments"""
        if not self.payment:
            return "unpaid"
        
        if self.payment.status != str(PaymentStatus.COMPLETED):
            return "unpaid"
        
        return "paid" if self.payment.amount >= self.total_amount else "partially_paid"

    @property
    def currency_code(self):
        """Get currency code from user's wallet."""
        return self.app_user.wallet.currency_code
    
    def to_dict(self, include_user:bool = False, include_items: bool = False):
        """Serialize customer_order to dictionary with options"""
        
        data = {
            "id": self.id,
            "order_number": self.order_number,
            "total_amount": self.total_amount,
            "status": self.status,
            "shipping_address": self.shipping_address,
            "billing_address": self.billing_address,
            "meta_info": self.meta_info,
            "created_at": self.created_at.strftime("%b %d, %Y - %I:%M %p"),
            "updated_at": self.updated_at.strftime("%b %d, %Y - %I:%M %p"),
            "user_id": self.user_id,
            "item_count": len(self.items),
            "payment_status": self.payment_status,
        }
        
        if include_user:
            data["user"] = self.app_user.to_dict()
        
        if include_items:
            data["items"] = [item.to_dict() for item in self.items]
        return data


class OrderItem(db.Model):
    """
    Model representing individual items within a customer order.
    
    Attributes:
        id: Unique identifier
        quantity: Number of items ordered
        unit_price: Price per unit
        subtotal: Total price for this item (quantity * unit_price)
        meta_info: Additional item data (e.g., selected options)
    """
    __tablename__ = "order_item"

    id = db.Column(db.Integer(), primary_key=True)
    
    quantity = db.Column(db.Integer(), nullable=False, default=1, doc="Quantity ordered (must be positive)")
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, doc="Price per unit at time of purchase")
    meta_info = db.Column(db.JSON, default=dict, doc="Item-specific metadata (options, discounts)")
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)
    
    # Relationships
    order_id = db.Column(db.Integer(), db.ForeignKey("customer_order.id"), nullable=False, index=True)
    customer_order = db.relationship("CustomerOrder", back_populates="items")
    product_id = db.Column(db.Integer(), db.ForeignKey("product.id"), nullable=False, index=True)
    product = db.relationship("Product", back_populates="order_items")
    
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='check_unit_price_positive'),
    )

    def __repr__(self) -> str:
        return f"<OrderItem {self.id} ({self.quantity}x {self.product_id}) - CustomerOrder {self.order_id}>"
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal dynamically"""
        return Decimal(self.unit_price) * self.quantity
    
    def to_dict(self) -> dict:
        """Serialize order item to dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Deleted Product",
            "quantity": self.quantity,
            "unit_price": str(self.unit_price),
            "subtotal": str(self.subtotal),
            "meta_info": self.meta_info,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Add event listener to update order total when items change
@event.listens_for(OrderItem, 'after_insert')
@event.listens_for(OrderItem, 'after_update')
@event.listens_for(OrderItem, 'after_delete')
def update_order_total(mapper, connection, target):
    """Automatically update customer order total when items change"""
    customer_order = target.customer_order
    customer_order.recalculate_total()
    
    db.session.add(customer_order)
    db.session.commit()