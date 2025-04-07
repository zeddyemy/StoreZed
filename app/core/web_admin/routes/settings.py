import uuid as uuid
from slugify import slugify
from flask import render_template, request, flash, redirect, abort, url_for, make_response
from flask_login import login_required, current_user
from sqlalchemy.exc import ( DataError, DatabaseError, OperationalError )

from .. import web_admin_bp
from ....extensions import db
from ....enums.payments import PaymentMethods
from ....enums.settings import GeneralSettingsKeys, PaymentMethodSettingKeys
from ....utils.forms.web_admin.settings import GeneralSettingsForm
from ....utils.forms.web_admin.payment_methods import get_payment_method_forms
from ....utils.helpers.basics import redirect_url, get_or_404
from ....utils.helpers.loggers import console_log, log_exception
from ....utils.helpers.settings import save_general_setting, get_all_general_settings, get_payment_method_settings, get_default_payment_method_settings, save_payment_method_setting
from ....utils.decorators import session_roles_required, web_admin_login_required
from ....utils.constants.payments import PAYMENT_METHOD_OVERVIEW



@web_admin_bp.route("/settings/general", methods=['GET', 'POST'], strict_slashes=False)
@web_admin_login_required()
def general_settings():
    page_name = "general settings"
    
    # Fetch all settings in a single query
    settings = get_all_general_settings()
    console_log("SETTINGS", settings)
    
    form: GeneralSettingsForm = GeneralSettingsForm(
        # Pre-fill form with existing settings
        site_title=settings.get(str(GeneralSettingsKeys.SITE_TITLE), ""),
        tagline=settings.get(str(GeneralSettingsKeys.TAGLINE), ""),
        platform_url=settings.get(str(GeneralSettingsKeys.PLATFORM_URL), ""),
        site_url=settings.get(str(GeneralSettingsKeys.SITE_URL), ""),
        admin_email=settings.get(str(GeneralSettingsKeys.ADMIN_EMAIL), ""),
        timezone=settings.get(str(GeneralSettingsKeys.TIMEZONE), ""),
        week_starts_on=settings.get(str(GeneralSettingsKeys.WEEK_STARTS_ON)),
        
        currency=settings.get(str(GeneralSettingsKeys.CURRENCY), ""),
        currency_position=settings.get(str(GeneralSettingsKeys.CURRENCY_POSITION), ""),
        thousand_separator=settings.get(str(GeneralSettingsKeys.THOUSAND_SEPARATOR), ""),
        decimal_separator=settings.get(str(GeneralSettingsKeys.DECIMAL_SEPARATOR), ""),
        number_of_decimals=settings.get(str(GeneralSettingsKeys.NUMBER_OF_DECIMALS), ""),
    )
    
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            form_data = form.data # get form data
            
            for key in form_data:
                if key != "csrf_token" and key != "submit":
                    save_general_setting(key, form_data.get(key))
            
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('web_admin.general_settings'))
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred while saving general settings', e)
            flash(f"Database error occurred. Please try again.", "danger")
        except Exception as e:
            db.session.rollback()
            log_exception('An exception occurred while saving general settings', e)
            flash('An unexpected error occurred. Please try again later.', 'danger')
    elif request.method == 'POST':
        # Log validation errors
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                if field_name == "csrf_token":
                    flash("CSRF validation failed. Please refresh and try again.", "danger")
                else:
                    flash(f"Error in {field_name}: {err}", "danger")
                console_log(f"Validation error in {field_name}", err)
    
    return render_template('web_admin/pages/settings/general_settings.html', page_name=page_name, form=form)


@web_admin_bp.route("/settings", methods=['GET'], strict_slashes=False)
def settings():
    return redirect(url_for('web_admin.general_settings'))


@web_admin_bp.route("/settings/payments", methods=['GET', 'POST'], strict_slashes=False)
@web_admin_login_required()
def payment_settings():
    """
    Displays an overview of available payment methods.
    """
    page_name = "payment settings"
    
    # Add the current enabled status for each method
    payment_methods = []
    for overview in PAYMENT_METHOD_OVERVIEW:
        current_settings = get_payment_method_settings(overview["key"])
        
        payment_methods.append({
            **overview,
            "enabled": current_settings.get("enabled", "false").lower() == "true",
            "setup_url": overview["setup_url"](),  # Call lambda to generate URL
        })
    
    return render_template('web_admin/pages/settings/payment_settings.html', page_name=page_name, payment_methods=payment_methods)



@web_admin_bp.route("/settings/payments/methods/<method>", methods=["GET", "POST"], strict_slashes=False)
@web_admin_login_required()
def payment_setup(method):
    """
    Displays and saves settings for a specific payment method.
    """
    try:
        method_enum = PaymentMethods(method)  # Convert string to Enum
    except ValueError:
        flash("Invalid payment method.", "danger")
        return redirect(url_for("web_admin.payment_settings"))
    
    method_overview = {}
    for overview in PAYMENT_METHOD_OVERVIEW:
        if overview["key"] == method:
            method_overview = overview
    
    # Get form class dynamically
    payment_forms = get_payment_method_forms()
    FormClass = payment_forms.get(method_enum)
    if not FormClass:
        flash("Unsupported payment method.", "danger")
        return redirect(url_for("web_admin.payment_settings"))
    
    
    # Get existing settings or set defaults
    current_settings = get_payment_method_settings(method_enum)
    
    # Pass existing settings as keyword arguments
    form = FormClass(**current_settings)
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            form_data = form.data # get form data
            
            for key in form_data:
                if key != "csrf_token":
                    save_payment_method_setting(method_enum, key, form_data.get(key))
            
            flash("Payment settings updated successfully!", "success")
            return redirect(url_for("web_admin.payment_settings"))
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred while saving payment settings', e)
            flash(f"Database error occurred. Please try again.", "danger")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while saving settings.", "danger")
    elif request.method == 'POST':
        # Log validation errors
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                if field_name == "csrf_token":
                    flash("CSRF validation failed. Please refresh and try again.", "danger")
                else:
                    flash(f"Error in {field_name}: {err}", "danger")
                console_log(f"Validation error in {field_name}", err)
    

    return render_template("web_admin/pages/settings/payment_setup.html", method=method, settings=current_settings, method_overview=method_overview, form=form)


