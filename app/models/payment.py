from enum import Enum

from ..extensions import db
from ..utils.helpers.basics import generate_random_string
from ..utils.date_time import DateTimeUtils
from ..utils.payments.rates import convert_amount
from ..enums.payments import PaymentStatus, TransactionType

class Payment(db.Model):
    """
    Model to represent a payment request made by a user in Trendit³.
    This model captures details about a payment request before it is processed.
    """
    __tablename__ = "payment"

    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False) # Unique identifier for the payments
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    narration = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(), nullable=False)  # 'wallet' or 'payment gateway(flutterwave)'
    status = db.Column(db.String(20), nullable=False, default="pending")  # Status of the payment request
    meta_info = db.Column(db.JSON, default=dict)  # Store payment type and related data
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)

    # relationships
    user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    app_user = db.relationship('AppUser', back_populates='payments')
    
    order_id = db.Column(db.Integer(), db.ForeignKey('order.id'), nullable=True)
    order = db.relationship('Order', back_populates='payment')
    
    subscription_id = db.Column(db.Integer(), db.ForeignKey('subscription.id'), nullable=True)
    subscription = db.relationship('Subscription', back_populates='payment')
    
    def __repr__(self):
        return f'<ID: {self.id}, Amount: {self.amount}, Payment Method: {self.payment_method}>'
    
    @property
    def currency_code(self):
        return self.app_user.wallet.currency_code
    
    @classmethod
    def create_payment_record(cls, key, amount, payment_method, status, app_user, commit=True, **kwargs):
        payment_record = cls(key=key, amount=amount, payment_method=payment_method, status=str(status), app_user=app_user)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(payment_record, key, value)
        
        db.session.add(payment_record)
        
        if commit:
            db.session.commit()
        
        return payment_record
    
    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        if commit:
            db.session.commit()
    
    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    def to_dict(self, user=False):
        user_info = {'user': self.app_user.to_dict()} if user else {'user_id': self.user_id} # optionally include user info in dict
        return {
            'id': self.id,
            'key': self.key,
            'amount': convert_amount(self.amount, self.currency_code),
            'narration': self.narration,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at,
            **user_info,
        }


class Transaction(db.Model):
    """
    Model to represent a financial transaction associated with a payment on the platform.
    This model captures details about the financial aspect of a payment or withdrawal.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False) # Unique identifier for the financial transaction
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(), nullable=False) # 'credit', 'debit', 'payment' or 'withdraw'
    narration = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(80), nullable=False) # Status of the financial transaction
    meta_info = db.Column(db.JSON, default=dict)  # Store addition info or related data
    
    created_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=DateTimeUtils.aware_utcnow, onupdate=DateTimeUtils.aware_utcnow)
    
    # Relationship with the user model
    user_id = db.Column(db.Integer(), db.ForeignKey('app_user.id'), nullable=False)
    app_user = db.relationship('AppUser', backref=db.backref('transactions', lazy='dynamic'))
    
    @property
    def currency_code(self):
        return self.app_user.wallet.currency_code
    
    def __repr__(self):
        return f'<ID: {self.id}, Transaction Reference: {self.key}, Transaction Type: {self.transaction_type}, Status: {self.status}>'
    
    
    @classmethod
    def create_transaction(cls, key, amount, transaction_type, narration, status, app_user, commit=True, **kwargs):
        transaction = cls(key=key, amount=amount, transaction_type=str(transaction_type), narration=narration, status=str(status), app_user=app_user)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(transaction, key, value)
        
        
        db.session.add(transaction)
        
        if commit:
            db.session.commit()
        
        return transaction
    
    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        if commit:
            db.session.commit()
    
    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
    
    def to_dict(self, user=False):
        user_info = {'user': self.app_user.to_dict(),} if user else {'user_id': self.user_id} # optionally include user info in dict
        return {
            'id': self.id,
            'key': self.key,
            'amount': convert_amount(self.amount, self.currency_code),
            'transaction_type': str(self.transaction_type.value),
            'narration': self.narration,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            **user_info,
        }

