"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from slugify import slugify
from flask import request, render_template, flash, redirect, url_for
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, OperationalError )
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash

from . import web_admin_bp
from ....extensions import db
from ....enums.auth import RoleNames
from ....models import AppUser, Profile, Address, Role, UserRole
from ....utils.helpers.basics import redirect_url
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.helpers.user import get_current_user
from ....utils.decorators.auth import web_admin_login_required, session_roles_required
from ....utils.forms import AdminAddUserForm

@web_admin_bp.route("/users", methods=['GET'])
@session_roles_required("Super Admin", "Admin")
def users():
    try:
        pagination = []
        page_num = request.args.get("page", 1, type=int)
        search_term = request.args.get("search", "").strip()
        
        query = AppUser.query.options(joinedload(AppUser.roles).joinedload(UserRole.role), joinedload(AppUser.profile), joinedload(AppUser.address))
        
        # Apply search filters
        query = AppUser.add_search_filters(query, search_term)
        
        pagination = query.paginate(page=page_num, per_page=10, error_out=False)
        
        console_log('pagination', pagination.items)
    
        # Extract paginated users and pagination info
        all_users = pagination.items
        total_pages = pagination.pages
    except (DataError, DatabaseError, OperationalError) as e:
        db.session.rollback()
        log_exception("Error connecting to the database", e)
        flash(f"Error interacting with the database.", "danger")
    except Exception as e:
        log_exception("An exception occurred trying to login", e)
        flash(f"An unexpected error occurred.", "danger")
    finally:
        db.session.close()
    
    return render_template('web_admin/pages/users/users.html', all_users=all_users, pagination=pagination, total_pages=total_pages, search_term=search_term)


@web_admin_bp.route("/users/new", methods=['GET', 'POST'])
@session_roles_required("Super Admin", "Admin")
def add_new_user():
    form: AdminAddUserForm = AdminAddUserForm()
    
    
    if request.method == 'POST':
        if form.validate_on_submit():
            console_log('form', request.form)
            try:
                current_user = get_current_user()
                
                username = form.username.data
                email = form.email.data
                firstname = form.firstname.data
                lastname = form.lastname.data
                password = form.password.data
                role = form.role.data
                hashed_pwd = generate_password_hash(password, "pbkdf2:sha256")
                
                new_user = AppUser(username=username, email=email, password_hash=hashed_pwd)
                new_user_profile = Profile(firstname=firstname, lastname=lastname, app_user=new_user)
                new_user_address = Address(app_user=new_user)
                
                # Determine the role to assign
                # get role from db where the name is same as form role
                user_role = Role.query.filter(Role.name == RoleNames.get_member_by_value(role)).first()
                
                db.session.add_all([new_user, new_user_profile, new_user_address])
                db.session.commit() # Commit to generate the new_user.id
            
                # Assign role using the UserRole class method
                UserRole.assign_role(new_user, user_role, current_user)
                
                # on successful db insert, flash success
                flash("New users has been successfully added. Login details will be sent to user's Email", 'success')
                console_log('redirect', url_for('web_admin.users'))
                return redirect(url_for('web_admin.users'))
            except ValueError as e:
                db.session.rollback()
                log_exception('Value error occurred while adding user', e)
                flash(f"An unexpected error occurred!", "danger")
            except InvalidRequestError:
                db.session.rollback()
                flash(f"An unexpected error occurred!", "danger")
            except IntegrityError:
                db.session.rollback()
                flash(f"User already exists!.", "warning")
            except (DataError, DatabaseError) as e:
                db.session.rollback()
                log_exception('Database error occurred while adding user', e)
                flash(f"Error interacting with the database.", "danger")
            except Exception as e:
                db.session.rollback()
                flash('An unexpected error occurred. Please try again later.', 'danger')
                log_exception('An exception occurred while adding user', e)
        else:
            all_fields = ['email', 'username', 'password', 'role']
            if any(field in form.errors for field in all_fields):
                console_log('form.errors', form.errors)
                pass
            else:
                for field_name, error_messages in form.errors.items():
                    for err in error_messages:
                        if field_name == "csrf_token":
                            flash("Session expired. Please refresh the page.", "danger")
                            console_log("error", err)
                            break
    
    return render_template('web_admin/pages/users/new_user.html', form=form)


@web_admin_bp.route("/users/<user_id>/edit", methods=['GET', 'POST'])
@session_roles_required("Super Admin", "Admin")
def edit_user(user_id):
    form: AdminAddUserForm = AdminAddUserForm()
    
    current_user = get_current_user()
    user = AppUser.query.get(user_id)
    
    return render_template('web_admin/pages/users/edit_user.html', form=form, user=user)