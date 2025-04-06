from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError, OperationalError

from .. import web_admin_bp
from ....extensions import db
from ....models.nav_menu import NavigationMenu, NavMenuItem
from ....utils.helpers.nav_menu import get_nav_menu
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.helpers.category import fetch_all_categories, get_cached_categories
from ....utils.helpers.product_tags import fetch_all_tags
from ....utils.helpers.pages import get_predefined_pages
from ....utils.decorators import web_admin_login_required
from ....utils.forms.web_admin.settings import MenuItemsForm

@web_admin_bp.route('/appearance/nav-menus', methods=['GET'])
@web_admin_login_required()
def nav_menus():
    """get all navigation menus."""
    nav_menus = NavigationMenu.query.order_by(NavigationMenu.created_at.asc()).all()
    main_menu = NavigationMenu.query.filter_by(slug="main-menu").first()
    categories = fetch_all_categories()
    tags = fetch_all_tags()
    
    console_log("nav_menus", nav_menus)
    
    return render_template('web_admin/pages/appearance/nav_menu/nav_menus.html', nav_menus=nav_menus, main_menu=main_menu, categories=categories, tags=tags)


@web_admin_bp.route('/appearance/nav-menus/<identifier>', methods=['GET'])
@web_admin_login_required()
def manage_nav_menu(identifier):
    """Manage and edit a navigation menu along with its menu items."""
    try:
        # Retrieve the navigation menu based on the provided identifier.
        nav_menu = get_nav_menu(identifier)
        if not nav_menu:
            flash(f'Navigation menu not found.', 'warning')
            return redirect(url_for('web_admin.nav_menus'))

        # Check for action query parameter for delete operation.
        action = request.args.get("action", "").lower()
        if action == "delete":
            nav_menu.delete()
            flash(f'Navigation menu "{nav_menu.name}" deleted successfully.', 'success')
            console_log(f"Deleted navigation menu: {nav_menu.name}")
            return redirect(url_for('web_admin.nav_menus'))

        # Retrieve supporting data.
        categories = fetch_all_categories()
        tags = fetch_all_tags()
        pages = get_predefined_pages()
    except Exception as e:
        db.session.rollback()
        error_message = f"Error processing navigation menu '{identifier}': {str(e)}"
        log_exception(error_message, e)
        flash("An error occurred while processing the navigation menu. Please try again later.", 'danger')
        return redirect(url_for('web_admin.nav_menus'))

    return render_template('web_admin/pages/appearance/nav_menu/manage_nav_menu.html',
                            nav_menu=nav_menu, categories=categories, tags=tags, pages=pages)


@web_admin_bp.route('/appearance/nav-menus/<identifier>', methods=['DELETE'])
@web_admin_login_required()
def delete_nav_menu(identifier):
    try:
        # Retrieve the navigation menu based on the provided identifier.
        nav_menu = get_nav_menu(identifier)
        if not nav_menu:
            flash(f'Navigation menu not found.', 'warning')
            return redirect(url_for('web_admin.nav_menus'))

        nav_menu.delete()
        flash(f'Navigation menu "{nav_menu.name}" deleted successfully.', 'success')
        console_log(f"Deleted navigation menu: {nav_menu.name}")
        return redirect(url_for('web_admin.nav_menus'))
    except Exception as e:
        db.session.rollback()
        error_message = f"Error deleting navigation menu '{identifier}': {str(e)}"
        log_exception(error_message, e)
        flash("An error occurred while deleting the navigation menu. Please try again later.", 'danger')
        return redirect(url_for('web_admin.nav_menus'))


