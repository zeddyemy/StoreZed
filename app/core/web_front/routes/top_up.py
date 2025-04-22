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
from ....enums import PaymentMethods, PaymentMethodSettingKeys, PaymentType
from ....utils.decorators.auth import login_required
from ....utils.helpers.settings import get_active_payment_gateway, get_payment_method_setting
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.forms import handle_form_errors
from ....utils.forms.web_front.payments import TopUpForm
from ....utils.payments.payment_manager import PaymentManager

from .. import web_front_bp

@web_front_bp.route("/top-up", methods=['GET', 'POST'])
@login_required
def top_up():
    """
    Allows users to top up their wallet using a selected payment gateway.
    """
    
    payment_manager:PaymentManager = PaymentManager()
    
    active_payment_gateway = get_active_payment_gateway()
    if not active_payment_gateway:
        flash("Payment gateway is not set up. Please contact admin.", "danger")
        return redirect(url_for("web_front.index"))
    
    form = TopUpForm() # A form to allow users to input the top-up amount
    
    # Pre-fill or display gateway information
    gateway = get_payment_method_setting(PaymentMethods.GATEWAY, PaymentMethodSettingKeys.PROVIDER)
    
    if form.validate_on_submit():
        try:
            form_data = form.data # get form data
            amount = form_data.get("amount", 0)
            processor = payment_manager.get_payment_processor() # Get the payment processor for the selected gateway
            
            if not processor:
                flash("We are sorry. But a payment Gateway has not been setup yet. Please contact admin.", "danger")
                return redirect(url_for("web_front.top_up"))
            
            # Get user's wallet currency
            currency = current_user.wallet.currency_code
            
            # Validate currency support
            if not processor.supports_currency(currency):
                supported = ", ".join(sorted(processor.supported_currencies))
                flash(f"Selected payment method only supports: {supported}", "danger")
                return redirect(url_for("web_front.top_up"))
            
            # Initialize payment
            response = payment_manager.initialize_gateway_payment(
                amount=amount,
                currency="NGN",
                user=current_user,
                payment_type=PaymentType.WALLET_TOP_UP,
                narration="Wallet top-up"
            )
            
            console_log( "response", response )
            
            # On successful initialization
            if response["status"] == "success":
                authorization_url = response["authorization_url"]
                url = authorization_url if authorization_url else url_for("web_front.index")
                return redirect(url)
            else:
                flash(f"Payment failed: {response.get('message', 'Unknown error')}", "danger")
                return redirect(url_for("web_front.top_up"))
            
        except RequestException as e:
            # Handle API specific errors
            db.session.rollback()
            flash(f"Error communicating with the payment provider: {str(e)}", "danger")
            log_exception("Payment API error", e)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Database error", "danger")
            log_exception("Database error", e)
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred", "danger")
            log_exception("Unexpected error", e)
        
        return redirect(url_for("web_front.top_up"))
    elif request.method == 'POST':
        handle_form_errors(form)
        return redirect(url_for("web_front.top_up"))
    
    return render_template('web_front/pages/top_up/top_up.html', gateway=gateway, form=form)

