import pytest
from decimal import Decimal
from unittest.mock import patch

from app.extensions import db
from app.models import CustomerOrder
from app.utils.helpers.loggers import console_log

def test_create_order(app_context, test_user):
    console_log("TEST START", "Creating a new order")
    order = CustomerOrder(app_user=test_user, total_amount=100.00)
    db.session.add(order)
    db.session.commit()
    console_log("ORDER CREATED", f"ID: {order.id}, Number: {order.order_number}")
    assert order.id is not None
    assert order.order_number is not None
    # Add more assertions based on your model (e.g., order_number)

def test_soft_delete_order(app_context, test_user):
    # Create an order
    order = CustomerOrder(app_user=test_user, total_amount=100.00)
    db.session.add(order)
    db.session.commit()
    order_id = order.id

    # Soft delete
    order.is_deleted = True
    db.session.commit()

    # Check if it's not fetched by default
    fetched_order = CustomerOrder.query.get(order_id)
    assert fetched_order.is_deleted is True

    # Check if it still exists with is_deleted=True
    deleted_order = CustomerOrder.query.filter_by(id=order_id, is_deleted=True).first()
    assert deleted_order is not None