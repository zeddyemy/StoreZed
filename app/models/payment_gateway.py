from enum import Enum

from ..extensions import db
from ..utils.date_time import DateTimeUtils
from ..utils.helpers.basics import generate_random_string
from ..utils.payments.rates import convert_amount
from ..enums.payments import PaymentGatewayName


class PaymentGateway(db.Model):
    __tablename__ = 'payment_gateway'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g., 'BitPay', 'Stripe'
    is_active = db.Column(db.Boolean, default=False)
    credentials = db.Column(db.JSON)  # Store credentials like API keys, secrets as JSON

    def __repr__(self):
        return f"<PaymentGateway {self.name}>"
