import sys
import uuid as uuid
from sqlalchemy.orm import joinedload
from slugify import slugify
from flask import render_template, request, flash, redirect, abort, url_for, jsonify, make_response
from flask_login import login_required, current_user

from .. import web_admin_bp
from ....extensions import db
from ....models import CustomerOrder, OrderItem, Product, AppUser
from ....enums import OrderStatus
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.helpers.customer_orders import fetch_customer_orders
from ....utils.decorators import session_roles_required, web_admin_login_required


@web_admin_bp.route("/orders", methods=['GET'], strict_slashes=False)
@web_admin_login_required()
def order_list():
    page_num = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()
    search_term = request.args.get('search', '').strip()
    
    
    # Paginate the query and Extract paginated orders and pagination info
    pagination = fetch_customer_orders(page_num=page_num, status_filter=status_filter, search_term=search_term)
    all_orders = pagination.items
    total_pages = pagination.pages
    
    # Get unique statuses for filter dropdown
    statuses = db.session.query(CustomerOrder.status).distinct().all()
    statuses = [status[0] for status in statuses]
    
    return render_template(
        'web_admin/pages/orders/order_list.html',
        all_orders=all_orders,
        pagination=pagination,
        total_pages=total_pages,
        statuses=statuses,
        selected_status=status_filter,
        search_term=search_term,
    )
    

@web_admin_bp.route('/orders/update/<int:order_id>', methods=['POST'], strict_slashes=False)
@web_admin_login_required()
def update_order(order_id):
    order: CustomerOrder = CustomerOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    try:
        if new_status and new_status != order.status:
            order.update(status=new_status)
            flash(f'Order #{order.order_number} updated to {new_status}.', 'success')
        else:
            flash('No changes made to order status.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the order.', 'danger')
        log_exception("---An unexpected error occurred updating order---", e)
    
    return redirect(url_for('web_admin.order_list'))