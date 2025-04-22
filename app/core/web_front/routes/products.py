"""
Author: Emmanuel Olowu
Link: https://eshomonu.com
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
"""

from flask import render_template, request, flash, redirect, abort, url_for
from flask_login import login_required, current_user
from requests.exceptions import RequestException
from sqlalchemy.exc import SQLAlchemyError

from ....extensions import db
from ....models import Product, Category, Tag
from ....utils.helpers.products import fetch_product, fetch_all_products
from ....utils.helpers.category import fetch_category
from ....utils.decorators.auth import login_required
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.forms import handle_form_errors

from .. import web_front_bp

@web_front_bp.route("/store", methods=['GET', 'POST'])
def products():
    page_num = request.args.get("page", 1, type=int)
    search_term = request.args.get("search", "").strip()
    
    pagination = fetch_all_products(page_num=page_num, search_term=search_term)
    
    console_log('pagination', pagination.items)
    
    # Extract paginated products and pagination info
    all_products = pagination.items
    total_pages = pagination.pages
    
    return render_template('web_front/pages/products/products.html', all_products=all_products, pagination=pagination, total_pages=total_pages, search_term=search_term)