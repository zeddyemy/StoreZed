"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""

import sys
from typing import Optional
from flask import request, jsonify, current_app
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Query, joinedload
from flask_sqlalchemy.pagination import Pagination
from flask_login import current_user

from ...extensions import db
from ...models import CustomerOrder, OrderItem, Product, AppUser

from .loggers import log_exception, console_log

def fetch_customer_orders(
        page_num: Optional[int] = None,
        status_filter: Optional[str] = None,
        search_term: Optional[str] = None,
        is_deleted: Optional[bool] = False,
        paginate: bool = True,
    ) -> Pagination | list[CustomerOrder]:
    
    
    if not page_num:
        page_num = request.args.get("page", 1, type=int)
    
    if not search_term:
        search_term = request.args.get("search", "").strip()
    
    if not status_filter:
        status_filter = request.args.get('status', '').strip()
    
    # Base query
    query: Query = CustomerOrder.query.options(joinedload(CustomerOrder.app_user)).filter_by(is_deleted=is_deleted)
    
    # Apply status filter
    if status_filter:
        query = query.filter(CustomerOrder.status == status_filter)
    
    # Apply search filters (by order number or username)
    if search_term:
        query = CustomerOrder.add_search_filters(query, search_term)
    
    # Apply consistent ordering
    query = query.order_by(CustomerOrder.created_at.desc())
    
    # Execute query with/without pagination
    if paginate:
        pagination: Pagination = query.paginate(page=page_num, per_page=10, error_out=False)
        return pagination
    
    return query.all()


def fetch_customer_order(identifier: int | str) -> Product:
    """fetch a single customer order using an identifier like ID, or Order Number"""
    customer_order = None
    try:
        # Check if identifier is an integer
        id = int(identifier)
        # Fetch the customer order by id
        customer_order = CustomerOrder.query.filter_by(id=id).first()
    except ValueError:
        # If not an integer, treat it as a string
        customer_order = CustomerOrder.query.filter_by(order_number=identifier).first()
        
    return customer_order


def soft_delete_customer_order(order_id):
    customer_order: CustomerOrder = CustomerOrder.query.filter_by(id=order_id, is_deleted=False).first()
    if customer_order:
        customer_order.is_deleted = True
        db.session.commit()

def restore_order(order_id):
    customer_order: CustomerOrder = CustomerOrder.query.filter_by(id=order_id).first()  # No is_deleted filter
    if customer_order and customer_order.is_deleted:
        customer_order.is_deleted = False
        db.session.commit()

def generate_customer_order_number():
    last_order: CustomerOrder = CustomerOrder.query.order_by(CustomerOrder.id.desc()).first()
    if last_order:
        num = int(last_order.order_number.split('-')[-1]) + 1
        return f'ORD-{num:04d}'
    return 'ORD-0001'