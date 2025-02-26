"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

import sys
from urllib.parse import urlparse
from slugify import slugify
from flask import render_template, request, Response, flash, redirect, url_for, abort
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, OperationalError )
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from .. import web_admin_bp
from ....extensions import db
from ....enums.auth import RoleNames
from ....models import AppUser, Profile, Address, Role, UserRole
from ....utils.helpers.user import get_app_user
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.helpers.basics import redirect_url
from ....utils.forms import SignUpForm, LoginForm


## Route to sign up user
@web_admin_bp.route("/signup", methods=['GET', 'POST'])
@web_admin_bp.route("/register", methods=['GET', 'POST'])
def sign_up():
    form: SignUpForm = SignUpForm()
    
    if current_user.is_authenticated:
        return redirect(redirect_url('web_admin.index'))
    
    if request.method == 'POST':
        if form.validate_on_submit():
            console_log('Form', request.form)
            try:
                username = form.username.data
                email = form.email.data
                firstname = form.firstname.data
                lastname = form.lastname.data
                slug = slugify(username)
                password = form.password.data
                hashed_pwd = generate_password_hash(password, "pbkdf2:sha256")
                
                
                new_user = AppUser(username=username, email=email, password_hash=hashed_pwd)
                new_user_profile = Profile(firstname=firstname, lastname=lastname, app_user=new_user)
                new_user_address = Address(app_user=new_user)
            
                # Determine the role to assign
                role: Role = Role.query.filter_by(name=RoleNames.JUNIOR_ADMIN).first()
                
                db.session.add_all([new_user, new_user_profile, new_user_address])
                db.session.commit()
                
                # Assign role using the UserRole class method
                UserRole.assign_role(new_user, role)
                
                # on successful db insert, flash success
                flash('Your account has been successfully created', 'success')
                return redirect(redirect_url('web_admin.login'))
            except InvalidRequestError:
                db.session.rollback()
                flash(f"Something went wrong!", "danger")
            except IntegrityError:
                db.session.rollback()
                flash(f"User already exists!.", "warning")
            except (DataError, DatabaseError) as e:
                db.session.rollback()
                log_exception('Database error occurred during registration', e)
                flash(f"Error interacting with the database.", "danger")
            except Exception as e:
                db.session.rollback()
                log_exception('Database error occurred during registration', e)
                flash(f"An unexpected error occurred.", "danger")
                abort(500)
            finally:
                db.session.close()
        else:
            all_fields = ['email', 'username', 'password', 'confirmPasswd']
            if any(field in form.errors for field in all_fields):
                pass
            else:
                for field_name, error_messages in form.errors.items():
                    for err in error_messages:
                        if field_name == "csrf_token":
                            the_err_msg = "Sorry, we could not create your account. Please Try Again."
                            flash(the_err_msg, 'error')
                            console_log(data=err)
                            break
                        
    return render_template('web_admin/pages/auth/register.html', form=form, page='auth')

## Route to Login
@web_admin_bp.route("/login", methods=['GET', 'POST'])
def login():
    form: LoginForm = LoginForm()
    
    if current_user.is_authenticated:
        return redirect(redirect_url('web_admin.index'))
    
    if request.method == 'POST':
        if form.validate_on_submit():
            console_log('Form', data=request.form)
            try:
                email_username = form.email_username.data
                pwd = form.pwd.data
                
                # get user from db with the email/username.
                user = get_app_user(email_username)
                
                # get next argument fro url
                next = request.args.get('next')
                if not next or urlparse(next).netloc != '':
                    next = url_for('web_admin.index')
                
                if not user:
                    flash("Email/Username is incorrect or doesn't exist", 'error')
                    return render_template('web_admin/auth/login.html', form=form, page='auth')
                
                if not user.verify_password(pwd):
                    flash("Password is incorrect", 'error')
                    return render_template('web_admin/auth/login.html', form=form, page='auth')
                
                login_user(user)
                flash("Welcome back " + user.username, 'success')
                return redirect(next)
            except (DataError, DatabaseError, OperationalError) as e:
                db.session.rollback()
                log_exception("Error connecting to the database", e)
                flash(f"Error interacting with the database.", "danger")
            except Exception as e:
                log_exception("An exception occurred trying to login", e)
                flash(f"An unexpected error occurred.", "danger")
            finally:
                db.session.close()
        
        else:
            console_log('form.errors', form.errors)
            flash("Something went Wrong. Please Try Again.", 'error')
    
    return render_template('web_admin/pages/auth/login.html', form=form, page='auth')

## Route to Logout
@web_admin_bp.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been Logged Out", 'success')
    return redirect(url_for('web_admin.login'))


