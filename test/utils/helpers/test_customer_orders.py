import pytest
from decimal import Decimal
from unittest.mock import patch

from app.extensions import db
from app.models import CustomerOrder
from app.utils.helpers.loggers import console_log

def test_order_number_generation(test_user, app_context):
    # Create first order
    order1 = CustomerOrder(app_user=test_user, total_amount=100.00)
    db.session.add(order1)
    db.session.commit()
    
    console_log("Info", f"First Generated Order Number is: {order1.order_number}")
    assert order1.order_number == 'ORD-0001'  # Adjust based on your logic

    # Create second order
    order2 = CustomerOrder(app_user=test_user, total_amount=200.00)
    db.session.add(order2)
    db.session.commit()
    console_log("Info", f"Second Generated Order Number is: {order2.order_number}")
    assert order2.order_number == 'ORD-0002'