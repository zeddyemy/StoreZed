from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError, OperationalError

from .. import web_admin_bp
from ....extensions import db
from ....models.nav import NavigationBarItem
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.decorators import web_admin_login_required
from ....utils.forms.web_admin.settings import NavigationItemsForm

@web_admin_bp.route('/settings/navigation', methods=['GET'])
@web_admin_login_required()
def navigation_settings():
    """List all navigation items."""
    nav_items = NavigationBarItem.query.order_by(NavigationBarItem.order.asc()).all()
    return render_template('web_admin/pages/settings/nav/navigation.html', nav_items=nav_items)

@web_admin_bp.route('/settings/navigation/new', methods=['GET', 'POST'])
@web_admin_login_required()
def add_nav_item():
    """Add a new navigation item."""
    form = NavigationItemsForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            form_data = form.data # get form data
            
            name =  form_data.get("name")
            url = form_data.get('url')
            order = form_data.get('order', 0)
            parent_id = form_data.get('parent_id', None)
            is_active = form_data.get('is_active') == 'on'  # Checkbox returns 'on' or None
            
            if not name or not url:
                flash('Name and URL are required.', 'danger')
                return redirect(url_for('web_admin.add_nav_item'))
            
            NavigationBarItem.create(name=name, url=url, order=order, is_active=is_active, parent_id=parent_id)
            flash('Navigation item added successfully!', 'success')
            return redirect(url_for('web_admin.navigation_settings'))
        except IntegrityError:
            db.session.rollback()
            log_exception("Integrity Error: Nav Item already exists", e)
            flash('A navigation item with that name already exists.', 'danger')
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred while saving payment settings', e)
            flash(f"Database error occurred. Please try again.", "danger")
        except Exception as e:
            db.session.rollback()
            log_exception('Error adding navigation item', e)
            flash('An unexpected error occurred.', 'danger')
    elif request.method == 'POST':
        # Log validation errors
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                if field_name == "csrf_token":
                    flash("CSRF validation failed. Please refresh and try again.", "danger")
                else:
                    flash(f"Error in {field_name}: {err}", "danger")
                console_log(f"Validation error in {field_name}", err)
    
    return render_template('web_admin/pages/settings/nav/add_nav_item.html', form=form)

@web_admin_bp.route('/settings/navigation/edit/<int:nav_id>', methods=['GET', 'POST'])
@web_admin_login_required()
def edit_nav_item(nav_id):
    """Edit an existing navigation item."""
    nav_item: NavigationBarItem = NavigationBarItem.query.get(nav_id)
    
    if not nav_item:
        flash('Nav Item does not Exist', 'error')
        return redirect(url_for('web_admin.navigation_settings'))
    
    form = NavigationItemsForm(obj=nav_item)
    
    if request.method == 'POST':
        try:
            form_data = form.data # get form data
            
            name = form_data.get('name')
            url = form_data.get('url')
            order = form_data.get('order', nav_item.order)
            is_active = form_data.get('is_active') == True
            parent_id = form_data.get('parent_id', None)
            parent_id = None if parent_id == "" else parent_id
            
            console_log("is active", form_data.get('is_active'))
            
            if not name or not url:
                flash('Name and URL are required.', 'danger')
                return redirect(url_for('web_admin.edit_nav_item', nav_id=nav_id))
            
            nav_item.update(name=name, url=url, order=order, is_active=is_active, parent_id=parent_id)
            flash('Navigation item updated successfully!', 'success')
            return redirect(url_for('web_admin.navigation_settings'))
        except IntegrityError:
            db.session.rollback()
            flash('A navigation item with that name already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            log_exception('Error updating navigation item', e)
            flash('An unexpected error occurred.', 'danger')
    
    return render_template('web_admin/pages/settings/nav/edit_nav_item.html', nav_item=nav_item, form=form)

@web_admin_bp.route('/settings/navigation/delete/<int:nav_id>', methods=['POST'])
@web_admin_login_required()
def delete_nav_item(nav_id):
    """Delete a navigation item."""
    nav_item = NavigationBarItem.query.get_or_404(nav_id)
    try:
        db.session.delete(nav_item)
        db.session.commit()
        flash('Navigation item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        log_exception('Error deleting navigation item', e)
        flash('An unexpected error occurred.', 'danger')
    return redirect(url_for('web_admin.navigation_settings'))