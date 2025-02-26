import sys
import uuid as uuid
from slugify import slugify
from flask import render_template, request, flash, redirect, abort, url_for, jsonify, make_response
from flask_login import login_required, current_user

from .. import web_admin_bp
from ....extensions import db
from ....models import Category, Product, product_category
from ....utils.forms.web_admin.categories import CategoryForm
from ....utils.helpers.media import save_media
from ....utils.helpers.basics import redirect_url, get_or_404
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.helpers.category import fetch_all_categories, fetch_category, save_category
from ....utils.decorators import session_roles_required, web_admin_login_required



@web_admin_bp.route("/categories", methods=['GET'])
@web_admin_login_required()
def categories():
    page_num = request.args.get("page", 1, type=int)
    search_term = request.args.get("search", "").strip()
    page_name = "categories"
    
    current_user_roles = current_user.role_names
    current_user_id = current_user.id
    
    pagination = fetch_all_categories(page_num=page_num, paginate=True, parent_only=False, search_term=search_term)
    
    console_log('pagination', pagination.items)
    
    # Extract paginated categories and pagination info
    all_categories = pagination.items
    total_pages = pagination.pages
    
    return render_template('web_admin/pages/categories/categories.html', all_categories=all_categories, pagination=pagination, total_pages=total_pages, search_term=search_term, page_name=page_name)


@web_admin_bp.route("/categories/new", methods=['GET', 'POST'])
@web_admin_login_required()
def add_new_category():
    form: CategoryForm = CategoryForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                form_data = request.form # get form data
                new_category = save_category(form_data)
                
                
                
                flash('Your new category ' + new_category.name + ' was created successfully!', 'success')
                return redirect(url_for('web_admin.categories'))
            except ValueError as e:
                log_exception('Error updating category', e)
                flash(e, 'error')
            except Exception as e:
                log_exception('Error creating new category', e)
                flash('An error occurred. Your category ' + form_data['name'] + ' could not be Created.', 'error')
            
        else:
            console_log("Form Error", form.errors)
            flash("New category could not be created", 'error')

    
    return render_template('web_admin/pages/categories/new_category.html', form=form, category=None)


@web_admin_bp.route("/categories/edit/<slug>", methods=['GET', 'POST'])
@web_admin_login_required()
def edit_category(slug):
    
    category = fetch_category(slug)
    if not category:
        flash('No such category Exist', 'error')
        return redirect(url_for('web_admin.categories'))
    
    form: CategoryForm = CategoryForm(obj=category)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                form_data = request.form # get form data
                updated_category = save_category(form_data, slug)
                
                
                flash('Your category ' + updated_category.name + ' was updated successfully!', 'success')
                return redirect(url_for('web_admin.categories'))
            except ValueError as e:
                log_exception('Error updating category', e)
                flash(e, 'error')
            except Exception as e:
                log_exception('Error updating category', e)
                flash('An error occurred. Your category ' + form_data['name'] + ' could not be updated.', 'error')
            
        else:
            console_log("Form Error", form.errors)
            flash("Category could not be updated", 'error')

    
    return render_template('web_admin/pages/categories/edit_category.html', form=form, category=category)


@web_admin_bp.route("/categories/delete/<slug>", methods=['POST', 'GET'])
@web_admin_login_required()
def delete_category(slug):
    """Delete a category."""
    try:
        category = fetch_category(slug)
        if not category:
            flash('Category does not exist', 'error')
            return redirect(url_for('web_admin.categories'))
        
        # Check if there are products assigned to this category
        # Get all products that are assigned to this category
        products_in_category = db.session.query(Product).join(product_category).filter(product_category.c.category_id == category.id).all()
        
        # Get the uncategorized category (or create it if it doesn't exist)
        uncategorized_category = Category.query.filter_by(name='uncategorized').first()
        if not uncategorized_category:
            uncategorized_category = Category(name='uncategorized', slug='uncategorized')
            db.session.add(uncategorized_category)
            db.session.commit()
        
        
        # Reassign all products to the 'uncategorized' category
        for product in products_in_category:
            # Get the list of categories the product belongs to
            current_categories = [cat.id for cat in product.categories]
            
            # If the product is only in the category being deleted, reassign it
            if len(current_categories) == 1 and category.id in current_categories:
                product.categories.append(uncategorized_category)
                db.session.commit()
        
        # Check if the category has children and handle them (reassign)
        child_categories = category.children
        if child_categories:
            for child in child_categories:
                child.parent_id = None  # Reassign child categories to have no parent
                db.session.commit()

        # Delete the category itself
        db.session.delete(category)
        db.session.commit()

        flash(f'Category "{category.name}" was successfully deleted!', 'success')
        return redirect(url_for('web_admin.categories'))  # Redirect to the categories list page
    except Exception as e:
        db.session.rollback()
        log_exception('Error deleting category', e)
        flash('An error occurred while deleting the category. Please try again later.', 'error')
        return redirect(url_for('web_admin.categories'))
