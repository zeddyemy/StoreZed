"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: GNU, see LICENSE for more details.
"""
from flask import flash
from flask_wtf import FlaskForm
from .auth import SignUpForm, LoginForm
from .web_admin.tags import TagForm
from .web_admin.users import AdminAddUserForm
from .web_admin.products import AddProductForm
from .web_admin.categories import CategoryForm
from .web_admin.settings import GeneralSettingsForm
from .web_admin.payment_methods import BacsPaymentForm, CodPaymentForm, CheckPaymentForm, GatewayPaymentForm


def handle_form_errors(form: FlaskForm):
    """
    Flash form errors as user-friendly messages.
    
    - Handle all form validation errors consistently
    """
    if 'csrf_token' in form.errors:
        flash("Session expired. Please refresh the page.", "danger")
    else:
        for field_name, errors in form.errors.items():
            for error in errors:
                field = getattr(form, field_name)
                flash(f"{field.label.text}: {error}", 'danger')