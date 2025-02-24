"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

import sys
from typing import Optional
from flask import request, jsonify, current_app
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Query
from flask_sqlalchemy.pagination import Pagination
from flask_login import current_user

from ...extensions import db
from ...models.category import Category
from ...models.product import Product, productVariations, product_category, product_tag

from .media import save_media
from .basics import generate_slug
from .loggers import log_exception, console_log
from .product_tags import save_tags


def fetch_all_products(
        user_id: Optional[int] = None,
        cat_id: Optional[int] = None,
        page_num: Optional[int] = None,
        search_term: Optional[str] = None,
        paginate: bool = True,
    ) -> Pagination | list[Product]:
    """
    Get products from the database with optional filtering and pagination.
    
    Returns either a pagination object or list of Product instances.
    Eager loads categories and tags relationships.

    Args:
        user_id: Filter products by owner user ID
        cat_id: Filter products by category ID
        page_num: Page number for pagination (default from request if None)
        search_term: Filter term for product search
        paginate: Return pagination object when True

    Returns:
        Pagination object or list of Product instances
    """
    if not page_num:
        page_num = request.args.get("page", 1, type=int)
    
    if not search_term:
        search_term = request.args.get("search", "").strip()
    
    # Base query with eager loading
    query: Query = Product.query.options(
        db.selectinload(Product.categories),
        db.selectinload(Product.tags)
    )
    
    # Apply combined filters
    if user_id is not None and cat_id is not None:
        query = query.filter(
            Product.user_id == user_id,
            Product.category_id == cat_id
        )
    elif user_id is not None:
        query = query.filter_by(user_id=user_id)
    elif cat_id is not None:
        query = query.filter_by(category_id=cat_id)
    
    # Apply search filters
    query = Product.add_search_filters(query, search_term)
    
    # Apply consistent ordering
    query = query.order_by(Product.id.desc())
    
    # Execute query with/without pagination
    if paginate:
        pagination: Pagination = query.paginate(page=page_num, per_page=10, error_out=False)
        return pagination
    
    return query.all()


def fetch_product(identifier: int | str) -> Product:
    product = None
    try:
        # Check if product_id_key is an integer
        id = int(identifier)
        # Fetch the product by id
        product = Product.query.filter_by(id=id).first()
    except ValueError:
        # If not an integer, treat it as a string
        product = Product.query.filter_by(slug=identifier).first()

        if not product:
            product = Product.query.filter_by(uuid=str(identifier)).first()
        
    return product


def save_product(form_data: dict, pub_status: str ='published') -> Product:
    """
    Save a new product based on the form data.

    Args:
        form_data (ImmutableMultiDict): A dictionary containing the data submitted via the form.
        pub_status (str): The publication status of the product.

    Returns:
        Product: The newly saved product object.
    """
    try:
        # Extract data from form
        pid = form_data.get('uuid')
        name = form_data.get('name')
        description = form_data.get('description')
        selling_price = form_data.get('selling_price')
        actual_price = form_data.get('actual_price')
        colors = form_data.get('colors')
        category_ids = form_data.getlist('categories')
        tags = form_data.get('product_tags', '').split(',')
        product_img = request.files['product_img']
        user_id = current_user.id
        
        product = None
        if pid:
            product = fetch_product(pid)
        
        console_log("category_ids", category_ids)
        console_log("product_img", product_img)
        console_log("pid", pid)
        console_log("product", product)
        
        if not product_img:
            media_id = None
        elif product_img:
            try:
                media = save_media(product_img)
                media_id = media.id
            except Exception as e:
                log_exception(f"An error occurred saving media for Product", e)
                return None
        elif not product_img and product:
            media_id = product.media_id if product.media_id else None
        else:
            media_id = None
        
        if not category_ids:
            # User did not select any category, assign "uncategorized" category
            uncategorized_category = Category.query.filter_by(name='uncategorized').first()
            if not uncategorized_category:
                uncategorized_category = Category.create_category(name='uncategorized', slug=generate_slug('uncategorized', Category))
            selected_categories = [uncategorized_category]
        else:
            selected_categories = Category.query.filter(Category.id.in_(category_ids)).all()
        
        console_log("selected_categories", selected_categories)
        
        # Re-associate categories with the current session if necessary
        selected_categories = [db.session.merge(cat) for cat in selected_categories]
        
        console_log("selected_categories", selected_categories)
        
        if tags:
            tags = save_tags(tags, session=db.session)
        
        # Update the existing product or create a new one if it doesn't exist
        with current_app.app_context():
            if product:
                product.update(
                    name=name, description=description, selling_price=selling_price, actual_price=actual_price,
                    colors=colors, media_id=media_id, slug=generate_slug(name, Product, product),
                    pub_status=pub_status, tags=tags, categories=selected_categories
                )
                
                return product
            else:
                new_product = Product.create_product(
                    uuid=pid, name=name, slug=generate_slug(name, Product), user_id=user_id,
                    description=description, selling_price=selling_price, actual_price=actual_price,
                    colors=colors, media_id=media_id, pub_status=pub_status, tags=tags, categories=selected_categories
                )
                # Re-fetch the product to ensure it's attached to the session
                new_product = Product.query.get(new_product.id)  # Fetch product by ID
                return new_product
    except Exception as e:
        db.session.rollback()
        log_exception(f'An error occurred saving product', e)
        raise e

