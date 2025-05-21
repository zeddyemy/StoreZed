"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
Package: StoreZed
"""

import uuid
from slugify import slugify
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user
from sqlalchemy.exc import ( InvalidRequestError, IntegrityError, DataError, DatabaseError )
from werkzeug.security import generate_password_hash

from .. import web_admin_bp
from ....extensions import db
from ....utils.helpers.basics import redirect_url
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.decorators import web_admin_login_required
from ....utils.helpers.products import fetch_all_products, fetch_product, save_product

from ....utils.forms.web_admin.products import AddProductForm, generate_category_field

@web_admin_bp.route("/products", methods=['GET'], strict_slashes=False)
@web_admin_login_required()
def products():
    page_num = request.args.get("page", 1, type=int)
    search_term = request.args.get("search", "").strip()
    
    current_user_roles = current_user.role_names
    current_user_id = current_user.id
    
    if 'trader' in current_user_roles:
        pagination = fetch_all_products(user_id=current_user_id, page_num=page_num, search_term=search_term)
    else:
        pagination = fetch_all_products(page_num=page_num, search_term=search_term)
        
    console_log('pagination', pagination.items)
    
    # Extract paginated products and pagination info
    all_products = pagination.items
    total_pages = pagination.pages
    
    return render_template('web_admin/pages/products/products.html', all_products=all_products, pagination=pagination, total_pages=total_pages, search_term=search_term)

@web_admin_bp.route("/products/new", methods=['GET', 'POST'], strict_slashes=False)
@web_admin_login_required()
def add_new_product():
    """Render form for adding a new product and handle form submission."""
    form = AddProductForm()
    
    pid = request.args.get('pid', uuid.uuid4())
    
    # generate html fields
    category_field = generate_category_field(format='checkbox')
    parent_cat_field = generate_category_field(format='select')
    
    if pid:
        existing_product = fetch_product(pid)
        if existing_product:
            form = AddProductForm(obj=existing_product) # Pre-populate the form with the draft data
            return redirect(url_for('web_admin.edit_product', slug=existing_product.slug))
    
    if request.method == 'POST':
        if form.validate_on_submit():
            console_log('form', request.form)
            try:
                form_data = request.form
                product = save_product(form_data)
                slug = product.slug
                
                flash('Your New Product {} was successfully published!'.format(request.form['name']), 'success')
                return redirect(url_for('web_admin.edit_product', slug=slug))
            except ValueError as e:
                db.session.rollback()
                log_exception('Value error occurred adding new product', e)
                flash(f"An unexpected error occurred!", "danger")
            except Exception as e:
                db.session.rollback()
                log_exception('An exception occurred adding new product', e)
                flash('An unexpected error occurred. Please try again later.', 'danger')
        else:
            console_log('form.errors', form.errors)
            flash("Product was not published successfully. Please try again", 'danger')

    
    return render_template('web_admin/pages/products/new_products.html', form=form, product=None, pid=pid, category_field=category_field, parent_cat_field=parent_cat_field)


@web_admin_bp.route("/products/edit/<slug>", methods=['GET', 'POST'], strict_slashes=False)
@web_admin_login_required()
def edit_product(slug):
    
    product = fetch_product(slug)
    if not product:
        flash('No such Product Exist', 'error')
        return redirect(url_for('web_admin.products'))
    
    product.tags
    form: AddProductForm = AddProductForm(obj=product)
    
    # generate html fields
    category_field = generate_category_field(format='checkbox')
    parent_cat_field = generate_category_field(format='select')
    
    if request.method == 'POST':
        if form.validate_on_submit():
            console_log('form', request.form)
            try:
                form_data = request.form
                product = save_product(form_data)
                name = form_data['name']
                product = db.session.merge(product)
                
                flash(f'Your Product {name} was successfully updated!', 'success')
                return redirect(url_for('web_admin.edit_product', slug=product.slug))
            except ValueError as e:
                db.session.rollback()
                log_exception('Value error occurred updating product', e)
                flash(f"An unexpected error occurred!", "danger")
            except Exception as e:
                db.session.rollback()
                log_exception('An exception occurred updating product', e)
                flash('An unexpected error occurred. Please try again later.', 'danger')
        else:
            console_log('form.errors', form.errors)
            flash("Product was not updated successfully. Please try again", 'danger')
    
    return render_template('web_admin/pages/products/edit_product.html', form=form, product=product, pid=product.uuid, category_field=category_field, parent_cat_field=parent_cat_field)

@web_admin_bp.route("/products/delete/<slug>", methods=['GET', 'POST'], strict_slashes=False)
@web_admin_login_required()
def delete_product(slug):
    """Delete a product."""
    try:
        product = fetch_product(slug)
        if not product:
            flash('Product does not exist', 'error')
            return redirect(url_for('web_admin.products'))
        
        # Delete the product itself
        db.session.delete(product)
        db.session.commit()

        flash(f'Product "{product.name}" was successfully deleted!', 'success')
        return redirect(url_for('web_admin.products'))  # Redirect to the products list page
    except Exception as e:
        db.session.rollback()
        log_exception('Error deleting products', e)
        flash('An error occurred while deleting the products. Please try again later.', 'error')
        return redirect(url_for('web_admin.products'))
