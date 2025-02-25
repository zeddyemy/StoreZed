"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
"""
from typing import Any, Optional
from flask import request
from sqlalchemy import func

from ...extensions import db
from ...models import AppUser, Product, Category, Tag, CustomerOrder, Wallet, Payment
from ...enums import PaymentStatus, PaymentMethods
from ..date_time import timedelta, date
from .money import quantize_amount, format_monetary_value
from .loggers import console_log, log_exception

def get_stats_for_admin(period: Optional[str] = None) -> dict[str, Any]:
    
    if not period:
        period = request.args.get('period', 'year')  # Default to 'year'
    
    today = date.today()
    
    if period == 'day':
        start_date = today
        end_date = today + timedelta(days=1)
    elif period == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = today
    elif period == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1)
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = start_date.replace(year=start_date.year + 1)
    else:
        raise ValueError("Invalid period specified")
    
    # Fetch counts for products, categories, tags, and users
    total_products = Product.query.count()
    total_categories = Category.query.count()
    total_tags = Tag.query.count()
    total_users = AppUser.query.count()
    
    # Fetch the total wallet balance (sum of all user wallet balances)
    total_wallet_balance = db.session.query(db.func.sum(Wallet._balance)).scalar() or 0.00
    
    # Fetch the last 5 orders, ordered by creation date
    recent_orders = CustomerOrder.query.order_by(CustomerOrder.created_at.desc()).limit(5).all()
    
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    
    # Calculate total successful paid amounts by every user, excluding "wallet" payments
    total_payments = db.session.query(func.sum(Payment.amount)).filter(
        Payment.created_at >= start_date,
        Payment.created_at < end_date,
        Payment.payment_method != str(PaymentMethods.WALLET),
        Payment.status == str(PaymentStatus.COMPLETED)
    ).scalar() or 0.00
    
    stats = {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_tags": total_tags,
        "total_users": total_users,
        "total_wallet_balance": quantize_amount(total_wallet_balance),
        "total_payments": quantize_amount(total_payments),
        "recent_orders": recent_orders,
        "recent_products": recent_products,
    }
    
    return stats